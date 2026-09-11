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
  start_part?: string;
  middle_part?: string;
  template_type: 'standard' | 'detailed' | 'a11' | 'a11_tem2';
  template_path?: string;
  allow_partial: number;
  packing_mode?: 'item_scan' | 'weight_scale';
  target_weight?: number;
  min_weight?: number;
  max_weight?: number;
  weight_unit?: string;
  mfr_pn?: string;
  pkg_prefix?: string;
  revision?: string;
  factory_pn?: string;
  asin?: string;
  product_desc?: string;
  customer?: Customer;
}

export interface Carton {
  id: number;
  carton_sn: string;
  product_sku?: string;
  product_name?: string;
  customer_name?: string;
  packed_qty?: number;
  created_at: string;
  status?: string;
  job_order?: string;
  station_id?: string;
  carton_origin?: string;
  is_reprint?: boolean | number;
  product?: Product;
  items?: { id: number; item_sn: string }[];
  weight?: number;
  po_number?: string;
  lot_number?: string;
  date_code?: string;
  btxml?: string;
}

export interface ScaleReading {
  weight: number;
  weight_str?: string;
  unit: string;
  is_stable: boolean;
  is_tare?: boolean;
  is_net?: boolean;
  is_zero?: boolean;
  is_hold?: boolean;
  connected?: boolean;
  is_streaming?: boolean;
  timestamp?: number;
}


export interface ScaleStatus {
  connected: boolean;
  port: string;
  baudrate: number;
  is_streaming: boolean;
  mock_mode?: boolean;
}

export interface CartonWeighPackPayload {
  product_id: number;
  weight: number;
  po_number?: string;
  lot_number?: string;
  printer_name?: string;
  template_path?: string;
  station_id?: string;
  carton_origin?: string;
  custom_sn?: number;
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
  carton_number: number;
  carton_sn: string;
  status: 'PENDING' | 'SCANNED';
  scanned_at?: string;
  carton_id?: number;
}

export interface JobOrderDetails {
  job_order: string;
  total_qty: number;
  total_cartons: number;
  product: Product;
  slots: JobOrderSlot[];
}


