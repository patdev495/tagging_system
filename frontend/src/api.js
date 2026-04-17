import axios from 'axios';

const api = axios.create({
  baseURL: `http://${window.location.hostname}:8000`,
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
  }
};
