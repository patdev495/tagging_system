<template>
  <div class="p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900">{{ t('admin.history') }}</h1>
      <p class="text-slate-500">{{ t('admin.history_subtitle') }}</p>
    </div>

    <!-- Filters -->
    <div class="grid md:grid-cols-4 gap-4 mb-6 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div class="space-y-1">
        <label class="text-xs font-bold text-slate-400 uppercase">{{ t('admin.find_sn') }}</label>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input v-model="filters.search" type="text" :placeholder="t('admin.find_sn_placeholder')" class="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm">
        </div>
      </div>
      
      <div class="space-y-1">
        <label class="text-xs font-bold text-slate-400 uppercase">{{ t('admin.product') }}</label>
        <select v-model="filters.product_id" class="w-full p-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm bg-white">
          <option :value="null">{{ t('admin.all_products') }}</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.item_name }}</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="text-xs font-bold text-slate-400 uppercase">{{ t('admin.status') }}</label>
        <select v-model="filters.status" class="w-full p-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none text-sm bg-white">
          <option :value="null">{{ t('admin.all_statuses') }}</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
        </select>
      </div>

      <div class="flex items-end">
        <button @click="fetchHistory(0)" class="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition-colors shadow-md flex items-center justify-center gap-2">
          <Filter class="w-4 h-4" />
          {{ t('admin.filter_data') }}
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
            <th class="p-4 font-bold">{{ t('admin.created_at') }}</th>
            <th class="p-4 font-bold">{{ t('admin.carton_sn') }}</th>
            <th class="p-4 font-bold">{{ t('admin.product') }}</th>
            <th class="p-4 font-bold">{{ t('packing.job_order') }}</th>
            <th class="p-4 font-bold">{{ t('admin.status') }}</th>
            <th class="p-4 font-bold">{{ t('admin.station_id') }}</th>
            <th class="p-4 font-bold text-right">{{ t('admin.details') }}</th>
          </tr>
        </thead>
        <tbody class="text-sm">
          <tr v-for="carton in history" :key="carton.id" class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="p-4 text-slate-500">{{ formatDate(carton.created_at) }}</td>
            <td class="p-4 font-bold text-indigo-900">
              <div class="flex items-center gap-2">
                {{ carton.carton_sn }}
                <span v-if="carton.is_reprint" class="bg-amber-100 text-amber-700 text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter">{{ t('print.reprint') }}</span>
              </div>
            </td>
            <td class="p-4 text-slate-700">{{ carton.product?.item_name || 'N/A' }}</td>
            <td class="p-4 text-slate-600">{{ carton.job_order || '-' }}</td>
            <td class="p-4">
              <span :class="['px-2 py-1 rounded-full text-[10px] font-bold', carton.status === 'SUCCESS' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                {{ carton.status }}
              </span>
            </td>
            <td class="p-4 text-[10px] font-mono text-slate-400">{{ carton.station_id || '-' }}</td>
            <td class="p-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="viewDetail(carton)" class="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="View Details">
                  <ExternalLink class="w-5 h-5" />
                </button>
                <button @click="handleDelete(carton)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Delete Carton">
                  <Trash2 class="w-5 h-5" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="history.length === 0">
            <td colspan="7" class="p-12 text-center text-slate-400 italic">{{ t('admin.no_data') }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="p-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
        <span class="text-xs text-slate-500 font-medium">{{ t('admin.showing_records', { current: history.length, total: totalCount }) }}</span>
        <div class="flex gap-2">
          <button 
            @click="fetchHistory(currentPage - 1)" 
            :disabled="currentPage === 0"
            class="px-3 py-1 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-30 hover:bg-slate-50"
          >
            {{ t('admin.previous') }}
          </button>
          <button 
            @click="fetchHistory(currentPage + 1)" 
            :disabled="(currentPage + 1) * 50 >= totalCount"
            class="px-3 py-1 rounded border border-slate-200 bg-white text-slate-600 disabled:opacity-30 hover:bg-slate-50"
          >
            {{ t('admin.next') }}
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
            <h2 class="text-xl font-bold">{{ t('admin.carton_details') }}: {{ selectedCarton.carton_sn }}</h2>
            <p class="text-xs opacity-70">{{ t('admin.created_at') }}: {{ formatDate(selectedCarton.created_at) }}</p>
          </div>
          <button @click="selectedCarton = null" class="hover:bg-white/20 p-1 rounded-lg transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <!-- Scrollable Content Container -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
          <div class="grid grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-100">
            <div class="space-y-1">
              <p class="text-[10px] font-bold text-slate-400 uppercase">{{ t('admin.product') }}</p>
              <p class="font-bold text-slate-900 text-sm">{{ selectedCarton.product?.item_name }}</p>
            </div>
            <div class="space-y-1 text-right">
              <p class="text-[10px] font-bold text-slate-400 uppercase">{{ t('admin.upc') }}</p>
              <p class="font-mono text-slate-900 text-sm">{{ selectedCarton.product?.upc || '-' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[10px] font-bold text-slate-400 uppercase">{{ t('packing.job_order') }}</p>
              <p class="font-bold text-indigo-600 text-sm">{{ selectedCarton.job_order || 'None' }}</p>
            </div>
            <div class="space-y-1 text-right">
              <p class="text-[10px] font-bold text-slate-400 uppercase">{{ t('admin.station_id_mac') }}</p>
              <p class="font-mono text-indigo-900 text-[10px]">{{ selectedCarton.station_id || '-' }}</p>
            </div>
          </div>

          <div>
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-bold text-slate-700 flex items-center gap-2">
                <Box class="w-5 h-5 text-indigo-500" />
                {{ t('admin.detailed_sns', { count: cartonItems.length }) }}
              </h3>
            </div>
            
            <div class="rounded-xl border border-slate-200 bg-white shadow-inner overflow-hidden">
              <div v-for="(item, idx) in cartonItems" :key="item.id" class="px-6 py-3 border-b border-slate-50 last:border-0 flex items-center hover:bg-indigo-50/30 transition-colors group">
                <div class="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-black text-slate-400 shrink-0 mr-4 group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                  {{ idx + 1 }}
                </div>
                <span class="flex-1 font-mono text-sm font-medium text-slate-700">{{ item.item_sn }}</span>
                <CheckCircle2 class="w-4 h-4 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div v-if="isLoadingItems" class="p-12 text-center">
                <div class="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                <p class="text-xs text-slate-400">{{ t('admin.loading_data') }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Footer -->
        <div class="p-6 border-t border-slate-100 flex justify-between shrink-0 bg-white">
          <button @click="handleDelete(selectedCarton)" class="px-6 py-3 rounded-xl bg-red-50 font-bold text-red-600 hover:bg-red-100 transition-colors flex items-center gap-2">
            <Trash2 class="w-5 h-5" />
            Delete Carton
          </button>
          <button @click="selectedCarton = null" class="px-8 py-3 rounded-xl bg-slate-100 font-bold text-slate-600 hover:bg-slate-200 transition-colors">
            {{ t('admin.close_window') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { Search, Filter, ExternalLink, X, Box, CheckCircle2, Trash2 } from 'lucide-vue-next';
import historyApi from '../../features/history/api';
import catalogApi from '../../features/catalog/api';
import { useSystemStore } from '../../core/stores/system';
import type { Carton, Product } from '../../types/api';

const { t } = useI18n();
const system = useSystemStore();
const history = ref<(Carton & { product?: Product })[]>([]);
const products = ref<Product[]>([]);
const totalCount = ref<number>(0);
const currentPage = ref<number>(0);
const selectedCarton = ref<(Carton & { product?: Product }) | null>(null);
const cartonItems = ref<{ id: number, item_sn: string }[]>([]);
const isLoadingItems = ref<boolean>(false);

const filters = ref<{
  search: string;
  product_id: number | null;
  status: string | null;
}>({
  search: '',
  product_id: null,
  status: null
});

const fetchHistory = async (page: number = 0) => {
  try {
    currentPage.value = page;
    const res = await historyApi.getCartons({
      skip: page * 50,
      limit: 50,
      search: filters.value.search || undefined,
      product_id: (filters.value.product_id as any) || undefined,
      status: filters.value.status || undefined
    });
    history.value = res.data.items;
    totalCount.value = res.data.total;
  } catch (err) {
    system.showNotification('Could not load packing history', 'error');
  }
};

const fetchProducts = async () => {
  try {
    const res = await catalogApi.getAllProducts();
    products.value = res.data;
  } catch (err) {}
};

const viewDetail = async (carton: Carton & { product?: Product }) => {
  selectedCarton.value = carton;
  cartonItems.value = [];
  isLoadingItems.value = true;
  try {
    const res = await historyApi.getCartonDetail(carton.id);
    cartonItems.value = res.data.items || [];
  } catch (err) {
    system.showNotification('Could not load item details', 'error');
  } finally {
    isLoadingItems.value = false;
  }
};

const handleDelete = async (carton: Carton) => {
  if (!confirm(`Are you sure you want to delete carton ${carton.carton_sn}? This will also delete all associated S/Ns.`)) {
    return;
  }
  
  try {
    await historyApi.deleteCarton(carton.id);
    system.showNotification('Carton deleted successfully', 'success');
    if (selectedCarton.value?.id === carton.id) {
      selectedCarton.value = null;
    }
    fetchHistory(currentPage.value);
  } catch (err) {
    system.showNotification('Failed to delete carton', 'error');
  }
};

const formatDate = (dateStr: string) => {
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
