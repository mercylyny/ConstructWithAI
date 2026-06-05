import React, { useState, useEffect, useCallback } from "react";
import { API_BASE, fetchUserProjects } from "../services/api";

// ─── Helpers ───────────────────────────────────────────────────────────────────
const fmt = (v) => `UGX ${Number(v || 0).toLocaleString()}`;

const latest = (arr) =>
  arr && arr.length > 0
    ? arr.reduce((a, b) => (new Date(a.created_at) > new Date(b.created_at) ? a : b))
    : null;

const WALL_COLORS = {
  EXTERNAL:         { bg: "rgba(99,102,241,0.14)",  color: "#818cf8", label: "External" },
  INTERNAL:         { bg: "rgba(16,185,129,0.14)",  color: "#34d399", label: "Internal" },
  LOAD_BEARING:     { bg: "rgba(245,158,11,0.14)",  color: "#fbbf24", label: "Load Bearing" },
  NON_LOAD_BEARING: { bg: "rgba(148,163,184,0.10)", color: "#94a3b8", label: "Non-Load Bearing" },
  RETAINING:        { bg: "rgba(239,68,68,0.14)",   color: "#f87171", label: "Retaining" },
  UNKNOWN:          { bg: "rgba(255,255,255,0.05)", color: "#64748b", label: "Unknown" },
};

const wStyle = (t) => WALL_COLORS[t] || WALL_COLORS.UNKNOWN;

// ─── Sub-components ────────────────────────────────────────────────────────────
const ConfBar = ({ value }) => {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 80 ? "#10b981" : pct >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
      <div style={{ flex: 1, height: "3px", borderRadius: "99px", background: "rgba(255,255,255,0.07)", overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: "99px", transition: "width 0.7s ease" }} />
      </div>
      <span style={{ fontSize: "0.7rem", color, fontWeight: 700, minWidth: "28px" }}>{pct}%</span>
    </div>
  );
};

const MiniStat = ({ icon, label, value, color }) => (
  <div className="dash-mini-stat">
    {icon && <div style={{ fontSize: "1.1rem" }}>{icon}</div>}
    <div style={{ color: "var(--text-secondary)", fontSize: "0.68rem", textTransform: "uppercase", letterSpacing: "0.5px" }}>{label}</div>
    <div style={{ fontWeight: 700, fontSize: "0.95rem", color: color || "var(--text-primary)" }}>{value}</div>
  </div>
);

const DownBtn = ({ path, label, icon }) => {
  if (!path) return null;
  const url = `${API_BASE}/pipeline/download?filepath=${encodeURIComponent(path)}`;
  return (
    <a href={url} download className="dash-download-btn">
      <span>{icon}</span> {label}
    </a>
  );
};

// ─── KPI Card ──────────────────────────────────────────────────────────────────
const KpiCard = ({ icon, label, value, sub, accent, trend }) => (
  <div className="kpi-card" style={{ "--kpi-accent": accent }}>
    <div className="kpi-card__icon" style={{ background: `${accent}18`, color: accent }}>{icon}</div>
    <div className="kpi-card__body">
      <div className="kpi-card__value">{value}</div>
      <div className="kpi-card__label">{label}</div>
      {sub && <div className="kpi-card__sub">{sub}</div>}
    </div>
    <div className="kpi-card__bar" style={{ background: `linear-gradient(90deg, ${accent}30, transparent)` }} />
  </div>
);

// ─── Building Summary Section ──────────────────────────────────────────────────
const BuildingSection = ({ summaries }) => {
  const s = latest(summaries);
  if (!s) return null;
  const items = [
    { k: "rooms",     icon: "🏠", label: "Rooms"     },
    { k: "bedrooms",  icon: "🛏️",  label: "Bedrooms"  },
    { k: "bathrooms", icon: "🚿", label: "Bathrooms"  },
    { k: "kitchens",  icon: "🍳", label: "Kitchens"   },
    { k: "walls",     icon: "🧱", label: "Walls"      },
    { k: "doors",     icon: "🚪", label: "Doors"      },
    { k: "windows",   icon: "🪟", label: "Windows"    },
    { k: "columns",   icon: "🏛️",  label: "Columns"   },
    { k: "beams",     icon: "📐", label: "Beams"      },
  ];
  return (
    <div className="proj-section">
      <div className="proj-section__head">
        <div className="proj-section__title">🏗️ Extracted Building Elements</div>
        {s.confidence > 0 && (
          <div className="proj-section__badge" style={{ color: s.confidence >= 0.8 ? "#10b981" : "#f59e0b", background: s.confidence >= 0.8 ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)", border: `1px solid ${s.confidence >= 0.8 ? "rgba(16,185,129,0.25)" : "rgba(245,158,11,0.25)"}` }}>
            {Math.round(s.confidence * 100)}% confidence
          </div>
        )}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(82px, 1fr))", gap: "0.55rem" }}>
        {items.map(({ k, icon, label }) => (
          <MiniStat key={k} label={label} value={s[k] || 0} icon={icon} />
        ))}
      </div>
    </div>
  );
};

// ─── Walls Section ─────────────────────────────────────────────────────────────
const WallsSection = ({ walls }) => {
  const [exp, setExp] = useState(false);
  if (!walls || walls.length === 0) return null;
  const shown = exp ? walls : walls.slice(0, 5);
  return (
    <div className="proj-section">
      <div className="proj-section__head">
        <div className="proj-section__title">🧱 Wall Analysis <span className="count-chip">{walls.length} walls</span></div>
        {walls.length > 5 && (
          <button className="proj-section__toggle" onClick={() => setExp(!exp)}>
            {exp ? "Collapse ↑" : `View all ${walls.length} ↓`}
          </button>
        )}
      </div>
      <div style={{ overflowX: "auto" }}>
        <table className="dash-table">
          <thead>
            <tr>
              {["Wall ID", "Length (m)", "Height (m)", "Thickness (mm)", "Openings (m²)", "Type", "Confidence", "Reasoning"].map(h => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {shown.map((w, i) => {
              const ws = wStyle(w.wall_type);
              return (
                <tr key={w.id} className={i % 2 === 0 ? "tr-even" : ""}>
                  <td style={{ fontWeight: 700, color: "#c4b5fd" }}>{w.wall_id}</td>
                  <td>{(w.length_m || 0).toFixed(2)}</td>
                  <td>{(w.height_m || 0).toFixed(2)}</td>
                  <td>{w.thickness_mm || "—"}</td>
                  <td>{(w.openings_area_m2 || 0).toFixed(2)}</td>
                  <td>
                    <span className="wall-type-badge" style={{ background: ws.bg, color: ws.color }}>{ws.label}</span>
                  </td>
                  <td style={{ minWidth: "90px" }}><ConfBar value={w.classification_confidence} /></td>
                  <td style={{ color: "var(--text-secondary)", fontSize: "0.75rem", maxWidth: "180px" }}>{w.reasoning || "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ─── Estimation Section ────────────────────────────────────────────────────────
const EstSection = ({ estimations }) => {
  const est = latest(estimations);
  if (!est) return null;
  const phaseColors = ["#818cf8", "#34d399", "#fbbf24", "#f87171", "#60a5fa", "#a78bfa", "#fb923c", "#4ade80"];
  const totalPhase  = est.phases?.reduce((s, p) => s + (p.cost || 0), 0) || 0;

  return (
    <div className="proj-section">
      <div className="proj-section__head">
        <div className="proj-section__title">📊 Estimation Breakdown</div>
        <div style={{ fontSize: "0.73rem", color: "var(--text-secondary)" }}>
          Generated {new Date(est.created_at).toLocaleString("en-UG", { dateStyle: "medium", timeStyle: "short" })}
        </div>
      </div>

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: "0.65rem", marginBottom: "1rem" }}>
        <MiniStat icon="🧱" label="Total Bricks"    value={(est.total_bricks || 0).toLocaleString()} color="#fbbf24" />
        <MiniStat icon="🪣" label="Mortar Volume"   value={`${(est.total_mortar_volume || 0).toFixed(2)} m³`} color="#60a5fa" />
        <MiniStat icon="💰" label="Masonry Cost"    value={fmt(est.total_cost)} color="#34d399" />
        <MiniStat icon="🏆" label="Grand Total"     value={fmt(est.grand_total || est.total_cost)} color="#a78bfa" />
      </div>

      {/* Phase bars */}
      {est.phases && est.phases.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "0.85rem" }}>
          {est.phases.map((ph, i) => {
            const pct = totalPhase > 0 ? (ph.cost / totalPhase) * 100 : 0;
            const color = phaseColors[i % phaseColors.length];
            return (
              <div key={ph.id} className="phase-row">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: color, flexShrink: 0 }} />
                    <span style={{ fontWeight: 600, fontSize: "0.82rem" }}>{ph.phase_name}</span>
                  </div>
                  <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>{pct.toFixed(1)}%</span>
                    <span style={{ fontWeight: 700, fontSize: "0.82rem", color }}>{fmt(ph.cost)}</span>
                  </div>
                </div>
                <div style={{ height: "3px", borderRadius: "99px", background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                  <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: "99px", transition: "width 0.9s ease" }} />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Grand total bar */}
      <div className="grand-total-row">
        <span style={{ fontWeight: 700 }}>Grand Total (All Phases)</span>
        <span style={{ fontWeight: 900, fontSize: "1.1rem", color: "#10b981" }}>{fmt(est.grand_total || est.total_cost)}</span>
      </div>

      {/* Downloads */}
      <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", marginTop: "0.85rem" }}>
        <DownBtn path={est.boq_excel_path} label="Download Excel BOQ" icon="📥" />
        <DownBtn path={est.boq_pdf_path}   label="Download PDF BOQ"   icon="📄" />
      </div>
    </div>
  );
};

// ─── Main Dashboard ────────────────────────────────────────────────────────────
const DashboardPage = ({ onLogout, searchQuery = "" }) => {
  const [projects, setProjects]       = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState("");
  const [expanded, setExpanded]       = useState({});
  const [activeTab, setActiveTab]     = useState({});   // { [id]: "overview"|"walls"|"estimate" }

  const fetchProjects = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const data = await fetchUserProjects();
      setProjects(data);
      if (data.length > 0) setExpanded({ [data[0].id]: true });
    } catch (err) {
      setError(err.message || "Could not load projects");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  const toggle  = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  const getTab  = (id) => activeTab[id] || "overview";
  const setTab  = (id, tab) => setActiveTab(prev => ({ ...prev, [id]: tab }));

  // ─── KPI aggregates ───────────────────────────────────────────────────────
  const totalProjects   = projects.length;
  const totalWalls      = projects.reduce((s, p) => s + (p.walls?.length || 0), 0);
  const totalValue      = projects.reduce((s, p) => {
    const e = latest(p.estimations);
    return s + (e ? (e.grand_total || e.total_cost || 0) : 0);
  }, 0);
  const totalBOQ = projects.filter(p => {
    const e = latest(p.estimations);
    return e && (e.boq_excel_path || e.boq_pdf_path);
  }).length;

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-UG", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  const filteredProjects = projects.filter(p => 
    p.filename?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    p.id?.toString().includes(searchQuery)
  );

  return (
    <div className="fade-in dash-page">

      {/* ── Page Header ── */}
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Project Dashboard</h1>
          <p className="dash-subtitle">Monitor building analysis, material estimation, cost estimation and BOQ generation.</p>
        </div>
        <div className="dash-header-actions">
          <div className="dash-date-chip">📅 {dateStr}</div>
          <button className="btn btn-secondary dash-refresh-btn" onClick={fetchProjects} disabled={loading}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ transition: "transform 0.6s ease", transform: loading ? "rotate(360deg)" : "rotate(0deg)" }}>
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
            </svg>
            {loading ? "Refreshing…" : "Refresh"}
          </button>
        </div>
      </div>

      {/* ── KPI Cards ── */}
      <div className="kpi-grid">
        <KpiCard icon="📁" label="Total Projects"    value={totalProjects}          sub="Uploaded blueprints"      accent="#8b5cf6" />
        <KpiCard icon="🧱" label="Walls Analysed"   value={totalWalls.toLocaleString()} sub="Across all projects"   accent="#06b6d4" />
        <KpiCard icon="💰" label="Total Est. Value"  value={fmt(totalValue)}        sub="Grand total all projects"  accent="#10b981" />
        <KpiCard icon="📄" label="BOQ Exports"       value={totalBOQ}              sub="Excel &amp; PDF ready"     accent="#f59e0b" />
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="dash-error-bar">
          <span>⚠</span> {error}
          <button onClick={fetchProjects} style={{ marginLeft: "auto", background: "none", border: "none", color: "#f87171", cursor: "pointer", fontSize: "0.82rem", fontWeight: 600 }}>Retry</button>
        </div>
      )}

      {/* ── Loading ── */}
      {loading && projects.length === 0 && (
        <div className="dash-loading">
          <div className="dash-spinner" />
          <div>Loading your projects…</div>
        </div>
      )}

      {/* ── Empty ── */}
      {!loading && projects.length === 0 && (
        <div className="dash-empty">
          <div style={{ fontSize: "3.5rem", marginBottom: "1rem" }}>📋</div>
          <h2 style={{ marginBottom: "0.5rem", fontSize: "1.4rem" }}>No Projects Yet</h2>
          <p style={{ color: "var(--text-secondary)", maxWidth: "400px", margin: "0 auto" }}>
            Upload a construction plan and run the AI estimation pipeline to see your projects here.
          </p>
        </div>
      )}

      {/* ── Projects List ── */}
      {projects.length > 0 && (
        <div>
          <div className="section-head">
            <h2 className="section-title">
              Projects <span className="count-chip">{projects.length}</span>
              {searchQuery && <span style={{fontSize: "0.9rem", color: "var(--text-secondary)", fontWeight: "normal", marginLeft: "1rem"}}> (Filtered: {filteredProjects.length})</span>}
            </h2>
            <span style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>Click a project to expand details</span>
          </div>

          <div className="proj-list">
            {filteredProjects.length === 0 ? (
              <div className="dash-empty" style={{ padding: "3rem", background: "rgba(255,255,255,0.02)", borderRadius: "12px", border: "1px dashed rgba(255,255,255,0.1)" }}>
                <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🔍</div>
                <h3 style={{ fontSize: "1.1rem", marginBottom: "0.2rem" }}>No projects match your search</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>Try adjusting your search terms.</p>
              </div>
            ) : (
              filteredProjects.map((proj) => {
                const isOpen    = !!expanded[proj.id];
                const tab       = getTab(proj.id);
                const latestEst = latest(proj.estimations);
                const hasWalls  = proj.walls && proj.walls.length > 0;
                const hasSummary = proj.building_summaries && proj.building_summaries.length > 0;
                const hasEst    = proj.estimations && proj.estimations.length > 0;

                // Derived status
                const status = hasEst ? "Completed" : hasSummary ? "Analysed" : "Uploaded";
                const statusColor = hasEst ? "#10b981" : hasSummary ? "#06b6d4" : "#94a3b8";
                const statusBg    = hasEst ? "rgba(16,185,129,0.1)" : hasSummary ? "rgba(6,182,212,0.1)" : "rgba(148,163,184,0.1)";

                return (
                  <div key={proj.id} className={`proj-card ${isOpen ? "proj-card--open" : ""}`}>

                    {/* ── Card Header ── */}
                    <div className="proj-card__header" onClick={() => toggle(proj.id)}>
                      <div className="proj-card__icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                        </svg>
                      </div>

                      <div className="proj-card__info">
                        <div className="proj-card__name">{proj.filename}</div>
                        <div className="proj-card__meta">
                          <span>Scale: {proj.scale}</span>
                          <span className="dot-sep">·</span>
                          <span>Uploaded {new Date(proj.created_at).toLocaleDateString("en-UG", { year: "numeric", month: "short", day: "numeric" })}</span>
                        </div>
                      </div>

                      <div className="proj-card__stats">
                        <div className="proj-stat">
                          <div className="proj-stat__val">{proj.walls?.length || 0}</div>
                          <div className="proj-stat__lbl">Walls</div>
                        </div>
                        <div className="proj-stat">
                          <div className="proj-stat__val">{proj.estimations?.length || 0}</div>
                          <div className="proj-stat__lbl">Estimates</div>
                        </div>
                        {latestEst && (
                          <div className="proj-stat">
                            <div className="proj-stat__val" style={{ color: "#10b981", fontSize: "0.82rem" }}>{fmt(latestEst.grand_total || latestEst.total_cost)}</div>
                            <div className="proj-stat__lbl">Grand Total</div>
                          </div>
                        )}
                      </div>

                      <div className="proj-card__right">
                      <span className="status-pill" style={{ color: statusColor, background: statusBg, border: `1px solid ${statusColor}30` }}>
                        <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: statusColor, display: "inline-block", flexShrink: 0 }} />
                        {status}
                      </span>
                      <svg
                        className="proj-chevron"
                        style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0deg)" }}
                        width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                      >
                        <polyline points="6 9 12 15 18 9" />
                      </svg>
                    </div>
                  </div>

                  {/* ── Expanded Body ── */}
                  {isOpen && (
                    <div className="proj-card__body">

                      {/* Tabs */}
                      <div className="proj-tabs">
                        {[
                          { key: "overview",  label: "📋 Overview"   },
                          hasWalls && { key: "walls",    label: "🧱 Walls"      },
                          hasEst   && { key: "estimate", label: "📊 Estimation" },
                        ].filter(Boolean).map(({ key, label }) => (
                          <button
                            key={key}
                            className={`proj-tab ${tab === key ? "proj-tab--active" : ""}`}
                            onClick={() => setTab(proj.id, key)}
                          >
                            {label}
                          </button>
                        ))}
                      </div>

                      {/* Tab Content */}
                      <div className="proj-tab-content">
                        {tab === "overview" && (
                          <>
                            {hasSummary
                              ? <BuildingSection summaries={proj.building_summaries} />
                              : (
                                <div className="proj-empty-tab">
                                  <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🏗️</div>
                                  <div>No building analysis data yet.</div>
                                  <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "0.3rem" }}>Run the AI pipeline to extract building elements.</div>
                                </div>
                              )
                            }
                          </>
                        )}
                        {tab === "walls" && <WallsSection walls={proj.walls} />}
                        {tab === "estimate" && <EstSection estimations={proj.estimations} />}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardPage;
