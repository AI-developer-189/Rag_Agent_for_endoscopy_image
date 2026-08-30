import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { analyzeImage, fetchPatients, createPatient, API_BASE } from "../lib/api";

const Analyze = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const patientRefFromUrl = location?.search?.replace("?", "").replace("patient=", "") || "";

  useEffect(() => {
    async function loadPatients() {
      const data = await fetchPatients();
      setPatients(data);
    }
    loadPatients();
  }, []);

  useEffect(() => {
    if (patientRefFromUrl) {
      const patient = patients.find((p) => p.patient_ref === patientRefFromUrl);
      if (patient) {
        setSelectedPatient(patient);
      }
    }
  }, [patientRefFromUrl, patients]);

  const selectPatient = (patient) => {
    setSelectedPatient(patient);
  };

  const handleFileChange = (e) => {
    setImageFile(e.target.files[0]);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!selectedPatient || !imageFile) return;
    setUploading(true);
    setAnalyzing(true);
    try {
      const result = await analyzeImage(imageFile, selectedPatient.patient_ref);
      setAnalysisResult(result);
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setUploading(false);
      setAnalyzing(false);
    }
  };

  return (
    <div className="analyze-page">
      <h2>Clinical Analysis</h2>

      {/* Patient Selection */}
      <div className="card">
        <h3>Select Patient</h3>
        {patients.length === 0 && <p>No patients found. Create a patient first.</p>}
        <select
          value={selectedPatient?.patient_ref || ""}
          onChange={(e) => selectPatient(patients.find((p) => p.patient_ref === e.target.value))}
          style={{ width: "100%", marginBottom: "1rem" }}
        >
          <option value="">-- Select patient --</option>
          {patients.map((p) => (
            <option key={p.patient_ref} value={p.patient_ref}>
              {p.full_name} - {p.patient_ref}
            </option>
          ))}
        </select>
        <button
          onClick={() => navigate("/patients")}
          style={{ marginTop: "0.5rem", background: "none", border: "none", color: "var(--primary)", cursor: "pointer" }}
        >
          Manage Patients
</button>
        </div>

      {/* Image Upload Section */}
      {selectedPatient && (
        <div className="card">
          <h3>Upload Endoscopy Image</h3>
          <form onSubmit={handleAnalyze} style={{ marginTop: "1rem" }}>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              style={{ marginBottom: "0.5rem" }}
            />
            <button>Analyze Image</button>
          </form>
          {uploading && <p>Uploading...</p>}
          {analyzing && <p>Analyzing...</p>}
        </div>
      )}

      {/* Results Section */}
      {analysisResult && (
        <div className="card">
          <h3>Analysis Results</h3>
          <div className="kpi-row">
            <div className="kpi-card">
              <strong>Diagnosis:</strong> {analysisResult.prediction.predicted_disease}
            </div>
            <div className="kpi-card">
              <strong>Confidence:</strong> {analysisResult.prediction.confidence_percentage}%
            </div>
          </div>
          {analysisResult.gradcam.heatmap_url && (
            <img
              src={`${API_BASE}${analysisResult.gradcam.heatmap_url}`}
              alt="Grad-CAM Heatmap"
              style={{ width: "100%", marginTop: "1rem" }}
            />
          )}
          {analysisResult.severity && (
            <div style={{ marginTop: "1rem" }}>
              <strong>Severity:</strong> {analysisResult.severity.severity_level}
            </div>
          )}
          {analysisResult.segmentation && analysisResult.segmentation.overlay_url && (
            <div style={{ marginTop: "1rem" }}>
              <strong>Segmentation Overlay:</strong> <a
                href={`${API_BASE}${analysisResult.segmentation.overlay_url}`}
                target="_blank"
                rel="noopener"
              >
                View Overlay Image
              </a>
            </div>
          )}
          {analysisResult.severity && (
            <div style={{ marginTop: "1rem" }}>
              <strong>Coverage:</strong> {analysisResult.severity.percent_coverage}%
            </div>
          )}
          {analysisResult.agent_analysis && (
            <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--border-color)", paddingTop: "1rem" }}>
              <h4>AI Clinical Reasoning</h4>
              <p><strong>Probable Disease:</strong> {analysisResult.agent_analysis.probable_disease || analysisResult.prediction.predicted_disease}</p>
              <p><strong>Model Confidence:</strong> {analysisResult.agent_analysis.model_confidence || (analysisResult.prediction.confidence * 100).toFixed(1)}%</p>
              <p><strong>Clinical Reasoning:</strong> {analysisResult.agent_analysis.clinical_reasoning || 'No reasoning available'}</p>
              {analysisResult.agent_analysis.patient_factors && (
                <p><strong>Patient Factors:</strong> {analysisResult.agent_analysis.patient_factors.join(', ') || 'None'}</p>
              )}
              {analysisResult.agent_analysis.rag_guidelines && (
                <p><strong>Relevant Guidelines:</strong> {analysisResult.agent_analysis.rag_guidelines.map((g, i) => `${i + 1}. ${g.text.substring(0, 100)}...`).join(', ') || 'None'}</p>
              )}
              {analysisResult.agent_analysis.recommendations && (
                <p><strong>Recommendations:</strong> {analysisResult.agent_analysis.recommendations.join('. ') || 'None'}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Analyze;