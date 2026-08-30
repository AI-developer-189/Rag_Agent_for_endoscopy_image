import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  withCredentials: true,
});

// Login user
export const login = async (email, password) => {
  const res = await api.post("/api/auth/login", { email, password });
  return res.data;
};

// Signup new user
export const signup = async (fullName, email, password, confirm_password) => {
  const res = await api.post("/api/auth/signup", { full_name: fullName, email, password, confirm_password });
  return res.data;
};

// Get current authenticated user
export const getCurrentUser = async () => {
  const token = getToken();
  if (!token) {
    return null;
  }
  const res = await api.get("/api/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 200) {
    return res.data;
  }
  if (res.status === 401) {
    removeToken();
    return null;
  }
  return null;
};

// Logout user
export const logout = async () => {
  await api.post("/api/auth/logout");
};

// Remove token from localStorage
export const removeToken = () => {
  localStorage.removeItem("auth_token");
};

// Get token
export const getToken = () => localStorage.getItem("auth_token");