import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    if (status === 401 && !error.config?.url?.includes("/api/auth/")) {
      localStorage.removeItem("auth_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const login = async (email, password) => {
  const res = await api.post("/api/auth/login", { email, password });
  return res.data;
};

export const signup = async (fullName, email, password) => {
  const res = await api.post("/api/auth/signup", { fullName, email, password });
  return res.data;
};

export const getCurrentUser = async () => {
  const res = await api.get("/api/auth/me");
  return res.data;
};

export const logout = async () => {
  await api.post("/api/auth/logout");
};

export const analyzeImage = async (image, patientRef) => {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("patient_ref", patientRef);
  const res = await api.post("/api/analyze", formData);
  return res.data;
};

export const fetchPatients = async () => {
  const res = await api.get("/api/patients");
  return res.data;
};

export const createPatient = async (patientData) => {
  const res = await api.post("/api/patients", patientData);
  return res.data;
};

export const deletePatient = async (patientId) => {
  const res = await api.delete(`/api/patients/${patientId}`);
  return res.data;
};

export const getPatientPredictions = async (patientId) => {
  const res = await api.get(`/api/patients/${patientId}/predictions`);
  return res.data;
};

export const downloadReport = async (studyId) => {
  const res = await api.get(`/api/reports/${studyId}`, {
    responseType: "blob",
  });
  return res.data;
};

export const getReport = async (reportId) => {
  const res = await api.get(`/api/reports/${reportId}`);
  return res.data;
};