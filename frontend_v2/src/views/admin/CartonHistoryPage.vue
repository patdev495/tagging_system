<template>
  <div class="p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900">Lịch sử Carton</h1>
      <p class="text-slate-500">Tra cứu và quản lý lịch sử đóng gói thùng hàng.</p>
    </div>

    <!-- Filters -->
    <div class="grid md:grid-cols-4 gap-4 mb-6 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div class="space-y-1">
        <label class="text-xs font-bold text-slate-400 uppercase">Tìm Carton S/N</label>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input v-model="filters.search" type="text" placeholder="Nhập mã thùng..." class="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm">
        </div>
      </div>
      
      <div class="space-y-1">
        <label class="text-xs font-bold text-slate-400 uppercase">Sản phẩm</label>
        <select v-model="filters.product_id" class="w-full p-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm bg-white">
          <option :value="null">Tất cả sản phẩm</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.item_name }}</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-bold text-slate-400 uppercase">Trạng thái</label>
        <select v-model="filters.status" class="w-full p-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm bg-white">
          <option :value="null">Tất cả</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
        </select>
      </div>

      <div class="flex items-end">
        <button @click="fetchHistory(0)" class="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition-colors shadow-md flex items-center justify-center gap-2">
          <Filter class="w-4 h-4" />
          Lọc dữ liệu
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
            <th class="p-4 font-bold">Ngày tạo</th>
            <th class="p-4 font-bold">Carton S/N</th>
            <th class="p-4 font-bold">Sản phẩm</th>
            <th class="p-4 font-bold">Job Order</th>
            <th class="p-4 font-bold">Trạng thái</th>
            <th class="p-4 font-bold text-right">Chi tiết</th>
          </tr>
        </thead>
        <tbody class="text-sm">
          <tr v-for="carton in history" :key="carton.id" class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="p-4 text-slate-500">{{ formatDate(carton.created_at) }}</td>
            <td class="p-4 font-bold text-indigo-900">
              <div class="flex items-center gap-2">
                {{ carton.carton_sn }}
                <span v-if="carton.is_reprint" class="bg-amber-100 text-amber-700 text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter">Reprint</span>
              </div>
            </td>
            <td class="p-4 text-slate-700">{{ carton.product?.item_name || 'N/A' }}</td>
            <td class="p-4 text-slate-600">{{ carton.job_order || '-' }}</td>
            <td class="p-4">
              <span :class="['px-2 py-1 rounded-full text-[10px] font-bold', carton.status === 'SUCCESS' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                {{ carton.status }}
              </span>
            </td>
            <td class="p-4 text-right">
              <button @click="viewDetail(carton)" class="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                <ExternalLink class="w-5 h-5" />
              </button>
            </td>
          </tr>
          <tr v-if="history.length === 0">
            <td colspan="6" class="p-12 text-center text-slate-400 italic">Không tìm thấy dữ liệu đóng gói.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="p-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
        <span class="text-xs text-slate-500 font-medium">Hiển thị {{ history.length }} / {{ totalCount }} bản ghi</span>
        <div class="flex gap-2">
          <button 
            @click="fetchHistory(currentPage - 1)" 
            :disabled="currentPage === 0"
            class="px-3 py-1 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-30 hover:bg-slate-50"
          >
            Trước
          </button>
          <button 
            @click="fetchHistory(currentPage + 1)" 
            :disabled="(currentPage + 1) * 50 >= totalCount"
            class="px-3 py-1 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-30 hover:bg-slate-50"
          >
            Tiếp
          </button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedCarton" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        <!-- Sticky Header -->
        <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-indigo-900 text-white shrink-0">
          <div>
            <h2 class="text-xl font-bold">Chi tiết Carton: {{ selectedCarton.carton_sn }}</h2>
            <p class="text-xs opacity-70">Ngày tạo: {{ formatDate(selectedCarton.created_at) }}</p>
          </div>
          <button @click="selectedCarton = null" class="hover:bg-white/20 p-1 rounded-lg transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <!-- Scrollable Content Container -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
          <div class="grid grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-100">
            <div class="space-y-1">
              <p class="text-[10px] font-bold text-slate-400 uppercase">Sản phẩm</p>
              <p class="font-bold text-slate-900 text-sm">{{ selectedCarton.product?.item_name }}</p>
            </div>
            <div class="space-y-1 text-right">
              <p class="text-[10px] font-bold text-slate-400 uppercase">UPC</p>
              <p class="font-mono text-slate-900 text-sm">{{ selectedCarton.product?.upc || '-' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[10px] font-bold text-slate-400 uppercase">Job Order</p>
              <p class="font-bold text-indigo-600 text-sm">{{ selectedCarton.job_order || 'Không có' }}</p>
            </div>
            <div class="space-y-1 text-right">
              <p class="text-[10px] font-bold text-slate-400 uppercase">Packed By</p>
              <p class="font-bold text-slate-900 text-sm">{{ selectedCarton.packed_by || '-' }}</p>
            </div>
          </div>

          <div>
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-bold text-slate-700 flex items-center gap-2">
                <Box class="w-5 h-5 text-indigo-500" />
                S/N chi tiết ({{ cartonItems.length }})
              </h3>
            </div>
            
            <div class="rounded-xl border border-slate-200 bg-white shadow-inner overflow-hidden">
              <div v-for="(item, idx) in cartonItems" :key="item.id" class="px-6 py-3 border-b border-slate-50 last:border-0 flex items-center hover:bg-indigo-50/30 transition-colors group">
                <span class="text-[10px] font-bold text-slate-300 w-10">{{ String(idx + 1).padStart(2, '0') }}</span>
                <span class="flex-1 font-mono text-sm font-medium text-slate-700">{{ item.item_sn }}</span>
                <CheckCircle2 class="w-4 h-4 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div v-if="isLoadingItems" class="p-12 text-center">
                <div class="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                <p class="text-xs text-slate-400">Đang tải dữ liệu...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Footer -->
        <div class="p-6 border-t border-slate-100 flex justify-end shrink-0 bg-white">
          <button @click="selectedCarton = null" class="px-8 py-3 rounded-xl bg-slate-100 font-bold text-slate-600 hover:bg-slate-200 transition-colors">
            Đóng cửa sổ
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { Search, Filter, ExternalLink, X, Box, CheckCircle2 } from 'lucide-vue-next';
import historyApi from '../../features/history/api';
import catalogApi from '../../features/catalog/api';
import { useSystemStore } from '../../core/stores/system';

const system = useSystemStore();
const history = ref([]);
const products = ref([]);
const totalCount = ref(0);
const currentPage = ref(0);
const selectedCarton = ref(null);
const cartonItems = ref([]);
const isLoadingItems = ref(false);

const filters = ref({
  search: '',
  product_id: null,
  status: null
});

const fetchHistory = async (page = 0) => {
  try {
    currentPage.value = page;
    const res = await historyApi.getCartons({
      skip: page * 50,
      limit: 50,
      search: filters.value.search || undefined,
      product_id: filters.value.product_id || undefined,
      status: filters.value.status || undefined
    });
    history.value = res.data.items;
    totalCount.value = res.data.total;
  } catch (err) {
    system.showNotification('Không thể tải lịch sử đóng gói', 'error');
  }
};

const fetchProducts = async () => {
  try {
    const res = await catalogApi.getAllProducts();
    products.value = res.data;
  } catch (err) {}
};

const viewDetail = async (carton) => {
  selectedCarton.value = carton;
  cartonItems.value = [];
  isLoadingItems.value = true;
  try {
    const res = await historyApi.getCartonDetail(carton.id);
    cartonItems.value = res.data.items || [];
  } catch (err) {
    system.showNotification('Không thể tải chi tiết sản phẩm', 'error');
  } finally {
    isLoadingItems.value = false;
  }
};

const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleString('vi-VN');
};

onMounted(() => {
  fetchHistory();
  fetchProducts();
});

// Auto fetch when filters change (debounced search would be better, but simple for now)
watch([() => filters.value.product_id, () => filters.value.status], () => {
  fetchHistory(0);
});
</script>
