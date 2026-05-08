import axios, { type AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.DEV 
    ? `http://${window.location.hostname}:8001/api/v1` 
    : '/api/v1',
});

export default api;
