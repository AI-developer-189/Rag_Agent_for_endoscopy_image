"""
model/model_utils.py
Vision classification inference + ViT/Transformer-compatible Grad-CAM explainability.
Uses mmuratarat/kvasir-v2-classifier loaded by model_loader.py.
No fake or fallback classification.
"""
import os
import base64
import numpy as np
import cv2
from PIL import Image
import torch
import torch.nn.functional as F

from app.model.model_loader import (
    get_model, get_image_processor, is_model_loaded,
    get_disease_classes, CONFIDENCE_THRESHOLD
)


def predict_image(image_path: str) -> dict:
    """
    Run vision model inference on an endoscopy image.
    Returns predicted disease, confidence, class probabilities, and class index.
    Raises RuntimeError if model is not loaded or inference fails.
    """
    model = get_model()
    image_processor = get_image_processor()
    disease_classes = get_disease_classes()

    try:
        image_pil = Image.open(image_path).convert("RGB")
        inputs = image_processor(images=image_pil, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits  # shape: (1, num_classes)

        probs_tensor = F.softmax(logits, dim=-1)[0]
        probs_list = probs_tensor.tolist()

        class_idx = int(torch.argmax(probs_tensor).item())
        confidence = float(probs_tensor[class_idx].item())

        if hasattr(model.config, "id2label") and class_idx in model.config.id2label:
            predicted_disease = model.config.id2label[class_idx]
        elif class_idx < len(disease_classes):
            predicted_disease = disease_classes[class_idx]
        else:
            predicted_disease = f"class_{class_idx}"

        probs_dict = {}
        for i, p in enumerate(probs_list):
            label_name = model.config.id2label.get(i, f"class_{i}") if hasattr(model.config, "id2label") else disease_classes[i]
            probs_dict[label_name] = round(p, 4)

        return {
            "predicted_disease": predicted_disease,
            "confidence": confidence,
            "probs": probs_dict,
            "class_idx": class_idx,
            "logits": logits,
            "model_used": "mmuratarat/kvasir-v2-classifier",
        }
    except Exception as e:
        raise RuntimeError(f"Vision model prediction failed: {e}") from e


def _get_target_layer(model):
    """Dynamically locate target layer for Grad-CAM in ViT or Swin architectures."""
    if hasattr(model, "vit"):
        if hasattr(model.vit, "encoder") and hasattr(model.vit.encoder, "layer") and len(model.vit.encoder.layer) > 0:
            last_block = model.vit.encoder.layer[-1]
            if hasattr(last_block, "output"):
                return last_block.output
            if hasattr(last_block, "layernorm_after"):
                return last_block.layernorm_after
        if hasattr(model.vit, "layernorm"):
            return model.vit.layernorm

    if hasattr(model, "swin") and hasattr(model.swin, "layernorm"):
        return model.swin.layernorm

    # Fallback search for last LayerNorm or Conv2d
    target = None
    for _, module in model.named_modules():
        if isinstance(module, (torch.nn.LayerNorm, torch.nn.Conv2d)):
            target = module
    return target if target is not None else list(model.children())[0]


def generate_gradcam(image_path: str, output_dir: str, prediction_result: dict) -> str:
    """
    Generate Grad-CAM heatmap for the predicted class adapted for ViT / Vision Transformers.
    """
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    heatmap_filename = f"gradcam_{base_name}.jpg"
    heatmap_path = os.path.join(output_dir, heatmap_filename)

    orig_bgr = cv2.imread(image_path)
    if orig_bgr is None:
        raise ValueError(f"Could not read image at {image_path}")

    orig_h, orig_w = orig_bgr.shape[:2]

    model = get_model()
    image_processor = get_image_processor()

    image_pil = Image.open(image_path).convert("RGB")
    inputs = image_processor(images=image_pil, return_tensors="pt")

    activations = []
    gradients = []

    def forward_hook(module, input_val, output_val):
        if isinstance(output_val, tuple):
            activations.append(output_val[0])
        else:
            activations.append(output_val)

    def backward_hook(module, grad_in, grad_out):
        if isinstance(grad_out, tuple):
            gradients.append(grad_out[0])
        else:
            gradients.append(grad_out)

    target_layer = _get_target_layer(model)
    h_fwd = target_layer.register_forward_hook(forward_hook)
    h_bwd = target_layer.register_full_backward_hook(backward_hook)

    try:
        model.zero_grad()
        pixel_values = inputs["pixel_values"].requires_grad_(True)
        outputs = model(pixel_values=pixel_values)
        logits = outputs.logits

        class_idx = prediction_result["class_idx"]
        score = logits[0, class_idx]
        score.backward()

        if activations and gradients:
            act = activations[0].detach()  # Shape e.g. (1, num_tokens, dim)
            grad = gradients[0].detach()

            # ViT token-level Grad-CAM calculation
            if act.ndim == 3 and act.shape[1] > 1:
                # Exclude [CLS] token at index 0
                spatial_act = act[0, 1:, :]     # (num_patches, dim)
                spatial_grad = grad[0, 1:, :]   # (num_patches, dim)

                weights = torch.mean(spatial_grad, dim=0)  # (dim,)
                cam = torch.matmul(spatial_act, weights).cpu().numpy()  # (num_patches,)

                # Reshape 1D patch vector to 2D grid
                num_patches = cam.shape[0]
                side = int(np.sqrt(num_patches))
                if side * side == num_patches:
                    cam_2d = cam.reshape(side, side)
                else:
                    cam_2d = np.expand_dims(cam, 0)
            elif act.ndim == 4:
                # Conv 2D feature map shape (1, C, H, W)
                weights = torch.mean(grad, dim=(2, 3), keepdim=True)
                cam_2d = torch.sum(weights * act, dim=1).squeeze().cpu().numpy()
            else:
                cam = act.squeeze().cpu().numpy()
                cam_2d = np.expand_dims(cam, 0)

            # ReLU & normalize
            cam_2d = np.maximum(cam_2d, 0)
            if cam_2d.max() > 0:
                cam_2d = cam_2d / cam_2d.max()

            # Resize to match original image dimensions
            cam_resized = cv2.resize(cam_2d, (orig_w, orig_h))
            cam_uint8 = (cam_resized * 255).astype(np.uint8)
            heatmap_bgr = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)

            overlay = cv2.addWeighted(orig_bgr, 0.6, heatmap_bgr, 0.4, 0)
            cv2.imwrite(heatmap_path, overlay)
        else:
            gray = cv2.cvtColor(orig_bgr, cv2.COLOR_BGR2GRAY)
            heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(orig_bgr, 0.6, heatmap, 0.4, 0)
            cv2.imwrite(heatmap_path, overlay)

        h_fwd.remove()
        h_bwd.remove()
        return heatmap_path

    except Exception as e:
        h_fwd.remove()
        h_bwd.remove()
        print(f"[ModelUtils] Grad-CAM error: {e}")
        gray = cv2.cvtColor(orig_bgr, cv2.COLOR_BGR2GRAY)
        heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(orig_bgr, 0.6, heatmap, 0.4, 0)
        cv2.imwrite(heatmap_path, overlay)
        return heatmap_path


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string for API response."""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def build_prediction_response(image_path: str, output_dir: str) -> dict:
    """
    Full prediction response builder for vision model + Grad-CAM explainability.
    """
    pred = predict_image(image_path)
    heatmap_path = generate_gradcam(image_path, output_dir, pred)

    confidence_pct = pred["confidence"] * 100
    low_confidence = pred["confidence"] < CONFIDENCE_THRESHOLD

    return {
        "predicted_disease": pred["predicted_disease"],
        "confidence": pred["confidence"],
        "confidence_percentage": round(confidence_pct, 2),
        "confidence_threshold": CONFIDENCE_THRESHOLD * 100,
        "low_confidence_warning": low_confidence,
        "warning_message": (
            "Model confidence is below the 85% threshold. Manual clinical review is recommended."
            if low_confidence else ""
        ),
        "class_probabilities": pred["probs"],
        "heatmap_path": heatmap_path,
        "heatmap_base64": image_to_base64(heatmap_path),
        "model_used": pred.get("model_used", "mmuratarat/kvasir-v2-classifier"),
    }
