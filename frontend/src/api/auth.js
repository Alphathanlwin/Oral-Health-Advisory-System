import axios from 'axios';

// Relative, not an absolute host:port — Vite's dev server proxies /api to the
// backend (see vite.config.js), so this works identically whether the page
// was opened via localhost or a phone on the LAN via the dev machine's IP.
const API_BASE_URL = '/api/v1';

const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ohas_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('ohas_token');
    }
    return Promise.reject(error);
  }
);

export const register = async (payload) => {
  const response = await authApi.post('/auth/register', payload);
  return response.data;
};

export const login = async (payload) => {
  const response = await authApi.post('/auth/login', payload);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await authApi.get('/users/me');
  return response.data;
};

export default authApi;
