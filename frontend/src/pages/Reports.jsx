import React, { useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { fetchPatients, getPatientPredictions, downloadReport } from "../lib/api";


const Reports = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [report, setReport] = useState(null);

  useEffect(() => {
    async function loadPatients() {
      const data = await fetchPatients();
      setPatients(data);
    }
    loadPatients();
  }, []);

  const loadPredictions = async (patientId) => {
    const data = await getPatientPredictions(patientId);
    setPredictions(data);
    setSelectedPatientId(patientId);
  };

  const handleDownload = async () => {
    if (!report?.pdf_path) return;
    const blob = await downloadReport(selectedPatientId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Endoscopy_Report_${selectedPatientId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="reports-page">
      <h2>Reports</h2>

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
          <h3>Prediction History</h3>
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

export default Reports;