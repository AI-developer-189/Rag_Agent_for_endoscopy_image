import React, { useEffect, useState } from "react";
import { fetchPatients, getPatientPredictions } from "../lib/api";

const History = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadPatients() {
      try {
        const data = await fetchPatients();
        setPatients(data);
      } catch (error) {
        console.error("Failed to load patients:", error);
      }
    }
    loadPatients();
  }, []);

  const loadPredictions = async (patient) => {
    setLoading(true);
    setSelectedPatient(patient);
    try {
      const data = await getPatientPredictions(patient.id);
      setPredictions(data);
    } catch (error) {
      console.error("Failed to load predictions:", error);
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="history-page">
      <h2>Prediction History</h2>

      <div className="card">
        <h3>Select Patient</h3>
        {patients.length === 0 && <p>No patients found.</p>}
        <ul className="patient-select-list">
          {patients.map((p) => (
            <li key={p.id} className={selectedPatient?.id === p.id ? "active" : ""} onClick={() => loadPredictions(p)}>
              {p.full_name} ({p.age}) - {p.patient_ref}
            </li>
          ))}
        </ul>
      </div>

      {selectedPatient && (
        <div className="card">
          <h3>Prediction History for {selectedPatient.full_name}</h3>
          {loading && <p>Loading...</p>}
          {!loading && predictions.length === 0 && <p>No predictions for this patient.</p>}
          <ul>
            {predictions.map((p) => (
              <li key={p.study_id} className="prediction-item">
                <strong>{p.predicted_disease}</strong> {p.confidence}%
                {p.heatmap_url && (
                  <img src={`http://localhost:8000${p.heatmap_url}`} alt="Grad-CAM heatmap" className="heatmap-thumb" />
                )}
                {p.low_confidence_warning && <span className="confidence-warning"> ⚠ Low confidence</span>}
                <div className="prediction-meta">
                  <span>{new Date(p.created_at).toLocaleString()}</span>
                  <span>Study: {p.study_id}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default History;
