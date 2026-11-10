import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getLanguages = () => api.get('/languages');
export const analyseThread = (payload) => api.post('/analyse', payload);
export const getSmartReply = (payload) => api.post('/reply', payload);
export const runCoach = (payload) => api.post('/coach', payload);

export default api;