"""
agent/agent.py
ONE Agentic AI Orchestrator for clinical decision support.

Workflow:
  1. Prediction Tool   → Vision classification + Grad-CAM
  2. Patient Tool      → patient history + risk context
  3. RAG Tool          → retrieve relevant clinical guidelines
  4. LLM reasoning     → Gemini (or structured template fallback)
  5. Return structured JSON response

The agent does NOT claim definitive diagnosis.
All output carries the medical disclaimer.
"""
import os
import json
from typing import Dict, Any, List

from app.agent.prediction_tool import run_prediction_tool
from app.agent.patient_tool import get_patient_history
from app.agent.rag_tool import retrieve_guidelines_tool

DISCLAIMER = (
    "This system is intended for research and clinical decision support only. "
    "It does not replace professional medical judgment, diagnosis, or treatment. "
    "All findings must be reviewed and confirmed by a qualified clinician."
)

# ─── Disease-to-risk mapping ──────────────────────────────────────────────────
DISEASE_RISK_MAP = {
    "dyed-lifted-polyps": {
        "display": "Polyp (Post-Lifting)",
        "risk_items": [
            "Polyp morphology requires histopathological confirmation",
            "Non-lifting may suggest submucosal invasion",
            "Adequate lifting confirms suitability for endoscopic resection",
        ],
        "high_risk_considerations": [
            "If non-lifting: consider malignant invasion, refer to surgical team",
            "Screen for hereditary polyposis syndromes if multiple polyps present",
        ],
    },
    "dyed-resection-margins": {
        "display": "Resection Margins (Post-EMR/ESD)",
        "risk_items": [
            "Dyed resection margins require assessment for completeness",
            "Positive margins indicate incomplete resection — residual neoplasia possible",
        ],
        "high_risk_considerations": [
            "Positive margins: repeat endoscopic resection or surgical referral",
            "Surveillance endoscopy within 3–6 months to confirm clear margins",
        ],
    },
    "esophagitis": {
        "display": "Esophagitis",
        "risk_items": [
            "Chronic GERD can progress to Barrett's esophagus",
            "Alarm features (dysphagia, weight loss) require urgent evaluation",
            "PPI therapy is first-line treatment",
        ],
        "high_risk_considerations": [
            "Long-standing severe esophagitis: biopsy to exclude Barrett's or dysplasia",
            "Esophageal stricture if untreated — monitor for dysphagia",
        ],
    },
    "normal-cecum": {
        "display": "Normal Cecum",
        "risk_items": [
            "Normal cecal appearance — no active pathology identified",
            "Ileocecal valve visualisation confirms adequate colonoscopic reach",
        ],
        "high_risk_considerations": [
            "Continue age-appropriate colorectal cancer screening schedule",
        ],
    },
    "normal-pylorus": {
        "display": "Normal Pylorus",
        "risk_items": [
            "Normal pyloric function — no obstruction or ulceration seen",
        ],
        "high_risk_considerations": [
            "If symptoms persist, consider H. pylori testing and functional dyspepsia work-up",
        ],
    },
    "normal-z-line": {
        "display": "Normal Z-Line",
        "risk_items": [
            "Sharp squamocolumnar junction — no Barrett's esophagus features",
            "Normal Z-line is a reassuring finding in GERD surveillance",
        ],
        "high_risk_considerations": [
            "If GERD symptoms persist despite normal Z-line: consider functional heartburn or pH monitoring",
        ],
    },
    "polyps": {
        "display": "Polyps",
        "risk_items": [
            "Polyp type (adenomatous vs. hyperplastic) requires histopathology",
            "Size, morphology, and number determine surveillance intervals",
            "Advanced adenoma features: size ≥10mm, villous component, high-grade dysplasia",
        ],
        "high_risk_considerations": [
            "Multiple adenomas: consider Lynch syndrome or FAP — refer clinical genetics",
            "Large sessile polyps (≥20mm): EMR or ESD required; consider incomplete resection risk",
            "Any polyp with high-grade dysplasia: urgent multidisciplinary team review",
        ],
    },
    "ulcerative-colitis": {
        "display": "Ulcerative Colitis",
        "risk_items": [
            "UC severity grading determines treatment escalation",
            "Colorectal cancer risk increases after 8–10 years of pancolitis",
            "Primary sclerosing cholangitis co-diagnosis significantly elevates CRC risk",
        ],
        "high_risk_considerations": [
            "Severe active UC (Mayo score 3): consider hospital admission and IV therapy",
            "Toxic megacolon: urgent surgical consultation",
            "Any dysplasia on biopsy: colectomy discussion required",
            "Long-standing disease without surveillance: initiate cancer surveillance colonoscopy",
        ],
    },
}


# ─── Fallback template (no LLM) ───────────────────────────────────────────────
def _build_template_response(
    prediction: Dict[str, Any],
    patient_data: Dict[str, Any],
    guidelines: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate a structured response without an LLM."""
    disease = prediction.get("predicted_disease", "unknown")
    confidence = prediction.get("confidence", 0.0)
    confidence_pct = round(confidence * 100, 1)
    low_conf = prediction.get("low_confidence_warning", False)

    key = disease.lower().replace("_", "-").replace(" ", "-")
    disease_info = DISEASE_RISK_MAP.get(key, DISEASE_RISK_MAP.get(disease, {
        "display": disease.replace("-", " ").replace("_", " ").title(),
        "risk_items": ["Clinical review recommended for complete assessment."],
        "high_risk_considerations": ["Specialist referral may be required."],
    }))

    # Patient factors
    patient_factors: List[str] = []
    if patient_data.get("found"):
        p = patient_data["patient"]
        patient_factors.append(f"Patient: {p['full_name']}, {p['age']}yo {p['sex']}")
        if p.get("medical_history") and p["medical_history"] != "Not recorded":
            patient_factors.append(f"Medical history: {p['medical_history'][:200]}")
        if p.get("medications") and p["medications"] != "None recorded":
            patient_factors.append(f"Current medications: {p['medications'][:150]}")
        if p.get("family_history") and p["family_history"] != "None recorded":
            patient_factors.append(f"Family history: {p['family_history'][:150]}")
        if p.get("previous_endoscopy") and p["previous_endoscopy"] != "None recorded":
            patient_factors.append(f"Previous endoscopy: {p['previous_endoscopy'][:150]}")
        patient_factors.extend(patient_data.get("risk_context", []))
    else:
        patient_factors.append("Patient data not available — analysis based on image findings only.")

    # Previous predictions context
    prev_preds = patient_data.get("previous_predictions", []) if patient_data.get("found") else []
    if prev_preds:
        prev_str = "; ".join(
            f"{p['predicted_disease']} ({p['confidence']}%)" for p in prev_preds[:3]
        )
        patient_factors.append(f"Prior endoscopic findings: {prev_str}")

    # Clinical reasoning
    reasoning_parts = [
        f"The vision classification model classified this endoscopy image as '{disease_info['display']}' "
        f"with a confidence of {confidence_pct}%.",
    ]
    if low_conf:
        reasoning_parts.append(
            "Note: confidence is below the 85% threshold — this finding should be treated with caution "
            "and manual clinical review is strongly recommended."
        )
    reasoning_parts.extend(disease_info["risk_items"])
    if prev_preds:
        reasoning_parts.append(
            f"This patient has {len(prev_preds)} prior endoscopic study(ies) on record, "
            "which may provide relevant longitudinal context."
        )

    # Guideline considerations
    guideline_considerations = [
        {"source": g.get("source", "Clinical Guidelines"), "text": g.get("text", "")[:400]}
        for g in guidelines
        if g.get("score", 0) > 0.0
    ]

    # Recommendations
    recommendations = [
        "This report is generated by an AI system for clinical decision support. All findings must be reviewed by a qualified clinician.",
        f"The model prediction indicates: {disease_info['display']} — histopathological confirmation is recommended where applicable.",
    ]
    if low_conf:
        recommendations.append("Low confidence prediction: do not rely on this result without independent clinical assessment.")
    recommendations.append("Ensure appropriate follow-up imaging or biopsy per clinical guidelines.")
    recommendations.append("Document all findings in the patient's medical record with appropriate clinical context.")

    return {
        "probable_disease": disease_info["display"],
        "model_confidence": confidence_pct,
        "confidence_warning": low_conf,
        "patient_factors": patient_factors,
        "overlooked_high_risk_considerations": disease_info["high_risk_considerations"],
        "clinical_reasoning": " ".join(reasoning_parts),
        "guideline_considerations": guideline_considerations,
        "recommendations": recommendations,
        "disclaimer": DISCLAIMER,
        "generated_by": "template",
    }


# ─── LLM-powered reasoning (Gemini) ───────────────────────────────────────────
def _build_llm_response(
    prediction: Dict[str, Any],
    patient_data: Dict[str, Any],
    guidelines: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Use Gemini to generate clinical reasoning. Falls back to template on failure."""
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("LLM_API_KEY", "")
    if not api_key:
        return _build_template_response(prediction, patient_data, guidelines)

    disease = prediction.get("predicted_disease", "unknown")
    confidence_pct = round(prediction.get("confidence", 0.0) * 100, 1)
    low_conf = prediction.get("low_confidence_warning", False)

    patient_summary = "Patient data unavailable."
    if patient_data.get("found"):
        p = patient_data["patient"]
        patient_summary = (
            f"Patient: {p['full_name']}, {p['age']}yo {p['sex']}. "
            f"Medical history: {p.get('medical_history', 'Not recorded')}. "
            f"Medications: {p.get('medications', 'None recorded')}. "
            f"Family history: {p.get('family_history', 'None recorded')}. "
            f"Previous endoscopy: {p.get('previous_endoscopy', 'None recorded')}."
        )
        risk_ctx = patient_data.get("risk_context", [])
        if risk_ctx:
            patient_summary += f" Risk flags: {'; '.join(risk_ctx)}."
        prev_preds = patient_data.get("previous_predictions", [])
        if prev_preds:
            patient_summary += f" Previous predictions: {'; '.join(p2['predicted_disease'] for p2 in prev_preds[:3])}."

    guideline_text = "\n".join(
        f"- [{g.get('source', '')}]: {g.get('text', '')[:300]}"
        for g in guidelines[:3]
    )

    prompt = f"""You are an expert clinical AI assistant providing decision support for endoscopic findings.
You must NOT claim definitive diagnosis. Use careful, measured clinical language.

== ENDOSCOPY AI FINDINGS ==
Predicted finding: {disease}
Model confidence: {confidence_pct}%
Low confidence warning: {low_conf}

== PATIENT CONTEXT ==
{patient_summary}

== RETRIEVED CLINICAL GUIDELINES ==
{guideline_text}

== TASK ==
Generate a structured clinical decision support analysis. Output ONLY valid JSON (no markdown) with this exact schema:
{{
    "probable_disease": "human-readable finding name",
    "model_confidence": {confidence_pct},
    "confidence_warning": {str(low_conf).lower()},
    "patient_factors": ["list of relevant patient factors"],
    "overlooked_high_risk_considerations": ["list of potential high-risk considerations the clinician should not overlook"],
    "clinical_reasoning": "one paragraph of clinical reasoning in measured, non-definitive language",
    "guideline_considerations": [{{"source": "source name", "text": "relevant guideline text"}}],
    "recommendations": ["list of actionable recommendations"],
    "disclaimer": "{DISCLAIMER}"
}}

Rules:
- Never say the patient "definitely has" any disease
- Always say "the model indicates" or "findings are consistent with" or "consider"
- If confidence < 85%, prominently note uncertainty
- Include at least 2 overlooked high-risk considerations
- Include at least 3 recommendations
- Keep clinical_reasoning under 150 words
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_name = os.environ.get("LLM_MODEL", "gemini-1.5-flash")
        llm_model = genai.GenerativeModel(model_name)
        response = llm_model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown fences if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["generated_by"] = "gemini"
        return result

    except json.JSONDecodeError as je:
        print(f"[Agent] LLM returned invalid JSON: {je}. Falling back to template.")
        return _build_template_response(prediction, patient_data, guidelines)
    except Exception as e:
        print(f"[Agent] LLM call failed: {e}. Falling back to template.")
        return _build_template_response(prediction, patient_data, guidelines)


# ─── Main Orchestrator ────────────────────────────────────────────────────────
class ClinicalAgent:
    """
    ONE Agentic AI Orchestrator.
    Combines Prediction Tool, Patient Tool, and RAG Tool.
    Uses LLM (Gemini) for reasoning, falls back to template.
    """

    def run(
        self,
        image_path: str,
        patient_id: int,
        current_user_id: int,
        db,
        output_dir: str = "outputs",
    ) -> Dict[str, Any]:
        """
        Full agentic analysis pipeline.
        """
        # ── Tool 1: Vision Prediction + Grad-CAM ────────────────────────────
        prediction = run_prediction_tool(image_path, output_dir)

        # ── Tool 2: Patient History ─────────────────────────────────────────
        patient_data = get_patient_history(patient_id, current_user_id, db)

        # ── Tool 3: RAG Guideline Retrieval ────────────────────────────────
        disease = prediction.get("predicted_disease", "unknown")
        severity_info = patient_data.get("risk_context", [])
        patient_context = (
            "; ".join(severity_info[:3]) if severity_info else ""
        )
        guidelines = retrieve_guidelines_tool(
            disease=disease,
            patient_context=patient_context,
            top_k=3,
        )

        # ── Agent Reasoning (LLM or template) ──────────────────────────────
        agent_response = _build_llm_response(prediction, patient_data, guidelines)

        # Attach raw prediction data for heatmap display
        agent_response["_prediction"] = {
            "predicted_disease": prediction["predicted_disease"],
            "confidence": prediction["confidence"],
            "confidence_percentage": prediction["confidence_percentage"],
            "low_confidence_warning": prediction["low_confidence_warning"],
            "warning_message": prediction.get("warning_message", ""),
            "class_probabilities": prediction.get("class_probabilities", {}),
            "heatmap_path": prediction.get("heatmap_path", ""),
            "heatmap_base64": prediction.get("heatmap_base64", ""),
            "model_used": prediction.get("model_used", "mmuratarat/kvasir-v2-classifier"),
        }

        # Attach patient summary
        agent_response["_patient"] = patient_data.get("patient", {})

        return agent_response


# Module-level singleton agent
clinical_agent = ClinicalAgent()
