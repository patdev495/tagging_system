import api from '../../core/api';
import type { Carton } from '../../types/api';

export default {
  createCarton(data: { 
    product_id: number; 
    items: string[]; 
    job_order?: string; 
    slot_id?: number;
    custom_sn?: number; 
    carton_origin?: string;
    custom_yymm?: string;
  }) {
    return api.post<Carton>('/cartons', data);
  },
  getLastCarton(productId: number) {
    return api.get<Carton>(`/products/${productId}/last-carton`);
  },
  getNextSN(productId: number, yymm?: string) {
    return api.get<{ next_seq: number; next_sn?: string | null; prefix?: string }>(`/products/${productId}/next-sn`, { params: { yymm } });
  },
  rescanCarton(data: { carton_sn: string; items: string[] }) {
    return api.put<Carton>('/cartons/rescan', data);
  }
};
