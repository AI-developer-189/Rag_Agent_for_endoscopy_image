import React from "react";

const RiskCard = ({ disease, highRiskConsiderations }) => {
  return (
    <div className="risk-card">
      <strong>Disease:</strong> {disease}
      <ul>
        {highRiskConsiderations.map((risk, idx) => (
          <li key={idx}>{risk}</li>
        ))}
      </ul>
    </div>
  );
};

export default RiskCard;