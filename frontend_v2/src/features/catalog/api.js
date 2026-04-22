import api from '../../core/api';

export default {
  getCustomers() {
    return api.get('/customers');
  },
  getCustomerProducts(customerId) {
    return api.get(`/customers/${customerId}/products`);
  }
};
