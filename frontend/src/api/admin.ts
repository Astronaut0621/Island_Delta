import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8080',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor - attach JWT token for admin requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes('/api/admin/login');
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_username');
      localStorage.removeItem('admin_role');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

// ----- Auth -----
export const adminLogin = (data: { username: string; password: string }) =>
  api.post('/api/admin/login', data);

// ----- Posts -----
export const getAdminPosts = (params: {
  status?: string;
  emotionType?: string;
  startTime?: string;
  endTime?: string;
  page?: number;
  size?: number;
}) => api.get('/api/admin/posts', { params });

export const getAdminPost = (id: number) => api.get(`/api/admin/posts/${id}`);

export const hidePost = (id: number) => api.put(`/api/admin/posts/${id}/hide`);

export const restorePost = (id: number) => api.put(`/api/admin/posts/${id}/restore`);

export const deletePost = (id: number) => api.delete(`/api/admin/posts/${id}`);

// ----- Reports -----
export const getAdminReports = (params: {
  status?: string;
  page?: number;
  size?: number;
}) => api.get('/api/admin/reports', { params });

export const handleReport = (id: number) => api.put(`/api/admin/reports/${id}/handle`);

export const ignoreReport = (id: number) => api.put(`/api/admin/reports/${id}/ignore`);

// ----- Statistics -----
export const getAdminStatistics = () => api.get('/api/admin/statistics');

// ----- NLP Feedback -----
export const getNlpFeedback = (params: {
  userCorrected?: boolean;
  page?: number;
  size?: number;
}) => api.get('/api/admin/nlp-feedback', { params });

export const getNlpAcceptanceRate = () => api.get('/api/admin/nlp-feedback/acceptance-rate');

export default api;
