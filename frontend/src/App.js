import React, { useState, useEffect, useRef } from "react";
import "./index.css";
import UploadPage    from "./pages/UploadPage";
import LoginPage     from "./pages/LoginPage";
import ServicesPage  from "./pages/ServicesPage";
import DashboardPage from "./pages/DashboardPage";
import SettingsPage  from "./pages/SettingsPage";
import HelpSupportPage from "./pages/HelpSupportPage";
import ProfilePage   from "./pages/ProfilePage";

// ─── Brand Logo SVG ────────────────────────────────────────────────────────────
const ConstructLogo = () => (
  <svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="34" height="34" rx="9" fill="url(#logoGrad)" />
    <path d="M8 17 L17 8 L26 17 L22 17 L22 26 L12 26 L12 17 Z" fill="white" opacity="0.9" />
    <path d="M14 26 L14 20 L20 20 L20 26" fill="url(#logoGrad2)" />
    <defs>
      <linearGradient id="logoGrad" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="#6366f1" />
        <stop offset="100%" stopColor="#8b5cf6" />
      </linearGradient>
      <linearGradient id="logoGrad2" x1="14" y1="20" x2="20" y2="26" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="#06b6d4" />
        <stop offset="100%" stopColor="#0891b2" />
      </linearGradient>
    </defs>
  </svg>
);

// ─── Notification Bell ─────────────────────────────────────────────────────────
const NotificationBell = () => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const fn = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", fn);
    return () => document.removeEventListener("mousedown", fn);
  }, []);

  const notifications = [
    { icon: "✅", title: "Analysis Complete", body: "Floor plan analysed successfully.", time: "2m ago", color: "#10b981" },
    { icon: "📊", title: "BOQ Generated",     body: "Excel & PDF exports are ready.",   time: "15m ago", color: "#a78bfa" },
    { icon: "🧱", title: "Estimation Done",   body: "Material quantities calculated.",  time: "1h ago",  color: "#06b6d4" },
  ];

  return (
    <div style={{ position: "relative" }} ref={ref}>
      <button className="nav-icon-btn" onClick={() => setOpen(o => !o)} title="Notifications">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        <span className="nav-notif-dot" />
      </button>

      {open && (
        <div className="nav-dropdown notif-dropdown">
          <div className="notif-header">
            <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>Notifications</span>
            <span className="notif-badge">3</span>
          </div>
          {notifications.map((n, i) => (
            <div key={i} className="notif-item">
              <div className="notif-icon" style={{ background: `${n.color}18`, color: n.color }}>{n.icon}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: "0.82rem" }}>{n.title}</div>
                <div style={{ color: "var(--text-secondary)", fontSize: "0.76rem", marginTop: "0.1rem" }}>{n.body}</div>
              </div>
              <div style={{ color: "var(--text-muted)", fontSize: "0.7rem", flexShrink: 0 }}>{n.time}</div>
            </div>
          ))}
          <div className="notif-footer">Mark all as read</div>
        </div>
      )}
    </div>
  );
};

// ─── Search Bar ────────────────────────────────────────────────────────────────
const NavSearch = ({ searchQuery, setSearchQuery, onSearchFocus }) => {
  const [focused, setFocused] = useState(false);
  return (
    <div className={`nav-search ${focused ? "nav-search--focused" : ""}`}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
      </svg>
      <input
        type="text"
        placeholder="Search projects..."
        className="nav-search-input"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        onFocus={() => { setFocused(true); onSearchFocus && onSearchFocus(); }}
        onBlur={() => setFocused(false)}
      />
    </div>
  );
};

// ─── Nav User Profile ──────────────────────────────────────────────────────────
const NavUserProfile = ({ onLogout, onNavigate }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const storedUser = (() => {
    try { return JSON.parse(localStorage.getItem("construct_ai_user") || "{}"); }
    catch { return {}; }
  })();

  const name = storedUser.name || "Namara Mercy";
  const email = storedUser.email || "";
  const initials = name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2) || "U";

  useEffect(() => {
    const fn = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", fn);
    return () => document.removeEventListener("mousedown", fn);
  }, []);

  const items = [
    { icon: "👤", label: "View Profile",        action: () => { setOpen(false); onNavigate("profile"); } },
    { icon: "⚙️",  label: "Settings",           action: () => { setOpen(false); onNavigate("settings"); } },
    { icon: "❓", label: "Help & Support",      action: () => { setOpen(false); onNavigate("help"); } },
    { divider: true },
    { icon: "🚪", label: "Sign Out",            action: () => { setOpen(false); onLogout(); }, danger: true },
  ];

  return (
    <div style={{ position: "relative" }} ref={ref}>
      <button className={`profile-trigger ${open ? "profile-trigger--open" : ""}`} onClick={() => setOpen(o => !o)}>
        <div className="profile-avatar-sm">{initials}</div>
        <div className="profile-trigger-info">
          <div className="profile-trigger-name">{name.split(" ")[0]} {name.split(" ")[1] || ""}</div>
        </div>
        <svg className={`profile-chevron ${open ? "profile-chevron--up" : ""}`} width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <div className="nav-dropdown profile-dropdown-menu" style={{ width: "220px" }}>
          <div className="profile-dropdown-header">
            <div className="profile-avatar-sm profile-avatar-lg">{initials}</div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: "0.88rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{name}</div>
              <div style={{ color: "var(--text-secondary)", fontSize: "0.72rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{email}</div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.3rem", marginTop: "0.2rem" }}>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#10b981", display: "inline-block" }} />
                <span style={{ fontSize: "0.68rem", color: "#10b981", fontWeight: 600 }}>Active</span>
              </div>
            </div>
          </div>
          <div className="profile-dropdown-divider" />
          {items.map((item, i) =>
            item.divider
              ? <div key={i} className="profile-dropdown-divider" />
              : (
                <button key={i} className={`profile-dropdown-item ${item.danger ? "profile-dropdown-item--danger" : ""}`} onClick={item.action}>
                  <span className="profile-dropdown-item-icon">{item.icon}</span>
                  {item.label}
                </button>
              )
          )}
        </div>
      )}
    </div>
  );
};

// ─── App ───────────────────────────────────────────────────────────────────────
function App() {
  const [currentPage, setCurrentPage]       = useState("login");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen]  = useState(false);
  const [searchQuery, setSearchQuery]        = useState("");

  useEffect(() => {
    const token = localStorage.getItem("construct_ai_token");
    if (token) { setIsAuthenticated(true); setCurrentPage("upload"); }
  }, []);

  const handleLogin = () => {
    localStorage.setItem("construct_ai_last_login", new Date().toISOString());
    setIsAuthenticated(true);
    setCurrentPage("upload");
  };

  const handleLogout = () => {
    localStorage.removeItem("construct_ai_token");
    localStorage.removeItem("construct_ai_user");
    setIsAuthenticated(false);
    setCurrentPage("login");
  };

  const navItems = [
    { key: "upload",    label: "Analysis",   icon: "⬡" },
    { key: "services",  label: "Services",   icon: "◈" },
    { key: "dashboard", label: "Dashboard",  icon: "▦" },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case "login":     return <LoginPage onLogin={handleLogin} />;
      case "services":  return <ServicesPage />;
      case "dashboard": return <DashboardPage onLogout={handleLogout} searchQuery={searchQuery} />;
      case "settings":  return <SettingsPage />;
      case "help":      return <HelpSupportPage />;
      case "profile":   return <ProfilePage />;
      case "upload":
      default:          return <UploadPage />;
    }
  };

  return (
    <div className="app-container">
      {/* ══════════════════ NAVBAR ══════════════════ */}
      <header className="navbar-enterprise">

        {/* LEFT — Brand */}
        <div
          className="nav-brand-enterprise"
          onClick={() => setCurrentPage(isAuthenticated ? "upload" : "login")}
        >
          <ConstructLogo />
          <div className="nav-brand-text-wrap">
            <span className="nav-brand-title">Construct<span>AI</span></span>
            <span className="nav-brand-sub">AI-Powered Building Analysis &amp; Estimation</span>
          </div>
        </div>

        {/* CENTER — Navigation tabs */}
        {isAuthenticated && (
          <nav className="nav-center-tabs">
            {navItems.map(({ key, label }) => (
              <button
                key={key}
                className={`nav-tab-enterprise ${currentPage === key ? "nav-tab-enterprise--active" : ""}`}
                onClick={() => { setCurrentPage(key); setMobileMenuOpen(false); }}
              >
                {label}
              </button>
            ))}
          </nav>
        )}

        {/* RIGHT — Actions */}
        {isAuthenticated ? (
          <div className="nav-right-actions">
            <NavSearch 
              searchQuery={searchQuery} 
              setSearchQuery={setSearchQuery} 
              onSearchFocus={() => setCurrentPage("dashboard")} 
            />
            <NotificationBell />
            <NavUserProfile onLogout={handleLogout} onNavigate={setCurrentPage} />
          </div>
        ) : (
          <div className="nav-right-actions">
            {currentPage !== "login" && (
              <button className="btn btn-primary" style={{ padding: "0.5rem 1.2rem", fontSize: "0.88rem" }} onClick={() => setCurrentPage("login")}>
                Sign In
              </button>
            )}
          </div>
        )}

        {/* Mobile hamburger */}
        {isAuthenticated && (
          <button className="nav-hamburger" onClick={() => setMobileMenuOpen(o => !o)}>
            <span /><span /><span />
          </button>
        )}

        {/* Mobile menu */}
        {isAuthenticated && mobileMenuOpen && (
          <div className="nav-mobile-menu">
            {navItems.map(({ key, label }) => (
              <button
                key={key}
                className={`nav-mobile-item ${currentPage === key ? "nav-mobile-item--active" : ""}`}
                onClick={() => { setCurrentPage(key); setMobileMenuOpen(false); }}
              >
                {label}
              </button>
            ))}
            <button className="nav-mobile-item nav-mobile-item--danger" onClick={handleLogout}>Sign Out</button>
          </div>
        )}
      </header>

      <main className="main-content">{renderPage()}</main>
    </div>
  );
}

export default App;