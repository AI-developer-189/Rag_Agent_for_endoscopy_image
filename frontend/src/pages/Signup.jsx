import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { UserPlus, Mail, Lock, Eye, EyeOff, Shield } from "lucide-react";

const Signup = () => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signup } = useAuth();

  const validatePassword = (pwd) => {
    const checks = {
      length: pwd.length >= 8,
      uppercase: /[A-Z]/.test(pwd),
      lowercase: /[a-z]/.test(pwd),
      number: /[0-9]/.test(pwd),
      special: /[!@#$%^&*]/.test(pwd),
    };
    return checks;
  };

  const passwordChecks = validatePassword(password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!fullName.trim()) {
      setError("Full name is required.");
      return;
    }
    if (!passwordChecks.length) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (!passwordChecks.uppercase || !passwordChecks.lowercase || !passwordChecks.number) {
      setError("Password must contain uppercase, lowercase, and number.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await signup(fullName, email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <UserPlus size={32} style={{color: "var(--accent-color)"}} />
          </div>
          <h1>Create Account</h1>
          <p>Join Endoscopy CDSS Platform</p>
          <span className="badge">Clinician Access</span>
        </div>

        {error && <div className="error-toast">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <div className="input-wrapper">
              <Shield size={18} style={{color: "var(--accent-color)"}} />
              <input
                type="text"
                id="fullName"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. John Smith"
                required
                autoComplete="name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail size={18} />
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="doctor@hospital.com"
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock size={18} />
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-password"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <div className="password-strength">
              <div className="strength-bar">
                <div 
                  className="strength-fill" 
                  style={{ 
                    width: `${Object.values(passwordChecks).filter(Boolean).length * 20}%`,
                    backgroundColor: Object.values(passwordChecks).filter(Boolean).length < 3 
                      ? "var(--error-color)" 
                      : Object.values(passwordChecks).filter(Boolean).length < 5 
                        ? "var(--warning-color)" 
                        : "var(--success-color)"
                  }} 
                />
              </div>
              <div className="strength-requirements">
                <span className={passwordChecks.length ? "met" : "unmet"}>8+ chars</span>
                <span className={passwordChecks.uppercase ? "met" : "unmet"}>Uppercase</span>
                <span className={passwordChecks.lowercase ? "met" : "unmet"}>Lowercase</span>
                <span className={passwordChecks.number ? "met" : "unmet"}>Number</span>
                <span className={passwordChecks.special ? "met" : "unmet"}>Special</span>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <div className="input-wrapper">
              <Lock size={18} />
              <input
                type={showConfirmPassword ? "text" : "password"}
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="toggle-password"
              >
                {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {confirmPassword && confirmPassword !== password && (
              <span className="field-error">Passwords do not match</span>
            )}
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" />
                Creating Account...
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        <div className="auth-link">
          Already have an account?{" "}
          <Link to="/login">Sign In</Link>
        </div>

        <div className="demo-hint">
          <p>Your account will be ready for clinical use immediately.</p>
        </div>
      </div>
    </div>
  );
};

export default Signup;