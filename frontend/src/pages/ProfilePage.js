import React, { useState } from "react";
import "../index.css";

const ProfilePage = () => {
  const loadUser = () => {
    try { return JSON.parse(localStorage.getItem("construct_ai_user") || "{}"); }
    catch { return {}; }
  };

  const storedUser = loadUser();

  const [isEditing, setIsEditing] = useState(false);
  const [saved, setSaved] = useState(false);

  const [form, setForm] = useState({
    name:     storedUser.name     || "Namara Mercy",
    email:    storedUser.email    || "mercylinenamara@gmail.com",
    role:     storedUser.role     || "Architect / Estimator",
    timezone: storedUser.timezone || "East Africa Time (EAT)",
    phone:    storedUser.phone    || "",
    company:  storedUser.company  || "",
  });

  const [draft, setDraft] = useState({ ...form });

  const initials = form.name.split(" ").map(w => w[0]).filter(Boolean).join("").toUpperCase().slice(0, 2) || "U";

  const handleChange = (field, value) => {
    setDraft(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    setForm({ ...draft });
    // Persist to localStorage so the navbar also reflects the new name
    const updated = { ...loadUser(), name: draft.name, email: draft.email, role: draft.role, timezone: draft.timezone, phone: draft.phone, company: draft.company };
    localStorage.setItem("construct_ai_user", JSON.stringify(updated));
    setIsEditing(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleCancel = () => {
    setDraft({ ...form });
    setIsEditing(false);
  };

  const memberSince = storedUser.created_at
    ? new Date(storedUser.created_at).toLocaleDateString("en-UG", { month: "long", year: "numeric" })
    : "June 2026";

  return (
    <div className="fade-in dash-page" style={{ maxWidth: "800px", margin: "0 auto" }}>
      <div className="dash-header">
        <div>
          <h1 className="dash-title">My Profile</h1>
          <p className="dash-subtitle">View and manage your personal account details.</p>
        </div>
      </div>

      {/* Success toast */}
      {saved && (
        <div className="dash-error-bar" style={{ background: "rgba(16,185,129,0.1)", borderColor: "#10b981", color: "#10b981", marginBottom: "1.5rem" }}>
          <span>✅</span> Profile updated successfully!
        </div>
      )}

      {/* Profile Header Card */}
      <div className="card" style={{ display: "flex", gap: "2rem", alignItems: "center", padding: "2rem" }}>
        <div style={{
          width: "100px", height: "100px", borderRadius: "50%",
          background: "linear-gradient(135deg, var(--accent), var(--teal))",
          color: "white", fontSize: "2.5rem", fontWeight: "bold",
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0, boxShadow: "0 8px 32px rgba(139,92,246,0.3)",
          transition: "all 0.3s",
        }}>
          {initials}
        </div>

        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: "1.8rem", marginBottom: "0.2rem", background: "none", WebkitTextFillColor: "var(--text-primary)" }}>
            {form.name}
          </h2>
          <div style={{ color: "var(--text-secondary)", marginBottom: "1rem" }}>{form.email}</div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem", background: "rgba(16,185,129,0.1)", color: "#10b981", padding: "0.3rem 0.8rem", borderRadius: "99px", fontSize: "0.85rem", fontWeight: "600" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981", display: "inline-block" }}></span>
            Active Member
          </div>
        </div>

        <div>
          {!isEditing ? (
            <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
              ✏️ Edit Profile
            </button>
          ) : (
            <button className="btn btn-secondary" onClick={handleCancel}>
              ✕ Cancel
            </button>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="kpi-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div className="kpi-card" style={{ padding: "1.5rem" }}>
          <div className="kpi-card__label" style={{ marginBottom: "0.5rem" }}>Account Created</div>
          <div className="kpi-card__value">{memberSince}</div>
          <div className="kpi-card__sub">Joined the ConstructAI platform</div>
          <div className="kpi-card__bar" style={{ background: "linear-gradient(90deg, rgba(139,92,246,0.3), transparent)" }}></div>
        </div>

        <div className="kpi-card" style={{ padding: "1.5rem" }}>
          <div className="kpi-card__label" style={{ marginBottom: "0.5rem" }}>Account Type</div>
          <div className="kpi-card__value" style={{ fontSize: "1.2rem" }}>{form.role}</div>
          <div className="kpi-card__sub">Professional plan</div>
          <div className="kpi-card__bar" style={{ background: "linear-gradient(90deg, rgba(6,182,212,0.3), transparent)" }}></div>
        </div>
      </div>

      {/* Personal Information Form */}
      <div className="card">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.5rem" }}>
          <h3 style={{ fontSize: "1.2rem" }}>Personal Information</h3>
          {isEditing && (
            <span style={{ fontSize: "0.82rem", color: "var(--accent)", fontWeight: 600 }}>
              ✏️ Editing mode — make your changes below
            </span>
          )}
        </div>

        <form onSubmit={handleSave}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Full Name</label>
              <input
                type="text"
                className="input-field"
                value={isEditing ? draft.name : form.name}
                onChange={e => handleChange("name", e.target.value)}
                readOnly={!isEditing}
                style={{ opacity: isEditing ? 1 : 0.75, cursor: isEditing ? "text" : "default" }}
                required
              />
            </div>

            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Email Address</label>
              <input
                type="email"
                className="input-field"
                value={isEditing ? draft.email : form.email}
                onChange={e => handleChange("email", e.target.value)}
                readOnly={!isEditing}
                style={{ opacity: isEditing ? 1 : 0.75, cursor: isEditing ? "text" : "default" }}
                required
              />
            </div>

            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Role / Profession</label>
              <input
                type="text"
                className="input-field"
                value={isEditing ? draft.role : form.role}
                onChange={e => handleChange("role", e.target.value)}
                readOnly={!isEditing}
                style={{ opacity: isEditing ? 1 : 0.75, cursor: isEditing ? "text" : "default" }}
              />
            </div>

            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Phone Number</label>
              <input
                type="tel"
                className="input-field"
                value={isEditing ? draft.phone : form.phone}
                onChange={e => handleChange("phone", e.target.value)}
                readOnly={!isEditing}
                placeholder={isEditing ? "e.g. +256 779 877 356" : "Not set"}
                style={{ opacity: isEditing ? 1 : 0.75, cursor: isEditing ? "text" : "default" }}
              />
            </div>

            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Company / Organization</label>
              <input
                type="text"
                className="input-field"
                value={isEditing ? draft.company : form.company}
                onChange={e => handleChange("company", e.target.value)}
                readOnly={!isEditing}
                placeholder={isEditing ? "e.g. ConstructAI Ltd" : "Not set"}
                style={{ opacity: isEditing ? 1 : 0.75, cursor: isEditing ? "text" : "default" }}
              />
            </div>

            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Timezone</label>
              {isEditing ? (
                <select
                  className="input-field"
                  value={draft.timezone}
                  onChange={e => handleChange("timezone", e.target.value)}
                >
                  <option value="East Africa Time (EAT)">East Africa Time (EAT) — UTC+3</option>
                  <option value="West Africa Time (WAT)">West Africa Time (WAT) — UTC+1</option>
                  <option value="Central Africa Time (CAT)">Central Africa Time (CAT) — UTC+2</option>
                  <option value="Greenwich Mean Time (GMT)">Greenwich Mean Time (GMT) — UTC+0</option>
                  <option value="India Standard Time (IST)">India Standard Time (IST) — UTC+5:30</option>
                  <option value="Eastern Time (ET)">Eastern Time (ET) — UTC-5</option>
                </select>
              ) : (
                <input
                  type="text"
                  className="input-field"
                  value={form.timezone}
                  readOnly
                  style={{ opacity: 0.75, cursor: "default" }}
                />
              )}
            </div>
          </div>

          {isEditing && (
            <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.75rem" }}>
              <button type="submit" className="btn btn-primary">
                💾 Save Changes
              </button>
              <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                Discard
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
