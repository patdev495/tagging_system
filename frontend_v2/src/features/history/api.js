import api from '../../core/api';

export default {
  getCartons(params = {}) {
    return api.get('/cartons', { params });
  },
  getCartonDetail(id) {
    return api.get(`/cartons/${id}`);
  },
  searchByCartonSN(sn) {
    return api.get('/cartons/search', { params: { carton_sn: sn } });
  },
  searchByItemSN(sn) {
    return api.get('/cartons/search/item', { params: { item_sn: sn } });
  },
  deleteCarton(id) {
    return api.delete(`/cartons/${id}`);
  }
};
