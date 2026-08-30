import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchPatients, createPatient, deletePatient } from "../lib/api";
import { Plus, Trash2, ArrowRight } from "lucide-react";

const Patients = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newPatient, setNewPatient] = useState({
    full_name: "",
    age: "",
    sex: "Male",
    medical_history: "",
    allergies: "",
    medications: "",
    previous_endoscopy: "",
    family_history: "",
  });

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setLoading(true);
    try {
      const data = await fetchPatients();
      setPatients(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load patients.");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const data = await createPatient({
        full_name: newPatient.full_name.trim(),
        age: Number(newPatient.age),
        sex: newPatient.sex,
        medical_history: newPatient.medical_history,
        allergies: newPatient.allergies,
        medications: newPatient.medications,
        previous_endoscopy: newPatient.previous_endoscopy,
        family_history: newPatient.family_history,
      });
      setPatients([data, ...patients]);
      setNewPatient({
        full_name: "",
        age: "",
        sex: "Male",
        medical_history: "",
        allergies: "",
        medications: "",
        previous_endoscopy: "",
        family_history: "",
      });
      setShowCreate(false);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create patient.");
    }
  };

  const handleDelete = async (patient) => {
    if (!window.confirm(`Delete patient ${patient.full_name} and all associated analyses?`)) return;
    try {
      await deletePatient(patient.id);
      setPatients(patients.filter((p) => p.id !== patient.id));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete patient.");
    }
  };

  const handleAnalyze = (patient) => {
    navigate(`/analyze?patient=${patient.patient_ref}`);
  };

  return (
    <div className="patients-page">
      <div className="dashboard-header">
        <div>
          <h1>Patient Management</h1>
          <p>{patients.length} patients on record</p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={18} /> New Patient
        </button>
      </div>

      {error && <div className="error-toast">{error}</div>}

      <div className="card">
        {loading && <p>Loading...</p>}
        {!loading && patients.length === 0 && (
          <div className="empty-state">
            <h3>No Patients Yet</h3>
            <p>Create your first patient record to begin endoscopy analysis</p>
            <button className="btn-primary" onClick={() => setShowCreate(true)}>
              <Plus size={18} /> Add Patient
            </button>
          </div>
        )}

        {patients.length > 0 && (
          <div className="patient-table-container">
            <table className="patient-table">
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>Reference</th>
                  <th>Age / Sex</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>
                      <div className="patient-info">
                        <div className="patient-avatar">
                          {patient.full_name?.charAt(0)?.toUpperCase()}
                        </div>
                        <span className="patient-name">{patient.full_name}</span>
                      </div>
                    </td>
                    <td><span className="patient-ref">{patient.patient_ref}</span></td>
                    <td>{patient.age} / {patient.sex}</td>
                    <td>
                      <button className="action-btn primary" onClick={() => handleAnalyze(patient)} title="Analyze">
                        <ArrowRight size={16} />
                      </button>
                      <button className="action-btn danger" onClick={() => handleDelete(patient)} title="Delete">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><Plus size={20} /> New Patient Record</h2>
              <button className="modal-close" onClick={() => setShowCreate(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input type="text" value={newPatient.full_name} required
                      onChange={(e) => setNewPatient({ ...newPatient, full_name: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Age *</label>
                    <input type="number" value={newPatient.age} required min={0} max={120}
                      onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Sex *</label>
                    <select value={newPatient.sex}
                      onChange={(e) => setNewPatient({ ...newPatient, sex: e.target.value })}>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                    </select>
                  </div>
                </div>
                <div className="form-group full-width">
                  <label>Medical History</label>
                  <textarea rows={3} value={newPatient.medical_history}
                    onChange={(e) => setNewPatient({ ...newPatient, medical_history: e.target.value })} />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Allergies</label>
                    <input type="text" value={newPatient.allergies}
                      onChange={(e) => setNewPatient({ ...newPatient, allergies: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Medications</label>
                    <input type="text" value={newPatient.medications}
                      onChange={(e) => setNewPatient({ ...newPatient, medications: e.target.value })} />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Previous Endoscopy</label>
                    <input type="text" value={newPatient.previous_endoscopy}
                      onChange={(e) => setNewPatient({ ...newPatient, previous_endoscopy: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Family History</label>
                    <input type="text" value={newPatient.family_history}
                      onChange={(e) => setNewPatient({ ...newPatient, family_history: e.target.value })} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn-primary"><Plus size={16} /> Create Patient</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Patients;
