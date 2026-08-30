import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async (e) => {
    e.preventDefault();
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="navbar">
      <Link to="/dashboard" className="navbar-brand">
        Endoscopy AI
      </Link>
      <div className="navbar-nav">
        {!user ? (
          <>
            <Link to="/login" className="nav-item">Login</Link>
            <Link to="/signup" className="nav-item">Sign up</Link>
          </>
        ) : (
          <>
            <Link to="/dashboard" className="nav-item">Dashboard</Link>
            <Link to="/patients" className="nav-item">Patients</Link>
            <Link to="/analyze" className="nav-item">Analyze</Link>
            <button
              onClick={handleLogout}
              className="nav-btn"
                style={{
                  padding: "0.5rem 1rem",
                  background: "none",
                  border: "1px solid var(--border-color)",
                  borderRadius: "4px",
                  color: "var(--error-color)",
                  fontSize: "0.875rem",
                }}
            >
              Logout
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default Navbar;