import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { login as apiLogin, signup as apiSignup, getCurrentUser, logout as apiLogout } from "../lib/auth";

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const checkAuth = async () => {
    const token = localStorage.getItem("auth_token");

    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem("auth_token");
        setUser(null);
      } else {
        console.error("Authentication check failed:", error);
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email, password) => {
    const response = await apiLogin(email, password);
    localStorage.setItem("auth_token", response.access_token);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    navigate("/dashboard");
  };

  const signup = async (fullName, email, password) => {
    const response = await apiSignup(fullName, email, password);
    localStorage.setItem("auth_token", response.access_token);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    navigate("/dashboard");
  };

  const logout = async () => {
    await apiLogout();
    localStorage.removeItem("auth_token");
    setUser(null);
    navigate("/login");
  };

  const getToken = () => localStorage.getItem("auth_token");

  if (loading) {
    return <div>Loading auth...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
};