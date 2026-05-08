export interface Customer {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface Product {
  id: number;
  customer_id: number;
  item_name: string;
  upc?: string;
  packed_qty: number;
  start_part: string;
  middle_part: string;
  template_type: 'standard' | 'detailed';
  template_path?: string;
  allow_partial: number;
}

export interface Carton {
  id: number;
  carton_sn: string;
  product_sku: string;
  product_name: string;
  customer_name: string;
  packed_qty: number;
  created_at: string;
}

export interface ScanItem {
  sn: string;
  timestamp: string;
}

export interface PrintJobStatus {
  status: 'pending' | 'printing' | 'success' | 'failed';
  message: string;
  carton_sn?: string;
}
