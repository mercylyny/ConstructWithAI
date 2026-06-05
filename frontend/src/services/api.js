export const API_BASE = "http://localhost:8000";

// Helper to get the JWT auth headers
const getAuthHeaders = () => {
    const token = localStorage.getItem('build_ai_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export async function uploadPlan(file, scale) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("scale", scale);

    const response = await fetch(`${API_BASE}/upload/plan`, {
        method: "POST",
        headers: { ...getAuthHeaders() }, // no Content-Type for FormData
        body: formData,
    });

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            errorData = await response.text();
        }
        console.error("Backend error response:", errorData);
        throw Object.assign(new Error("Upload request failed"), { response: errorData });
    }

    return response.json();
}

export async function runOcr(filename) {
    const response = await fetch(`${API_BASE}/analyze/plan/ocr/images`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename }),
    });

    if (!response.ok) {
        throw new Error("OCR request failed");
    }

    return response.json();
}

export async function interpretOcr(filename) {
    const response = await fetch(`${API_BASE}/ai/interpret/ocr`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Interpretation request failed: ${errorText}`);
    }

    return response.json();
}

export async function estimateMaterials(wallSegments) {
    const response = await fetch(`${API_BASE}/ai/estimate/materials/detail`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(wallSegments),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Material estimation failed: ${errorText}`);
    }

    return response.json();
}

export async function estimateCosts(quantities, customRates = {}) {
    const payload = { quantities };
    if (customRates && Object.keys(customRates).length > 0) {
        payload.custom_rates = customRates;
    }

    const response = await fetch(`${API_BASE}/ai/estimate/costs`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Cost estimation failed: ${errorText}`);
    }

    return response.json();
}

export async function analyzePlan(filename, useQsFallbacks = true) {
    const response = await fetch(`${API_BASE}/pipeline/analyze-plan`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders(),
        },
        body: JSON.stringify({ 
            filename,
            use_qs_fallbacks: useQsFallbacks
        }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Plan analysis failed: ${errorText}`);
    }

    return response.json();
}

export async function estimatePlan(requestPayload) {
    const response = await fetch(`${API_BASE}/pipeline/estimate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders(),
        },
        body: JSON.stringify(requestPayload),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Estimation failed: ${errorText}`);
    }

    return response.json();
}

export async function fetchUserProjects() {
    const response = await fetch(`${API_BASE}/database/projects/`, {
        method: "GET",
        headers: { ...getAuthHeaders() },
    });
    if (!response.ok) throw new Error("Failed to load projects");
    return response.json();
}

export async function getPhases(filename) {
    const response = await fetch(`${API_BASE}/ai/estimate/phases`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Phase estimation failed: ${errorText}`);
    }

    return response.json();
}

export async function exportPhaseExcel(costResponse) {
    const response = await fetch(`${API_BASE}/export/boq/excel`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(costResponse),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`BOQ Excel export failed: ${errorText}`);
    }

    return response.blob();
}

export async function exportPhasePdf(costResponse) {
    const response = await fetch(`${API_BASE}/export/boq/pdf`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(costResponse),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`BOQ PDF export failed: ${errorText}`);
    }

    return response.blob();
}

async function handleResponse(response) {
    if (!response.ok) {
        let errorMessage = "An error occurred";
        try {
            const data = await response.json();
            errorMessage = data.detail || data.message || JSON.stringify(data);
        } catch (e) {
            try {
                errorMessage = await response.text();
            } catch (e2) {}
        }
        throw new Error(errorMessage);
    }
    return response.json();
}

export async function registerUser(name, email, password) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
    });
    return handleResponse(response);
}

export async function loginUser(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
}

export async function googleLoginUser(name, email) {
    const response = await fetch(`${API_BASE}/auth/google-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email }),
    });
    return handleResponse(response);
}

export async function requestPasswordReset(email) {
    const response = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
    });
    return handleResponse(response);
}

export async function confirmPasswordReset(email, token, newPassword) {
    const response = await fetch(`${API_BASE}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, token, new_password: newPassword }),
    });
    return handleResponse(response);
}