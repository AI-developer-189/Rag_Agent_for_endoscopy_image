import React from "react";

const GradCAMViewer = ({ heatmapUrl }) => {
  if (!heatmapUrl) return null;
  return (
    <div className="grad-cam-viewer">
      <img
        src={heatmapUrl}
        alt="Grad-CAM Heatmap"
        style={{ width: "100%", borderRadius: "4px" }}
      />
    </div>
  );
};

export default GradCAMViewer;