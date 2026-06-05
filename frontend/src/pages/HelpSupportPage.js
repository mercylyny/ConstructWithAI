import React from "react";
import "../index.css";

const HelpSupportPage = () => {
  return (
    <div className="fade-in dash-page" style={{ maxWidth: "800px", margin: "0 auto" }}>
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Help & Support</h1>
          <p className="dash-subtitle">Learn how to use ConstructAI and get in touch if you need help.</p>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1rem" }}>Step-by-Step Guide</h2>
        <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
          Follow these simple steps to analyze your building blueprints and generate an accurate bill of quantities.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", position: "relative" }}>
          {/* Vertical line connecting steps */}
          <div style={{ position: "absolute", left: "19px", top: "10px", bottom: "10px", width: "2px", background: "var(--border)" }}></div>

          {/* Step 1 */}
          <div style={{ display: "flex", gap: "1rem", position: "relative", zIndex: 1 }}>
            <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: "var(--accent)", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", flexShrink: 0, boxShadow: "0 0 0 4px var(--surface)" }}>1</div>
            <div>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "0.4rem" }}>Upload Your Blueprint</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.5" }}>
                Navigate to the <strong>Analysis</strong> tab. Drag and drop your architectural floor plan (PDF, PNG, or JPG) into the upload area. Make sure to input the correct scale (e.g., 1:100) and standard wall thickness before clicking "Run AI Pipeline".
              </p>
            </div>
          </div>

          {/* Step 2 */}
          <div style={{ display: "flex", gap: "1rem", position: "relative", zIndex: 1 }}>
            <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: "var(--teal)", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", flexShrink: 0, boxShadow: "0 0 0 4px var(--surface)" }}>2</div>
            <div>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "0.4rem" }}>AI Analysis & Extraction</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.5" }}>
                The system will process your image. It detects walls, classifies them by type (Internal/External), and reads text (OCR) to identify room labels. You will see a summary of the extracted data once completed.
              </p>
            </div>
          </div>

          {/* Step 3 */}
          <div style={{ display: "flex", gap: "1rem", position: "relative", zIndex: 1 }}>
            <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: "#f59e0b", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", flexShrink: 0, boxShadow: "0 0 0 4px var(--surface)" }}>3</div>
            <div>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "0.4rem" }}>Review Estimations</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.5" }}>
                Head over to your <strong>Dashboard</strong>. Click on your newly processed project to expand it. Under the "Estimation" tab, you'll see a detailed breakdown of materials (bricks, cement, sand) and their projected costs.
              </p>
            </div>
          </div>

          {/* Step 4 */}
          <div style={{ display: "flex", gap: "1rem", position: "relative", zIndex: 1 }}>
            <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: "#10b981", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", flexShrink: 0, boxShadow: "0 0 0 4px var(--surface)" }}>4</div>
            <div>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "0.4rem" }}>Export BOQ</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.5" }}>
                In the Estimation tab, use the "Export PDF" or "Export Excel" buttons to download your finalized Bill of Quantities, ready to be shared with clients or contractors.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1rem" }}>Contact Support</h2>
        <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
          Having trouble? Our support team is available to help you with technical issues or feature requests.
        </p>

        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <a 
            href="mailto:mercylinenamara@gmail.com" 
            className="btn btn-primary"
            style={{ textDecoration: "none", display: "inline-flex", padding: "0.8rem 1.5rem", fontSize: "0.95rem" }}
          >
            ✉️ Email Support
          </a>
          
          <a 
            href="https://wa.me/256779877356" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn btn-teal"
            style={{ background: "#25D366", boxShadow: "0 4px 20px rgba(37,211,102,0.3)", textDecoration: "none", display: "inline-flex", padding: "0.8rem 1.5rem", fontSize: "0.95rem" }}
          >
            💬 WhatsApp Us
          </a>
        </div>
      </div>

    </div>
  );
};

export default HelpSupportPage;
