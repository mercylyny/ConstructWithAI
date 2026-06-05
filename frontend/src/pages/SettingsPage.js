import React, { useState, useEffect } from "react";
import "../index.css";

const SettingsPage = () => {
  const [theme, setTheme] = useState(localStorage.getItem("build_ai_theme") || "dark");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (theme === "light") {
      document.body.classList.add("light-theme");
    } else {
      document.body.classList.remove("light-theme");
    }
    localStorage.setItem("build_ai_theme", theme);
  }, [theme]);

  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setMessage("New passwords do not match.");
      return;
    }
    // Simulation
    setMessage("Password successfully updated! (Simulated)");
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
  };

  const toggle2FA = () => {
    setTwoFactorEnabled(!twoFactorEnabled);
    setMessage(`Two-Factor Authentication has been ${!twoFactorEnabled ? "enabled" : "disabled"}.`);
  };

  return (
    <div className="fade-in dash-page" style={{ maxWidth: "800px", margin: "0 auto" }}>
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Settings</h1>
          <p className="dash-subtitle">Manage your application preferences and security.</p>
        </div>
      </div>

      {message && (
        <div className="dash-error-bar" style={{ background: "rgba(16,185,129,0.1)", borderColor: "#10b981", color: "#10b981" }}>
          <span>✅</span> {message}
        </div>
      )}

      {/* Preferences Section */}
      <div className="card">
        <h2 style={{ fontSize: "1.2rem", marginBottom: "1.5rem" }}>Preferences</h2>
        
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem", borderBottom: "1px solid var(--border)" }}>
          <div>
            <div style={{ fontWeight: 600 }}>Theme Mode</div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Toggle between Dark and Light mode.</div>
          </div>
          <button 
            className="btn btn-secondary" 
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            style={{ minWidth: "120px" }}
          >
            {theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "1rem" }}>
          <div>
            <div style={{ fontWeight: 600 }}>Currency</div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Preferred currency for estimations.</div>
          </div>
          <select className="input-field" style={{ width: "120px" }} defaultValue="UGX">
            <option value="UGX">UGX</option>
            <option value="USD">USD</option>
            <option value="KES">KES</option>
          </select>
        </div>
      </div>

      {/* Security Section */}
      <div className="card">
        <h2 style={{ fontSize: "1.2rem", marginBottom: "1.5rem" }}>Security</h2>

        {/* 2FA Toggle */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1.5rem", borderBottom: "1px solid var(--border)", marginBottom: "1.5rem" }}>
          <div>
            <div style={{ fontWeight: 600 }}>Two-Factor Authentication (2FA)</div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", maxWidth: "400px" }}>Add an extra layer of security to your account by requiring a code from your mobile device upon login.</div>
          </div>
          <button 
            className={`btn ${twoFactorEnabled ? "btn-danger" : "btn-primary"}`} 
            onClick={toggle2FA}
          >
            {twoFactorEnabled ? "Disable 2FA" : "Enable 2FA"}
          </button>
        </div>

        {/* Change Password */}
        <div>
          <div style={{ fontWeight: 600, marginBottom: "1rem" }}>Change Password</div>
          <form onSubmit={handlePasswordChange}>
            <div className="input-group">
              <label className="input-label">Current Password</label>
              <input 
                type="password" 
                className="input-field" 
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <div className="input-group">
                <label className="input-label">New Password</label>
                <input 
                  type="password" 
                  className="input-field" 
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <label className="input-label">Confirm New Password</label>
                <input 
                  type="password" 
                  className="input-field" 
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: "0.5rem" }}>
              Update Password
            </button>
          </form>
        </div>
      </div>

    </div>
  );
};

export default SettingsPage;
