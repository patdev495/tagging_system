import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export default {
  getCustomers() {
    return api.get('/customers');
  },
  getCustomerProducts(customerId) {
    return api.get(`/customers/${customerId}/products`);
  },
  checkHealth() {
    return api.get('/health');
  },
  createCarton(data) {
    return api.post('/cartons', data);
  },
  getLastCarton(productId) {
    return api.get(`/products/${productId}/last-carton`);
  },
  updateCartonStatus(cartonId, status) {
    return api.patch(`/cartons/${cartonId}/status`, { status });
  },
  getNextSN(productId) {
    return api.get(`/products/${productId}/next-sn`);
  },
  searchCarton(sn) {
    return api.get('/cartons/search', { params: { carton_sn: sn } });
  },
  reprintCarton(cartonId, templatePath, printerName) {
    return api.post(`/cartons/${cartonId}/reprint`, null, { 
      params: { template_path: templatePath, printer_name: printerName }
    });
  }
};
