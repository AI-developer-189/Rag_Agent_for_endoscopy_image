import React, { useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { fetchPatients, getPatientPredictions } from "../lib/api";


const History = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    async function loadPatients() {
      const data = await fetchPatients();
      setPatients(data);
    }
    loadPatients();
  }, []);

  const loadPredictions = async (patientRef) => {
    const data = await getPatientPredictions(patientRef);
    setPredictions(data);
    setSelectedPatientId(patientRef);
  };

  return (
    <div className="history-page">
      <h2>Prediction History</h2>

      <div className="card">
        <h3>Select Patient</h3>
        {patients.length === 0 && <p>No patients found.</p>}
        <ul>
          {patients.map((p) => (
            <li key={p.patient_ref} onClick={() => loadPredictions(p.patient_ref)}>
              {p.full_name} ({p.age})
            </li>
          ))}
</ul>
        </div>

      {selectedPatientId && (
        <div className="card">
          <h3>Prediction History for {patients.find((p) => p.patient_ref === selectedPatientId)?.full_name}</h3>
          {predictions.length === 0 && <p>No predictions for this patient.</p>}
          <ul>
            {predictions.map((p) => (
              <li key={p.study_id}>
                <strong>{p.predicted_disease}</strong> {p.confidence}%
                {(p.low_confidence_warning && <span style={{ color: "var(--error-color)" }}> ⚠ Low confidence</span>)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default History;