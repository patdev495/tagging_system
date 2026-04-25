import api from '../../core/api';

export default {
  // Customers
  getCustomers() {
    return api.get('/customers');
  },
  createCustomer(data) {
    return api.post('/customers', data);
  },
  updateCustomer(id, data) {
    return api.put(`/customers/${id}`, data);
  },
  deleteCustomer(id) {
    return api.delete(`/customers/${id}`);
  },

  // Products
  getAllProducts() {
    return api.get('/products');
  },
  getCustomerProducts(customerId) {
    return api.get(`/customers/${customerId}/products`);
  },
  createProduct(data) {
    return api.post('/products', data);
  },
  updateProduct(id, data) {
    return api.put(`/products/${id}`, data);
  },
  deleteProduct(id) {
    return api.delete(`/products/${id}`);
  }
};
