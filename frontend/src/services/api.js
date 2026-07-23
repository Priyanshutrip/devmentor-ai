import axios from "axios";

const API_BASE_URL = "http://localhost:8080/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Automatically attach JWT token to every request if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const registerUser = (username, email, password) =>
  api.post("/auth/register", { username, email, password });

export const loginUser = (username, password) =>
  api.post("/auth/login", { username, password });

export const askOrchestrator = (message) =>
  api.post("/agent/orchestrate", { message });

export default api;