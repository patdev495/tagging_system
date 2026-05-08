import api from '../../core/api';
import type { Customer, Product } from '../../types/api';

export default {
  // Customers
  getCustomers() {
    return api.get<Customer[]>('/customers');
  },
  createCustomer(data: Partial<Customer>) {
    return api.post<Customer>('/customers', data);
  },
  updateCustomer(id: number, data: Partial<Customer>) {
    return api.put<Customer>(`/customers/${id}`, data);
  },
  deleteCustomer(id: number) {
    return api.delete(`/customers/${id}`);
  },

  // Products
  getAllProducts() {
    return api.get<Product[]>('/products');
  },
  getCustomerProducts(customerId: number) {
    return api.get<Product[]>(`/customers/${customerId}/products`);
  },
  createProduct(data: Partial<Product>) {
    return api.post<Product>('/products', data);
  },
  updateProduct(id: number, data: Partial<Product>) {
    return api.put<Product>(`/products/${id}`, data);
  },
  deleteProduct(id: number) {
    return api.delete(`/products/${id}`);
  }
};
