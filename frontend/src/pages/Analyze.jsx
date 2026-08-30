import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { analyzeImage, fetchPatients, API_BASE } from "../lib/api";
import { Upload, Loader2, AlertTriangle, FileText, Image as ImageIcon } from "lucide-react";

const Analyze = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const patientRefFromUrl = location?.search?.match(/[?&]patient=([^&]+)/)?.[1] || "";

  useEffect(() => {
    async function loadPatients() {
      try {
        const data = await fetchPatients();
        setPatients(data);
      } catch (err) {
        console.error("Failed to load patients:", err);
      }
    }
    loadPatients();
  }, []);

  useEffect(() => {
    if (patientRefFromUrl) {
      const patient = patients.find((p) => p.patient_ref === patientRefFromUrl);
      if (patient) setSelectedPatient(patient);
    }
  }, [patientRefFromUrl, patients]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImageFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => setImagePreview(ev.target.result);
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!selectedPatient || !imageFile) return;
    setAnalyzing(true);
    setError("");
    setResult(null);
    try {
      const res = await analyzeImage(imageFile, selectedPatient.patient_ref);
      setResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const staticUrl = (path) => (path ? `${API_BASE}${path}` : "");

  return (
    <div className="analyze-page">
      <div className="dashboard-header">
        <div>
          <h1>Clinical Analysis</h1>
          <p>Agentic AI endoscopy image processing with RAG and Grad-CAM</p>
        </div>
      </div>

      {error && <div className="error-toast">{error}</div>}

      <div className="analyze-layout">
        <div className="analyze-left">
          <div className="card">
            <h3>1. Select Patient</h3>
            {patients.length === 0 && <p>No patients found. <button className="link-btn" onClick={() => navigate("/patients")}>Create a patient first</button></p>}
            <select
              value={selectedPatient?.patient_ref || ""}
              onChange={(e) => setSelectedPatient(patients.find((p) => p.patient_ref === e.target.value))}
              className="full-width"
            >
              <option value="">-- Select patient --</option>
              {patients.map((p) => (
                <option key={p.id} value={p.patient_ref}>{p.full_name} - {p.patient_ref}</option>
              ))}
            </select>
            {selectedPatient && (
              <div className="patient-chip">
                {selectedPatient.full_name} | {selectedPatient.age} / {selectedPatient.sex}
              </div>
            )}
          </div>

          {selectedPatient && (
            <div className="card">
              <h3>2. Upload Endoscopy Image</h3>
              <form onSubmit={handleAnalyze}>
                <label className="upload-drop" htmlFor="endo-image">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Preview" className="upload-preview" />
                  ) : (
                    <div className="upload-placeholder">
                      <ImageIcon size={32} />
                      <p>Click to choose an endoscopy image (JPG/PNG)</p>
                    </div>
                  )}
                  <input id="endo-image" type="file" accept="image/*" onChange={handleFileChange} hidden />
                </label>
                {imageFile && <p className="file-name">{imageFile.name}</p>}
                <button type="submit" className="btn-primary full-width" disabled={analyzing || !imageFile}>
                  {analyzing ? (<><Loader2 size={18} className="spin" /> Analyzing...</>) : (<><Upload size={18} /> Analyze Image</>)}
                </button>
              </form>
              {analyzing && <p className="hint">Running Swin prediction, Grad-CAM, segmentation, RAG retrieval and agentic reasoning...</p>}
            </div>
          )}
        </div>

        {result && (
          <div className="analyze-right">
            <div className="card">
              <h3>Analysis Results</h3>
              <div className="kpi-row">
                <div className="kpi-card">
                  <strong>Diagnosis:</strong> {result.prediction?.predicted_disease}
                </div>
                <div className="kpi-card">
                  <strong>Confidence:</strong> {result.prediction?.confidence_percentage ?? (result.prediction?.confidence * 100).toFixed(1)}%
                </div>
                <div className="kpi-card">
                  <strong>Model:</strong> {result.prediction?.model_used?.split("/").pop()}
                </div>
              </div>

              {result.prediction?.low_confidence_warning && (
                <div className="warning-banner"><AlertTriangle size={18} /> {result.prediction?.warning_message}</div>
              )}

              <div className="image-grid">
                {result.image_urls?.original && (
                  <figure>
                    <img src={staticUrl(result.image_urls.original)} alt="Original" />
                    <figcaption>Original</figcaption>
                  </figure>
                )}
                {result.gradcam?.heatmap_url && (
                  <figure>
                    <img src={staticUrl(result.gradcam.heatmap_url)} alt="Grad-CAM heatmap" />
                    <figcaption>Grad-CAM Heatmap</figcaption>
                  </figure>
                )}
                {result.segmentation?.overlay_url && (
                  <figure>
                    <img src={staticUrl(result.segmentation.overlay_url)} alt="Segmentation overlay" />
                    <figcaption>Segmentation Overlay</figcaption>
                  </figure>
                )}
              </div>

              {result.severity && (
                <div className="severity-row">
                  <span><strong>Severity:</strong> {result.severity.severity_level}</span>
                  <span><strong>Lesion coverage:</strong> {result.severity.percent_coverage}%</span>
                </div>
              )}

              {result.agent_analysis && (
                <div className="agent-section">
                  <h4><FileText size={18} /> Agentic Clinical Reasoning ({result.agent_analysis.generated_by})</h4>
                  <p><strong>Probable finding:</strong> {result.agent_analysis.probable_disease}</p>
                  <p><strong>Clinical reasoning:</strong> {result.agent_analysis.clinical_reasoning}</p>

                  {result.agent_analysis.patient_factors?.length > 0 && (
                    <div>
                      <strong>Patient factors considered:</strong>
                      <ul>{result.agent_analysis.patient_factors.map((f, i) => <li key={i}>{f}</li>)}</ul>
                    </div>
                  )}

                  {result.agent_analysis.overlooked_high_risk_considerations?.length > 0 && (
                    <div className="high-risk">
                      <strong><AlertTriangle size={14} /> High-risk considerations:</strong>
                      <ul>{result.agent_analysis.overlooked_high_risk_considerations.map((r, i) => <li key={i}>{r}</li>)}</ul>
                    </div>
                  )}

                  {result.agent_analysis.guideline_considerations?.length > 0 && (
                    <div>
                      <strong>Retrieved RAG clinical guidelines:</strong>
                      <ul>{result.agent_analysis.guideline_considerations.map((g, i) => (
                        <li key={i}><em>[{g.source}]</em> {g.text}</li>
                      ))}</ul>
                    </div>
                  )}

                  {result.agent_analysis.recommendations?.length > 0 && (
                    <div>
                      <strong>Recommendations:</strong>
                      <ul>{result.agent_analysis.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>
                    </div>
                  )}

                  {result.agent_analysis.disclaimer && (
                    <p className="disclaimer"><em>{result.agent_analysis.disclaimer}</em></p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analyze;
