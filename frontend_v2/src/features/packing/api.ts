import api from '../../core/api';
import type { Carton } from '../../types/api';

export default {
  createCarton(data: { product_id: number; packed_qty: number; scanned_items: string[] }) {
    return api.post<Carton>('/cartons', data);
  },
  getLastCarton(productId: number) {
    return api.get<Carton>(`/products/${productId}/last-carton`);
  },
  getNextSN(productId: number) {
    return api.get<{ next_sn: string }>(`/products/${productId}/next-sn`);
  },
  rescanCarton(data: { carton_id: number; scanned_items: string[] }) {
    return api.put<Carton>('/cartons/rescan', data);
  }
};
