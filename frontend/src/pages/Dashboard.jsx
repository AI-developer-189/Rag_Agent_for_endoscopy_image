import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { fetchPatients, createPatient, getPatientPredictions } from "../lib/api";


const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [error, setError] = useState("");
  const [newPatient, setNewPatient] = useState({
    full_name: "",
    age: "",
    sex: "",
    medical_history: "",
    allergies: "",
    medications: "",
    previous_endoscopy: "",
    family_history: "",
  });
  const [predictions, setPredictions] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);

  useEffect(() => {
    async function loadPatients() {
      try {
        const data = await fetchPatients();
        setPatients(data);
      } catch (error) {
        console.error("Failed to load patients:", error);
        if (error.response?.status === 401) {
          setPatients([]);
          return;
        }
        setPatients([]);
        setError(
          error.response?.data?.detail || "Unable to load patients."
        );
      }
    }
    loadPatients();
  }, []);

  const handleCreatePatient = async (e) => {
    e.preventDefault();
    try {
      const data = await createPatient(newPatient);
      setPatients([...patients, data]);
      setSelectedPatientId(data.id);
    } catch (error) {
      console.error("Failed to create patient:", error);
      setError(
        error.response?.data?.detail || "Failed to create patient."
      );
    }
  };

  const loadPatientPredictions = async (patientId) => {
    try {
      const data = await getPatientPredictions(patientId);
      setPredictions(data);
    } catch (error) {
      console.error("Failed to load predictions:", error);
      setError(
        error.response?.data?.detail || "Failed to load predictions."
      );
    }
  };

  return (
    <div className="dashboard-page">
      <h2>Dashboard</h2>
      {error && <p className="error-message">{error}</p>}

      {/* Patient Management Section */}
      <div className="card">
        <h3>Patient Management</h3>
        <form
          onSubmit={handleCreatePatient}
          style={{ marginBottom: "1rem", display: "grid", gap: "0.5rem" }}
        >
          <input
            placeholder="Full name"
            value={newPatient.full_name}
            onChange={(e) =>
              setNewPatient({ ...newPatient, full_name: e.target.value })
            }
            required
          />
          <input
            type="number"
            placeholder="Age"
            value={newPatient.age}
            onChange={(e) =>
              setNewPatient({ ...newPatient, age: Number(e.target.value) })
            }
            required
          />
          <select
            value={newPatient.sex}
            onChange={(e) =>
              setNewPatient({ ...newPatient, sex: e.target.value })
            }
            required
          >
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
          <button type="submit" style={{ marginTop: "0.5rem" }}>
            Create Patient
          </button>
        </form>
      </div>

      {patients.length === 0 && <p>No patients found.</p>}

      <ul>
        {patients.map((p) => (
          <li
            key={p.patient_ref}
            onClick={() => navigate(`/analyze?patient=${p.patient_ref}`)}
          >
            {p.full_name} ({p.age}) - {p.sex}
          </li>
        ))}
      </ul>

      {/* Prediction History Section */}
      {selectedPatientId && (
        <div className="card">
          <h3>
            Prediction History for {selectedPatientId}
            <button
              onClick={() => setSelectedPatientId(null)}
              style={{
                float: "right",
                background: "none",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                fontSize: "0.75rem",
              }}
            >
              Close
            </button>
          </h3>
          {predictions.length === 0 && <p>No predictions yet.</p>}
          <ul>
            {predictions.map((p) => (
              <li key={p.study_id}>
                <strong>{p.predicted_disease}</strong>
                {p.confidence}% confidence
                {(p.low_confidence_warning && (
                  <span style={{ color: "var(--error-color)" }}>
                    \u26a0 Low confidence
                  </span>
                ))}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Dashboard;