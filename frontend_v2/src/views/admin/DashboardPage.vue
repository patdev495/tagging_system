<template>
  <div class="p-6 md:p-8 space-y-6 max-w-7xl mx-auto animate-in">
    <!-- Header Toolbar -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">Bảng Điều Khiển Vận Hành</h1>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Thời Gian Thực
          </span>
        </div>
        <p class="text-sm text-slate-500 mt-1">Giám sát sản lượng đóng thùng, hiệu suất từng giờ và luồng dữ liệu trạm in.</p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Time Range Selector -->
        <div class="inline-flex p-1 bg-slate-100 rounded-xl border border-slate-200 text-xs font-semibold">
          <button
            v-for="tab in timeRanges" :key="tab.value"
            @click="setTimeRange(tab.value)"
            :class="['px-3 py-1.5 rounded-lg transition-all', selectedRange === tab.value ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-600 hover:text-slate-900']"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Refresh Button -->
        <button
          @click="loadData" :disabled="isLoading"
          class="inline-flex items-center gap-2 px-3.5 py-1.5 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-all shadow-sm active:scale-95 disabled:opacity-50"
        >
          <RefreshCw :class="['w-4 h-4 text-slate-500', isLoading ? 'animate-spin text-indigo-600' : '']" />
          <span>{{ isLoading ? 'Đang tải...' : 'Làm mới' }}</span>
        </button>

        <!-- Last Updated Badge -->
        <div v-if="lastUpdated" class="text-xs text-slate-400">
          Cập nhật: <span class="font-mono text-slate-600 font-medium">{{ lastUpdated }}</span>
        </div>
      </div>
    </div>

    <!-- KPI Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <!-- Card 1: Total Cartons -->
      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Tổng Thùng Đã Đóng</p>
            <p class="text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">{{ formatNumber(stats.kpis.total_cartons) }}</p>
          </div>
          <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100"><PackageCheck class="w-6 h-6" /></div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <span class="text-slate-500">Thành công: <strong class="text-emerald-600">{{ formatNumber(stats.kpis.success_cartons) }}</strong></span>
          <span class="px-2 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700">{{ stats.kpis.success_rate }}%</span>
        </div>
      </div>

      <!-- Card 2: Packed Items -->
      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Sản Phẩm Con Đã Đóng</p>
            <p class="text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">{{ formatNumber(stats.kpis.total_items) }}</p>
          </div>
          <div class="p-3 bg-blue-50 text-blue-600 rounded-xl border border-blue-100"><Layers class="w-6 h-6" /></div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Trung bình / thùng:</span>
          <strong class="text-blue-600">{{ stats.kpis.total_cartons > 0 ? (stats.kpis.total_items / stats.kpis.total_cartons).toFixed(1) : '0' }} sp</strong>
        </div>
      </div>

      <!-- Card 3: Reprints -->
      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Số Lần In Lại Tem</p>
            <p class="text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">{{ formatNumber(stats.kpis.reprint_cartons) }}</p>
          </div>
          <div class="p-3 bg-amber-50 text-amber-600 rounded-xl border border-amber-100"><Printer class="w-6 h-6" /></div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <span class="text-slate-500">Tỷ lệ in lại:</span>
          <span :class="['px-2 py-0.5 rounded-full font-bold', stats.kpis.reprint_rate > 5 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700']">{{ stats.kpis.reprint_rate }}%</span>
        </div>
      </div>

      <!-- Card 4: System Status -->
      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Trạng Thái Hệ Thống</p>
            <div class="flex items-center gap-2 mt-2">
              <span :class="['w-3 h-3 rounded-full', stats.system.bartender_status === 'ready' ? 'bg-emerald-500' : 'bg-rose-500']"></span>
              <p class="text-xl font-bold text-slate-900">{{ stats.system.bartender_status === 'ready' ? 'BarTender Sẵn Sàng' : 'BarTender Ngoại Tuyến' }}</p>
            </div>
          </div>
          <div class="p-3 bg-purple-50 text-purple-600 rounded-xl border border-purple-100"><Server class="w-6 h-6" /></div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Máy in kết nối:</span>
          <strong class="text-purple-700 font-semibold">{{ stats.system.active_printers_count }} máy in</strong>
        </div>
      </div>
    </div>

    <!-- Middle Section: Charts & Top Products -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Hourly Throughput Chart (8 cols) -->
      <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">{{ selectedRange === 'today' ? 'Sản Lượng Theo Khung Giờ (Hôm Nay)' : 'Sản Lượng Theo Ngày' }}</h2>
            <p class="text-xs text-slate-400">Phân bổ số lượng thùng quét và in theo thời gian thực</p>
          </div>
          <div class="flex items-center gap-4 text-xs font-medium">
            <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-emerald-500"></span><span class="text-slate-600">Thành công</span></div>
            <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-rose-500"></span><span class="text-slate-600">Thất bại</span></div>
          </div>
        </div>

        <!-- SVG Bar Chart -->
        <div class="w-full mt-2 pt-4">
          <div v-if="stats.hourly_throughput.length === 0" class="py-16 text-center text-slate-400 text-sm">Chưa có dữ liệu sản lượng trong khung thời gian này.</div>
          <div v-else class="w-full overflow-x-auto">
            <div class="min-w-[500px]">
              <!-- Bars Area -->
              <div class="h-44 flex items-end gap-1.5 sm:gap-2 px-2 border-b border-slate-200">
                <div v-for="(item, idx) in stats.hourly_throughput" :key="idx" class="flex-1 flex flex-col items-center justify-end h-full group relative">
                  <!-- Tooltip with item count ("con") and carton count ("thùng") -->
                  <div class="absolute -top-16 z-30 opacity-0 group-hover:opacity-100 transition-all pointer-events-none bg-slate-900/95 text-white text-[11px] rounded-xl px-3 py-2 shadow-xl whitespace-nowrap border border-slate-700/50 backdrop-blur-xs flex flex-col gap-0.5">
                    <div class="flex items-center justify-between gap-3 border-b border-slate-700 pb-1">
                      <span class="font-bold text-indigo-300 font-mono">{{ item.hour }}</span>
                      <span class="px-1.5 py-0.2 rounded bg-indigo-500/30 text-indigo-200 font-bold font-mono">{{ formatNumber(item.total_items) }} con</span>
                    </div>
                    <div class="flex items-center gap-2 pt-0.5 text-slate-300">
                      <span>Tổng: <strong>{{ formatNumber(item.total) }}</strong> thùng</span>
                      <span class="text-emerald-400 font-medium">({{ formatNumber(item.success) }} OK)</span>
                      <span v-if="item.failed > 0" class="text-rose-400 font-medium">({{ formatNumber(item.failed) }} Lỗi)</span>
                    </div>
                  </div>
                  <!-- Stacked Bar -->
                  <div class="w-full max-w-[28px] flex flex-col justify-end items-center rounded-t-md overflow-hidden transition-all duration-300 group-hover:opacity-90">
                    <div v-if="item.failed > 0" class="w-full bg-rose-500 transition-all duration-300" :style="{ height: getBarHeight(item.failed) + 'px' }"></div>
                    <div v-if="item.success > 0" class="w-full bg-emerald-500 transition-all duration-300" :style="{ height: getBarHeight(item.success) + 'px' }"></div>
                    <div v-if="item.total === 0" class="w-full h-1 bg-slate-100 rounded-t"></div>
                  </div>
                </div>
              </div>
              <!-- Labels Area -->
              <div class="flex gap-1.5 sm:gap-2 px-2 pt-2">
                <div v-for="(item, idx) in stats.hourly_throughput" :key="idx" class="flex-1 text-center">
                  <span class="text-[10px] font-mono text-slate-400 block truncate">{{ item.hour }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Products Distribution (4 cols) -->
      <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col">
        <h2 class="text-base font-bold text-slate-900">Top Sản Phẩm Đóng Gói</h2>
        <p class="text-xs text-slate-400 mt-0.5">Xếp hạng theo sản lượng thùng (chỉ vào để xem chi tiết)</p>

        <div class="mt-4 flex-1 flex flex-col justify-center space-y-4">
          <div v-if="stats.top_products.length === 0" class="py-12 text-center text-slate-400 text-sm">Chưa có sản phẩm nào được đóng gói.</div>
          <div v-for="(prod, idx) in stats.top_products" :key="idx" class="space-y-1.5 group relative cursor-pointer p-1.5 -mx-1.5 rounded-xl hover:bg-slate-50 transition-colors">
            <!-- Hover Card: Full Product Information -->
            <div :class="['absolute left-0 w-72 z-30 opacity-0 group-hover:opacity-100 transition-all pointer-events-none bg-slate-900 text-white rounded-xl p-3.5 shadow-2xl border border-slate-700 text-xs', idx === 0 ? 'top-full mt-2' : 'bottom-full mb-2']">
              <p class="font-bold text-white text-sm leading-snug break-words">{{ prod.item_name }}</p>
              <div class="mt-2 space-y-1.5 text-slate-300 border-t border-slate-700/80 pt-2 text-[11px]">
                <div class="flex justify-between">
                  <span class="text-slate-400">Khách hàng:</span>
                  <span class="font-semibold text-white">{{ prod.customer_code }} <span v-if="prod.customer_name">({{ prod.customer_name }})</span></span>
                </div>
                <div v-if="prod.upc" class="flex justify-between">
                  <span class="text-slate-400">Mã UPC:</span>
                  <span class="font-mono text-indigo-300">{{ prod.upc }}</span>
                </div>
                <div v-if="prod.packed_qty" class="flex justify-between">
                  <span class="text-slate-400">Quy cách:</span>
                  <span class="text-white">{{ prod.packed_qty }} con / thùng</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Sản lượng:</span>
                  <span class="font-bold text-emerald-400">{{ formatNumber(prod.count) }} thùng <span class="text-slate-300 font-normal">({{ formatNumber(prod.total_items) }} con)</span></span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Tỷ trọng:</span>
                  <span class="font-bold text-indigo-300">{{ prod.percentage }}% tổng sản lượng</span>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2 truncate pr-2">
                <span class="w-4 text-center font-bold text-slate-400">{{ idx + 1 }}</span>
                <span class="font-medium text-slate-800 truncate">{{ prod.item_name }}</span>
                <span class="px-1.5 py-0.2 bg-slate-100 text-slate-500 rounded text-[10px] uppercase font-mono shrink-0">{{ prod.customer_code }}</span>
              </div>
              <span class="font-semibold text-slate-700 shrink-0">
                {{ formatNumber(prod.count) }} <span class="text-slate-400 font-normal">({{ prod.percentage }}%)</span>
              </span>
            </div>
            <!-- Progress Bar -->
            <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-500" :style="{ width: `${prod.percentage}%` }"></div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Live Activity Feed Table -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></div>
          <div>
            <h2 class="text-base font-bold text-slate-900">Luồng Đóng Gói Trực Tiếp</h2>
            <p class="text-xs text-slate-400">15 thùng mới nhất vừa được quét hoặc in từ các trạm</p>
          </div>
        </div>
        <span class="text-xs font-medium text-slate-500">Hiển thị {{ stats.live_feed.length }} bản ghi</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-semibold border-b border-slate-100">
            <tr>
              <th class="py-3.5 px-4">Mã Thùng (SN)</th>
              <th class="py-3.5 px-4">Khách Hàng</th>
              <th class="py-3.5 px-4">Sản Phẩm</th>
              <th class="py-3.5 px-4 text-center">Trọng Lượng</th>
              <th class="py-3.5 px-4 text-center">Số S/N Con</th>
              <th class="py-3.5 px-4 text-center">Trạm In</th>
              <th class="py-3.5 px-4">Thời Gian</th>
              <th class="py-3.5 px-4 text-center">Loại In</th>
              <th class="py-3.5 px-4 text-center">Trạng Thái</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="stats.live_feed.length === 0">
              <td colspan="9" class="py-12 text-center text-slate-400 text-sm">Chưa có thùng nào được đóng trong hệ thống.</td>
            </tr>
            <tr v-for="carton in stats.live_feed" :key="carton.id" class="hover:bg-slate-50/80 transition-colors">
              <td class="py-3.5 px-4 font-mono font-bold text-indigo-700">{{ carton.carton_sn }}</td>
              <td class="py-3.5 px-4"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs font-semibold">{{ carton.customer_code }}</span></td>
              <td class="py-3.5 px-4 font-medium text-slate-800">{{ carton.item_name }}</td>
              <td class="py-3.5 px-4 text-center font-mono text-slate-600">{{ carton.weight != null ? carton.weight.toFixed(2) + ' kg' : '—' }}</td>
              <td class="py-3.5 px-4 text-center font-mono">
                <span class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-bold">{{ carton.items_count }}</span>
              </td>
              <td class="py-3.5 px-4 text-center text-xs font-mono text-slate-500">{{ carton.station_id || '—' }}</td>
              <td class="py-3.5 px-4 text-xs text-slate-500 whitespace-nowrap">{{ formatDateTime(carton.created_at) }}</td>
              <td class="py-3.5 px-4 text-center">
                <span v-if="carton.is_reprint === 1" class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200">In Lại</span>
                <span v-else class="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600">Gốc</span>
              </td>
              <td class="py-3.5 px-4 text-center">
                <span :class="['px-2.5 py-0.5 rounded-full text-xs font-bold inline-flex items-center gap-1', carton.status === 'SUCCESS' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200']">
                  <span :class="['w-1.5 h-1.5 rounded-full', carton.status === 'SUCCESS' ? 'bg-emerald-500' : 'bg-rose-500']"></span>
                  {{ carton.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { PackageCheck, Layers, Printer, Server, RefreshCw } from 'lucide-vue-next';
import { fetchDashboardStats, type DashboardStatsResponse } from '../../features/dashboard/api';

const timeRanges: { label: string; value: 'today' | '7d' | '30d' }[] = [
  { label: 'Hôm Nay', value: 'today' },
  { label: '7 Ngày Qua', value: '7d' },
  { label: '30 Ngày Qua', value: '30d' },
];

const selectedRange = ref<'today' | '7d' | '30d'>('today');
const isLoading = ref<boolean>(false);
const lastUpdated = ref<string>('');
let autoRefreshTimer: number | null = null;

const stats = ref<DashboardStatsResponse>({
  time_range: 'today',
  kpis: {
    total_cartons: 0, success_cartons: 0, failed_cartons: 0, reprint_cartons: 0,
    total_items: 0, success_rate: 0, error_rate: 0, reprint_rate: 0,
  },
  hourly_throughput: [],
  top_products: [],
  live_feed: [],
  system: { bartender_status: 'offline', active_printers_count: 0 },
});

const maxHourlyTotal = computed(() => {
  const values = stats.value.hourly_throughput.map((item) => item.total);
  const max = Math.max(...values, 0);
  return max > 0 ? max : 1;
});

function getBarHeight(val: number): number {
  if (val <= 0) return 0;
  return Math.max(Math.round((val / maxHourlyTotal.value) * 160), 4);
}

function formatNumber(num: number): string {
  return (num || 0).toLocaleString('vi-VN');
}

function formatDateTime(dtStr: string): string {
  if (!dtStr) return '—';
  const d = new Date(dtStr);
  return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
    ' ' + d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

async function loadData() {
  isLoading.value = true;
  try {
    const data = await fetchDashboardStats(selectedRange.value);
    stats.value = data;
    lastUpdated.value = new Date().toLocaleTimeString('vi-VN');
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
  } finally {
    isLoading.value = false;
  }
}

function setTimeRange(range: 'today' | '7d' | '30d') {
  selectedRange.value = range;
  loadData();
}

onMounted(() => {
  loadData();
  autoRefreshTimer = window.setInterval(() => { loadData(); }, 30000);
});

onUnmounted(() => {
  if (autoRefreshTimer !== null) clearInterval(autoRefreshTimer);
});
</script>

<style scoped>
.animate-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
