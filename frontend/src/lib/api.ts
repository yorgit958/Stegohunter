import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("auth-storage");
        if (token) {
            try {
                const parsed = JSON.parse(token);
                if (parsed?.state?.token) {
                    config.headers.Authorization = `Bearer ${parsed.state.token}`;
                }
            } catch (e) {
                console.error("Could not parse auth token from local storage", e);
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle 401s globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Auto-logout if token is expired or invalid
            // localStorage.removeItem('auth-storage');
            // window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Scan API Endpoints
export const scanApi = {
    // Upload image for analysis
    uploadImage: async (file: File) => {
        const formData = new FormData();
        formData.append("file", file);
        
        const response = await api.post("/scan", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
        return response.data;
    },

    // Get a specific scan job's details and results
    getJob: async (jobId: string) => {
        const response = await api.get(`/scan/jobs/${jobId}`);
        return response.data;
    },

    // Get scan history for the logged-in user
    getJobs: async (limit: number = 20, offset: number = 0) => {
        const response = await api.get(`/scan/jobs?limit=${limit}&offset=${offset}`);
        return response.data;
    },

    // Get aggregated statistics for the dashboard
    getStats: async () => {
        const response = await api.get("/scan/stats");
        return response.data;
    },
    
    neutralizeImage: async (file: File, analysisResults: any, forceStrategies?: string[]) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("analysis_results", JSON.stringify(analysisResults));
        
        if (forceStrategies && forceStrategies.length > 0) {
            formData.append("force_strategies", forceStrategies.join(","));
        }
        
        const response = await api.post("/neutralize", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
        return response.data;
    },

    extractPayload: async (file: File) => {
        const formData = new FormData();
        formData.append("file", file);
        
        const response = await api.post("/scan/extract", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
        return response.data;
    },

    downloadImage: async (jobId: string) => {
        const response = await api.get(`/scan/jobs/${jobId}/download`, {
            responseType: 'blob'
        });
        return response.data;
    },

    scanDnnModel: async (file: File) => {
        const formData = new FormData();
        formData.append("file", file);
        
        // DNN models can take up to 30 seconds to parse and return
        const response = await api.post("/dnn/scan", formData, {
            timeout: 300000, // 5 minute timeout for massive files
        });
        return response.data;
    }
};

// Admin API Endpoints
export const adminApi = {
    getSystemStats: async () => {
        const response = await api.get("/admin/stats");
        return response.data;
    },
    getUsers: async () => {
        const response = await api.get("/admin/users");
        return response.data;
    },
    getServiceHealth: async () => {
        const response = await api.get("/admin/health");
        return response.data;
    },
    getRecentScans: async (limit: number = 10) => {
        const response = await api.get(`/admin/recent-scans?limit=${limit}`);
        return response.data;
    },
    getAuditLog: async () => {
        const response = await api.get("/admin/audit-log");
        return response.data;
    },
    updateUserRole: async (targetUserId: string, newRole: string) => {
        const response = await api.patch("/admin/users/role", {
            target_user_id: targetUserId,
            new_role: newRole,
        });
        return response.data;
    },
};
