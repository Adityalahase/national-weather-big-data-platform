import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("admin-token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getEvents = async () => {
  const response = await api.get("/api/events");
  return response.data;
};

// Get public analytics
export const getAnalytics = async () => {
  const response = await api.get("/api/analytics");
  return response.data;
};

// Get pipeline status
export const getPipelineStatus = async () => {
  const response = await api.get("/api/pipeline/status");
  return response.data;
};

// Admin Auth
export const loginAdmin = async (username, password) => {
  const response = await api.post("/auth/login", { username, password });
  return response.data;
};

// Admin Events
export const getAdminEvents = async () => {
  const response = await api.get("/api/admin/events");
  return response.data;
};

export const updateVerificationStatusApi = async (eventId, verificationStatus) => {
  const response = await api.patch(`/api/admin/events/${eventId}/verify`, {
    verification_status: verificationStatus,
  });
  return response.data;
};

export const getAdminStatistics = async () => {
  const response = await api.get("/api/admin/statistics");
  return response.data;
};

export default api;