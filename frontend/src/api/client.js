import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API] Response ${response.status}`, response.data);
    }
    return response;
  },
  (error) => {
    const status = error.response?.status;
    const message = error.response?.data?.detail ?? error.message;
    console.error(`[API] Error ${status}:`, message);

    return Promise.reject({
      status,
      message,
      isTimeout: error.code === "ECONNABORTED",
      isNetwork: !error.response,
      isServer: status >= 500,
      isClient: status >= 400 && status < 500,
    });
  }
);

export default apiClient;

export async function verifyQuery(query, history = []) {
  if (!query?.trim()) {
    throw { status: 400, message: "Query cannot be empty", isClient: true };
  }

  const response = await apiClient.post("/verify", {
    query: query.trim(),
    history,
  });
  return response.data;
}

export async function checkHealth() {
  try {
    await apiClient.get("/health", { timeout: 3000 });
    return true;
  } catch {
    return false;
  }
}
