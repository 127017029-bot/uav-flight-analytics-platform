/**
 * @file Axios API client instance for the UAV Digital Twin Platform.
 *
 * - Reads base URL from `VITE_API_URL` env var (defaults to localhost:8000).
 * - Attaches JWT token from localStorage on every request.
 * - Intercepts 401 responses to clear auth state and redirect to login.
 * - Normalises error payloads so consumers always receive a consistent shape.
 */

import axios from 'axios';

const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) return envUrl;
  // Dynamic fallback to production Railway backend when deploying on Vercel
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://uav-flight-analytics-platform-production.up.railway.app/api';
  }
  return 'http://localhost:8000/api';
};

/** Base Axios instance */
const client = axios.create({
  baseURL: getBaseURL(),
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/* ------------------------------------------------------------------ */
/*  Request interceptor – attach JWT                                  */
/* ------------------------------------------------------------------ */
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('uav_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

/* ------------------------------------------------------------------ */
/*  Response interceptor – normalise errors & handle 401              */
/* ------------------------------------------------------------------ */
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // Unauthorized – clear token & bounce to login
      if (status === 401) {
        localStorage.removeItem('uav_token');
        localStorage.removeItem('uav_user');
        // Only redirect if we're not already on a public route
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login';
        }
      }

      // Standardised error shape
      return Promise.reject({
        status,
        message: data?.detail || data?.message || 'Something went wrong',
        errors: data?.errors || null,
      });
    }

    // Network / timeout errors
    return Promise.reject({
      status: 0,
      message: error.message || 'Network error — please check your connection',
      errors: null,
    });
  },
);

export default client;
