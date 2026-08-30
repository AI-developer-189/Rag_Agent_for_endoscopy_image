import React from "react";

const ConfidenceBar = ({ confidence, lowConfidenceWarning }) => {
  const percentage = Math.round(confidence * 100);
  const color = lowConfidenceWarning ? "var(--error-color)" : "var(--success-color)";
  return (
    <div className="confidence-bar">
      <span className="confidence-label">Confidence</span>
      <div
        className="confidence-fill"
        style={{ width: `${percentage}%`, backgroundColor: color }}
      ></div>
      <span className="confidence-value">{percentage}%</span>
    </div>
  );
};

export default ConfidenceBar;