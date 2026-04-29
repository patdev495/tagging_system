import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.DEV 
    ? `http://${window.location.hostname}:8001/api/v1` 
    : '/api/v1',
});

export default api;
