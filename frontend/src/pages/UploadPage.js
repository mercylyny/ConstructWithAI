import React, { useState } from "react";
import { uploadPlan, analyzePlan, estimatePlan, API_BASE } from "../services/api";

function UploadPage() {
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    // AI workflow state
    const [file, setFile] = useState(null);
    const [scale, setScale] = useState("1:100");
    const [isUploading, setIsUploading] = useState(false);
    const [filename, setFilename] = useState("");
    const [cloudinaryUrl, setCloudinaryUrl] = useState("");
    const [projectId, setProjectId] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [useQsFallbacks, setUseQsFallbacks] = useState(true);

    // Estimation state
    const [isEstimating, setIsEstimating] = useState(false);
    const [estimationResult, setEstimationResult] = useState(null);

    // Manual input (independent)
    const [manualSummary, setManualSummary] = useState({
        rooms: 0,
        bedrooms: 0,
        bathrooms: 0,
        kitchens: 0,
        walls: 0,
        doors: 0,
        windows: 0,
        columns: 0,
        beams: 0,
    });

    const formatCurrency = (value) => `UGX ${Number(value || 0).toLocaleString()}`;

    // AI handlers
    const handleUpload = async () => {
        if (!file) { setError("Select a file"); return; }
        setIsUploading(true); setError(""); setMessage(""); setAnalysisResult(null); setEstimationResult(null);
        try {
            const data = await uploadPlan(file, scale);
            if (data.filename) {
                setFilename(data.filename);
                if (data.url) setCloudinaryUrl(data.url);
                if (data.project_id) setProjectId(data.project_id);
                setMessage("Upload successful");
            }
        } catch (err) { setError(err.message || "Upload failed"); }
        finally { setIsUploading(false); }
    };

    const handleRunAnalysis = async () => {
        if (!filename) { setError("Upload a plan first"); return; }
        setIsAnalyzing(true); setError(""); setMessage(""); setEstimationResult(null);
        try {
            const data = await analyzePlan(filename, useQsFallbacks);
            setAnalysisResult(data); setMessage("Analysis complete");
        } catch (err) { setError(err.message || "Analysis failed"); }
        finally { setIsAnalyzing(false); }
    };

    const handleAIEstimation = async () => {
        if (!analysisResult || !analysisResult.summary) { setError("Run analysis first"); return; }
        setIsEstimating(true); setError(""); setMessage("");
        try {
            const data = await estimatePlan({ filename: analysisResult.filename, summary: analysisResult.summary, manual_mode: false, project_id: projectId });
            setEstimationResult(data); setMessage("Estimation complete");
        } catch (err) { setError(err.message || "Estimation failed"); }
        finally { setIsEstimating(false); }
    };

    // Manual handlers
    const handleManualInputChange = (e) => {
        const { name, value } = e.target;
        setManualSummary(prev => ({ ...prev, [name]: parseInt(value) || 0 }));
    };

    const handleManualEstimation = async () => {
        setIsEstimating(true); setError(""); setMessage(""); setEstimationResult(null);
        try {
            const data = await estimatePlan({ filename: null, summary: manualSummary, manual_mode: true });
            setEstimationResult(data); setMessage("Manual estimation complete");
        } catch (err) { setError(err.message || "Estimation failed"); }
        finally { setIsEstimating(false); }
    };

    const renderDownloadUrl = (path) => {
        if (!path) return <span style={{color: "var(--text-secondary)"}}>Not available</span>;
        
        // Ensure path uses forward slashes and extract the filename
        const normalizedPath = path.replace(/\\/g, '/');
        const name = normalizedPath.split("/").pop();
        
        // Encode the path to pass safely in the URL
        const downloadUrl = `${API_BASE}/pipeline/download?filepath=${encodeURIComponent(path)}`;
        
        return (
            <a href={downloadUrl} download style={{color: "var(--success-color)", fontWeight: 700, textDecoration: "underline", cursor: "pointer"}}>
                {name}
            </a>
        );
    };

    return (
        <div className="fade-in page-container" style={{ maxWidth: "900px", margin: "0 auto" }}>
            <h1 style={{ textAlign: "center", marginBottom: "1.5rem" }}>Construction Plan Analysis & Estimation</h1>

            {error && <div className="list-item" style={{ borderLeft: "4px solid var(--danger-color)", marginBottom: "1rem", color: "var(--danger-color)" }}>{error}</div>}
            {message && <div className="list-item" style={{ borderLeft: "4px solid var(--success-color)", marginBottom: "1rem", color: "var(--success-color)" }}>{message}</div>}

            {/* Section 1: Plan Upload */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>1. Plan Upload</h2>
                <div className="input-group" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <input type="file" onChange={(e) => setFile(e.target.files[0])} disabled={isUploading || isAnalyzing || isEstimating} />
                    <select value={scale} onChange={(e) => setScale(e.target.value)}>
                        <option>1:50</option>
                        <option>1:100</option>
                        <option>1:200</option>
                    </select>
                    <button className="btn btn-primary" onClick={handleUpload} disabled={isUploading}>{isUploading ? 'Uploading...' : 'Upload'}</button>
                </div>
                
                {cloudinaryUrl && (
                    <div style={{ marginTop: "1.5rem", padding: "1rem", backgroundColor: "rgba(255,255,255,0.05)", borderRadius: "8px", textAlign: "center" }}>
                        <h3 style={{ marginBottom: "1rem", fontSize: "1rem", color: "var(--text-secondary)" }}>Uploaded Document Preview</h3>
                        {cloudinaryUrl.toLowerCase().endsWith(".pdf") ? (
                            <a href={cloudinaryUrl} target="_blank" rel="noreferrer" className="btn btn-secondary">
                                📄 View Uploaded PDF
                            </a>
                        ) : (
                            <img src={cloudinaryUrl} alt="Uploaded Plan Preview" style={{ maxWidth: "100%", maxHeight: "400px", borderRadius: "4px", objectFit: "contain", border: "1px solid rgba(255,255,255,0.1)" }} />
                        )}
                    </div>
                )}
            </div>

            {/* Section 2: OCR Analysis */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>2. OCR Analysis</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Run AI analysis to extract building summary and measurements.</p>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <button className="btn btn-secondary" onClick={handleRunAnalysis} disabled={!filename || isAnalyzing}>{isAnalyzing ? 'Analyzing...' : 'Run Analysis'}</button>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.9rem' }}>
                        <input type="checkbox" checked={useQsFallbacks} onChange={(e) => setUseQsFallbacks(e.target.checked)} disabled={isAnalyzing} />
                        Auto-Infer Missing Elements (Recommended for Beginners)
                    </label>
                    <div style={{ marginLeft: 'auto' }}>{filename && <strong>Uploaded:</strong>} {filename}</div>
                </div>

                {analysisResult && analysisResult.summary && (
                    <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '1rem' }}>
                        {['rooms','bedrooms','kitchens','bathrooms','walls','doors','windows','columns','beams'].map((k) => (
                            <div key={k} className="list-item" style={{ textAlign: 'center' }}>
                                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{k.charAt(0).toUpperCase()+k.slice(1)}</div>
                                <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{analysisResult.summary[k] || 0}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Section 3: Full Estimation Pipeline */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>3. Full Estimation Pipeline</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Run the full pipeline (materials, costing, phases).</p>
                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button className="btn btn-primary" onClick={handleAIEstimation} disabled={!analysisResult || isEstimating}>{isEstimating ? 'Estimating...' : 'Run Pipeline'}</button>
                </div>
                {estimationResult && estimationResult.grand_total && (
                    <div style={{ marginTop: '1rem' }}>
                        <strong>Building Summary:</strong> Grand Total - {formatCurrency(estimationResult.grand_total)}
                    </div>
                )}
            </div>

            {/* Section 4: Material Estimation */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>4. Material Estimation</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Detailed materials per phase (Material, Quantity, Amount).</p>
                <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {estimationResult && estimationResult.stages && estimationResult.stages.length > 0 ? (
                        estimationResult.stages.map((stage, sidx) => (
                            <div key={sidx} className="list-item">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <strong>{stage.phase_name}</strong>
                                    <span style={{ fontWeight: 700 }}>{formatCurrency(stage.cost)}</span>
                                </div>
                                <div style={{ marginTop: '0.5rem' }}>
                                    {(stage.materials || []).length === 0 && <div style={{ color: 'var(--text-secondary)' }}>No detailed materials available for this phase.</div>}
                                    {(stage.materials || []).length > 0 && (
                                        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem' }}>
                                            <thead>
                                                <tr style={{ textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                                                    <th>Material</th>
                                                    <th>Quantity</th>
                                                    <th>Unit</th>
                                                    <th>Unit Rate</th>
                                                    <th>Amount</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {stage.materials.map((m, midx) => (
                                                    <tr key={midx}>
                                                        <td>{m.item}</td>
                                                        <td>{m.quantity}</td>
                                                        <td>{m.unit}</td>
                                                        <td>{formatCurrency(m.unit_rate)}</td>
                                                        <td>{formatCurrency(m.total_cost)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    )}
                                </div>
                            </div>
                        ))
                    ) : (
                        <div style={{ color: 'var(--text-secondary)' }}>No material estimation available yet.</div>
                    )}
                </div>
            </div>

            {/* Section 5: Project Cost Summary */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>5. Project Cost Summary</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {((estimationResult && estimationResult.stages) || []).map((st, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <div>{st.phase_name}</div>
                            <div style={{ fontWeight: 700 }}>{formatCurrency(st.cost)}</div>
                        </div>
                    ))}
                    <div style={{ height: '1px', background: 'rgba(255,255,255,0.04)', margin: '0.5rem 0' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(0,255,100,0.06)', padding: '0.5rem', borderRadius: '6px' }}>
                        <div style={{ fontWeight: 700 }}>Grand Total</div>
                        <div style={{ fontWeight: 900, color: 'var(--success-color)' }}>{formatCurrency(estimationResult ? estimationResult.grand_total : 0)}</div>
                    </div>
                </div>
            </div>

            {/* Section 6: Reports */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>6. Reports</h2>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <strong>Excel BOQ</strong>
                        {renderDownloadUrl(estimationResult && estimationResult.boq_excel_path)}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <strong>PDF BOQ</strong>
                        {renderDownloadUrl(estimationResult && estimationResult.boq_pdf_path)}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <strong>QS Report</strong>
                        {renderDownloadUrl(estimationResult && estimationResult.qs_report_path)}
                    </div>
                </div>
            </div>

            {/* Section 7: Manual Input (independent) */}
            <div className="card glass-panel" style={{ marginBottom: "1rem" }}>
                <h2>7. Manual Input</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Enter counts manually without uploading a file. This is isolated from the AI pipeline.</p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem', marginTop: '0.5rem' }}>
                    {Object.keys(manualSummary).map((k) => (
                        <div key={k} className="input-group">
                            <label className="input-label" style={{ textTransform: 'capitalize' }}>{k}</label>
                            <input type="number" name={k} value={manualSummary[k]} onChange={handleManualInputChange} className="input-field" min={0} />
                        </div>
                    ))}
                </div>
                <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                    <button className="btn btn-primary" onClick={handleManualEstimation} disabled={isEstimating}>{isEstimating ? 'Estimating...' : 'Run Manual Estimation'}</button>
                </div>
            </div>
        </div>
    );
}

export default UploadPage;