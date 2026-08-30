import React from "react";

const GuidelineSources = ({ guidelineConsiderations }) => {
  if (!guidelineConsiderations || guidelineConsiderations.length === 0) {
    return <p>No specific guidelines found.</p>;
  }
  return (
    <div>
      {guidelineConsiderations.map((g, idx) => (
        <div key={idx} style={{ marginBottom: "0.5rem", paddingBottom: "0.5rem", borderBottom: "1px solid var(--border-color)" }}>
          <strong>{g.source}:</strong> {g.text}
        </div>
      ))}
    </div>
  );
};

export default GuidelineSources;