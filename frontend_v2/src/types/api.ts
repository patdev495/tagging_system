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
  status?: string;
  job_order?: string;
  station_id?: string;
  carton_origin?: string;
  is_reprint?: boolean;
  product?: Product;
  items?: { id: number; item_sn: string }[];
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

export interface JobOrderSlot {
  id: number;
  box_number: number;
  carton_sn: string;
  status: 'PENDING' | 'SCANNED';
  scanned_at?: string;
  carton_id?: number;
}

export interface JobOrderDetails {
  job_order: string;
  total_qty: number;
  total_boxes: number;
  product: Product;
  slots: JobOrderSlot[];
}

