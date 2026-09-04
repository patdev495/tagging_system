import api from '../../core/api';

export interface KPIStats {
  total_cartons: number;
  success_cartons: number;
  failed_cartons: number;
  reprint_cartons: number;
  total_items: number;
  success_rate: number;
  error_rate: number;
  reprint_rate: number;
}

export interface HourlyStat {
  hour: string;
  total: number;
  success: number;
  failed: number;
}

export interface ProductStat {
  item_name: string;
  customer_code: string;
  count: number;
  percentage: number;
}

export interface LiveCartonFeed {
  id: number;
  carton_sn: string;
  item_name: string;
  customer_code: string;
  created_at: string;
  status: string;
  is_reprint: number;
  weight: number | null;
  station_id: string | null;
  items_count: number;
}

export interface SystemHealth {
  bartender_status: 'ready' | 'offline';
  active_printers_count: number;
}

export interface DashboardStatsResponse {
  time_range: string;
  kpis: KPIStats;
  hourly_throughput: HourlyStat[];
  top_products: ProductStat[];
  live_feed: LiveCartonFeed[];
  system: SystemHealth;
}

export async function fetchDashboardStats(
  timeRange: 'today' | '7d' | '30d' = 'today'
): Promise<DashboardStatsResponse> {
  const response = await api.get<DashboardStatsResponse>('/admin/dashboard/stats', {
    params: { time_range: timeRange },
  });
  return response.data;
}
