import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const client = axios.create({ baseURL: API_BASE_URL });

// --- Jobs ---

export const getJobs = (source, page = 1) =>
  client.get("/jobs", { params: { source, page } }).then((res) => res.data);

export const getJobSources = () =>
  client.get("/jobs/sources").then((res) => res.data);

export const getJobById = (id) =>
  client.get(`/jobs/${id}`).then((res) => res.data);

// --- Resume ---

export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return client
    .post("/resume/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((res) => res.data);
};

// --- Chat ---

export const sendChatMessage = (payload) =>
  client.post("/chat", payload).then((res) => res.data);

export default client;