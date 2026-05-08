import api from '../../core/api';
import type { Carton } from '../../types/api';

export default {
  createCarton(data: { 
    product_id: number; 
    items: string[]; 
    job_order?: string; 
    custom_sn?: number; 
    carton_origin?: string;
    custom_yymm?: string;
  }) {
    return api.post<Carton>('/cartons', data);
  },
  getLastCarton(productId: number) {
    return api.get<Carton>(`/products/${productId}/last-carton`);
  },
  getNextSN(productId: number) {
    return api.get<{ next_sn: string }>(`/products/${productId}/next-sn`);
  },
  rescanCarton(data: { carton_sn: string; items: string[] }) {
    return api.put<Carton>('/cartons/rescan', data);
  }
};
