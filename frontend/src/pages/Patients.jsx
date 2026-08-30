import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { fetchPatients, createPatient } from "../lib/api";


const Patients = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
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

  useEffect(() => {
    async function loadPatients() {
      const data = await fetchPatients();
      setPatients(data);
    }
    loadPatients();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    const data = await createPatient(newPatient);
    setPatients([...patients, data]);
  };

  return (
    <div className="patients-page">
      <h2>Patient Management</h2>

      <div className="card">
        <h3>Add New Patient</h3>
        <form onSubmit={handleCreate} style={{ marginBottom: "1rem", display: "grid", gap: "0.5rem" }}>
          <input
            placeholder="Full name"
            value={newPatient.full_name}
            onChange={(e) => setNewPatient({ ...newPatient, full_name: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Age"
            value={newPatient.age}
            onChange={(e) => setNewPatient({ ...newPatient, age: Number(e.target.value) })}
            required
          />
          <select value={newPatient.sex} onChange={(e) => setNewPatient({ ...newPatient, sex: e.target.value })} required>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
          <button type="submit">Create Patient</button>
        </form>
      </div>

      {patients.length === 0 && <p>No patients found.</p>}

      <ul>
        {patients.map((p) => (
          <li key={p.patient_ref} onClick={() => navigate(`/analyze?patient=${p.patient_ref}`)}>
            {p.full_name} ({p.age}) - {p.sex}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Patients;