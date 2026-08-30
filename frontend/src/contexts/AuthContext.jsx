import React, { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, signup as apiSignup, getCurrentUser } from "../lib/api";

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
    } catch {
      localStorage.removeItem("auth_token");
      setUser(null);
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
    setUser(response.user);
    return response.user;
  };

  const signup = async (fullName, email, password) => {
    const response = await apiSignup(fullName, email, password);
    localStorage.setItem("auth_token", response.access_token);
    setUser(response.user);
    return response.user;
  };

  const logout = async () => {
    localStorage.removeItem("auth_token");
    setUser(null);
  };

  const getToken = () => localStorage.getItem("auth_token");

  if (loading) {
    return <div className="auth-loading">Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, signup, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
};
