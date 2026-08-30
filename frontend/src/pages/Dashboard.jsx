import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { fetchPatients, createPatient, getPatientPredictions } from "../lib/api";
import { 
  Users, Plus, Search, ArrowRight, Eye, 
  Activity, FileText, AlertTriangle, CheckCircle2,
  Loader2
} from "lucide-react";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
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
  const [selectedPatient, setSelectedPatient] = useState(null);

  useEffect(() => {
    async function loadPatients() {
      setLoading(true);
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
      } finally {
        setLoading(false);
      }
    }
    loadPatients();
  }, []);

  const handleCreatePatient = async (e) => {
    e.preventDefault();
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
      setSelectedPatient(data);
      setShowCreateModal(false);
      setNewPatient({
        full_name: "",
        age: "",
        sex: "",
        medical_history: "",
        allergies: "",
        medications: "",
        previous_endoscopy: "",
        family_history: "",
      });
    } catch (error) {
      console.error("Failed to create patient:", error);
      setError(
        error.response?.data?.detail || "Failed to create patient."
      );
    }
  };

  const loadPatientPredictions = async (patient) => {
    try {
      const data = await getPatientPredictions(patient.id);
      setPredictions(data);
      setSelectedPatient(patient);
      setSelectedPatientId(patient.id);
    } catch (error) {
      console.error("Failed to load predictions:", error);
      setError(
        error.response?.data?.detail || "Failed to load predictions."
      );
    }
  };

  const handleSelectPatient = (patient) => {
    setSelectedPatient(patient);
    setSelectedPatientId(patient.id);
    navigate(`/analyze?patient=${patient.patient_ref}`);
  };

  const statCards = [
    { label: "Total Patients", value: patients.length, icon: Users, color: "var(--accent-blue)" },
    { label: "Analyses Today", value: predictions.length, icon: Activity, color: "var(--accent-color)" },
    { label: "Pending Reviews", value: predictions.filter(p => p.low_confidence_warning).length, icon: AlertTriangle, color: "var(--warning-color)" },
    { label: "Completed", value: predictions.filter(p => !p.low_confidence_warning).length, icon: CheckCircle2, color: "var(--success-color)" },
  ];

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Clinical Dashboard</h1>
          <p>Welcome back, {user?.full_name || "Clinician"}</p>
        </div>
        <button 
          className="btn-primary" 
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={18} /> New Patient
        </button>
      </div>

      {error && <div className="error-toast">{error}</div>}

      {/* Stats Grid */}
      <div className="stats-grid">
        {statCards.map((stat, i) => (
          <div key={i} className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: stat.color + "20" }}>
              <stat.icon size={20} style={{ color: stat.color }} />
            </div>
            <div className="stat-content">
              <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Patient List */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <Users size={20} /> Patient Records
            </h2>
            <p className="card-subtitle">{patients.length} patients under your care</p>
          </div>
          <div className="search-box">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search patients..." 
              className="search-input"
            />
          </div>
        </div>

        {loading && <div className="loading-state"><Loader2 size={24} className="spin" /> Loading patients...</div>}

        {!loading && patients.length === 0 && (
          <div className="empty-state">
            <Users size={48} />
            <h3>No Patients Yet</h3>
            <p>Create your first patient record to begin analysis</p>
            <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
              <Plus size={18} /> Add Patient
            </button>
          </div>
        )}

        {!loading && patients.length > 0 && (
          <div className="patient-table-container">
            <table className="patient-table">
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>Reference</th>
                  <th>Age / Sex</th>
                  <th>Last Analysis</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id} onClick={() => handleSelectPatient(patient)}>
                    <td>
                      <div className="patient-info">
                        <div className="patient-avatar">
                          {patient.full_name?.charAt(0)?.toUpperCase()}
                        </div>
                        <div>
                          <div className="patient-name">{patient.full_name}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="patient-ref">{patient.patient_ref}</span>
                    </td>
                    <td>
                      <span>{patient.age} / {patient.sex}</span>
                    </td>
                    <td>
                      {predictions.length > 0 && predictions[0].created_at 
                        ? new Date(predictions[0].created_at).toLocaleDateString()
                        : "—"}
                    </td>
                    <td>
                      {predictions.some(p => p.low_confidence_warning) ? (
                        <span className="status-badge warning">Review Needed</span>
                      ) : predictions.length > 0 ? (
                        <span className="status-badge success">Completed</span>
                      ) : (
                        <span className="status-badge pending">Pending</span>
                      )}
                    </td>
                    <td>
                      <button 
                        className="action-btn"
                        onClick={(e) => { e.stopPropagation(); loadPatientPredictions(patient); }}
                        title="View History"
                      >
                        <Eye size={16} />
                      </button>
                      <button 
                        className="action-btn primary"
                        onClick={(e) => { e.stopPropagation(); handleSelectPatient(patient); }}
                        title="New Analysis"
                      >
                        <ArrowRight size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Selected Patient Predictions */}
        {selectedPatient && predictions.length > 0 && (
          <div className="predictions-panel">
            <div className="panel-header">
              <h3>
                <FileText size={18} /> Analysis History for {selectedPatient.full_name}
              </h3>
              <button 
                className="btn-ghost"
                onClick={() => { setSelectedPatient(null); setSelectedPatientId(null); }}
              >
                Close
              </button>
            </div>
            <div className="predictions-list">
              {predictions.map((p) => (
                <div key={p.study_id} className="prediction-item">
                  <div className="prediction-main">
                    <span className="prediction-disease">{p.predicted_disease}</span>
                    <span className="prediction-confidence">
                      {p.confidence}% confidence
                    </span>
                    {p.low_confidence_warning && (
                      <span className="confidence-warning">
                        <AlertTriangle size={14} /> Low confidence
                      </span>
                    )}
                  </div>
                  <div className="prediction-meta">
                    <span>{new Date(p.created_at).toLocaleDateString()}</span>
                    <span>Study: {p.study_id}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Create Patient Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><Plus size={20} /> New Patient Record</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreatePatient}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input
                      type="text"
                      value={newPatient.full_name}
                      onChange={(e) => setNewPatient({ ...newPatient, full_name: e.target.value })}
                      placeholder="Dr. John Smith"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Age *</label>
                    <input
                      type="number"
                      value={newPatient.age}
                      onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })}
                      placeholder="45"
                      required
                      min={0}
                      max={120}
                    />
                  </div>
                  <div className="form-group">
                    <label>Sex *</label>
                    <select
                      value={newPatient.sex}
                      onChange={(e) => setNewPatient({ ...newPatient, sex: e.target.value })}
                      required
                    >
                      <option value="">Select</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                    </select>
                  </div>
                </div>
                <div className="form-group full-width">
                  <label>Medical History</label>
                  <textarea
                    value={newPatient.medical_history}
                    onChange={(e) => setNewPatient({ ...newPatient, medical_history: e.target.value })}
                    placeholder="Relevant medical conditions, surgeries, etc."
                    rows={3}
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Allergies</label>
                    <input
                      type="text"
                      value={newPatient.allergies}
                      onChange={(e) => setNewPatient({ ...newPatient, allergies: e.target.value })}
                      placeholder="Drug allergies, latex, etc."
                    />
                  </div>
                  <div className="form-group">
                    <label>Current Medications</label>
                    <input
                      type="text"
                      value={newPatient.medications}
                      onChange={(e) => setNewPatient({ ...newPatient, medications: e.target.value })}
                      placeholder="Current prescriptions"
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Previous Endoscopy</label>
                    <input
                      type="text"
                      value={newPatient.previous_endoscopy}
                      onChange={(e) => setNewPatient({ ...newPatient, previous_endoscopy: e.target.value })}
                      placeholder="Previous findings, dates"
                    />
                  </div>
                  <div className="form-group">
                    <label>Family History</label>
                    <input
                      type="text"
                      value={newPatient.family_history}
                      onChange={(e) => setNewPatient({ ...newPatient, family_history: e.target.value })}
                      placeholder="GI cancer, IBD, polyposis syndromes"
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  <Plus size={16} /> Create Patient
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;