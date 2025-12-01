import axios from 'axios';
import keycloak from '../auth/keycloakConfig';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // File service base URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication token
apiClient.interceptors.request.use(
  (config) => {
    // Add token to request if authenticated
    if (keycloak.authenticated && keycloak.token) {
      config.headers.Authorization = `Bearer ${keycloak.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // If token expired, try to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Refresh token
        const refreshed = await keycloak.updateToken(5);
        if (refreshed) {
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${keycloak.token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        keycloak.login();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// RAG service client
export const ragClient = axios.create({
  baseURL: 'http://localhost:8002', // RAG service base URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add same interceptors to RAG client
ragClient.interceptors.request.use(
  (config) => {
    if (keycloak.authenticated && keycloak.token) {
      config.headers.Authorization = `Bearer ${keycloak.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

ragClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshed = await keycloak.updateToken(5);
        if (refreshed) {
          originalRequest.headers.Authorization = `Bearer ${keycloak.token}`;
          return ragClient(originalRequest);
        }
      } catch (refreshError) {
        keycloak.login();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
