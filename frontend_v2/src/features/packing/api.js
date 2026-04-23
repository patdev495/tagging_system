import api from '../../core/api';

export default {
  createCarton(data) {
    return api.post('/cartons', data);
  },
  getLastCarton(productId) {
    return api.get(`/products/${productId}/last-carton`);
  },
  getNextSN(productId) {
    return api.get(`/products/${productId}/next-sn`);
  }
};
