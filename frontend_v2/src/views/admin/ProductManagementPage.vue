<template>
  <div class="p-8 max-w-7xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
          <i class="fas fa-boxes-stacked text-indigo-600"></i>
          <span>Quản Lý Sản Phẩm (Products)</span>
        </h1>
        <p class="text-slate-500 text-sm mt-1">Cấu hình thông số đóng gói, quy chuẩn cân dung sai và file tem nhãn BarTender.</p>
      </div>
      <button 
        v-if="authStore.isAdmin"
        @click="openCreateModal" 
        class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-indigo-200 transition-all hover:scale-102 cursor-pointer w-fit"
      >
        <Plus class="w-5 h-5" />
        <span>Thêm Sản Phẩm Mới</span>
      </button>
    </div>

    <!-- Filters Bar -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
      <div class="relative">
        <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Tìm theo tên sản phẩm, mã CPN, UPC..." 
          class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
        >
      </div>
      
      <div>
        <select 
          v-model="selectedCustomerId" 
          class="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white font-medium text-slate-700"
        >
          <option :value="null">Tất cả Khách hàng (All Customers)</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
        </select>
      </div>

      <div>
        <select 
          v-model="selectedPackingMode" 
          class="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white font-medium text-slate-700"
        >
          <option :value="null">Tất cả Chế độ đóng gói (All Modes)</option>
          <option value="item_scan">📦 Quét mã con (Barcode Scan)</option>
          <option value="weight_scale">⚖️ Đóng gói cân (Weight Scale)</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow-xs border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/80 border-b border-slate-200 text-slate-600 text-xs uppercase tracking-wider font-bold">
              <th class="p-4">Mã Sản Phẩm / CPN</th>
              <th class="p-4">Khách Hàng</th>
              <th class="p-4">Chế Độ / Quy Cách</th>
              <th class="p-4 text-center">Số Lượng / Thùng</th>
              <th class="p-4">Quy Tắc S/N & Mã In</th>
              <th class="p-4">Mẫu Tem (.btw)</th>
              <th v-if="authStore.isAdmin" class="p-4 text-right">Thao Tác</th>
            </tr>

          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="product in filteredProducts" :key="product.id" class="hover:bg-indigo-50/30 transition-colors">
              <td class="p-4">
                <div class="font-bold text-slate-900 font-mono text-base">{{ product.item_name }}</div>
                <div v-if="product.asin" class="text-xs text-amber-700 font-mono font-bold mt-0.5">ASIN: {{ product.asin }}</div>
                <div v-if="product.upc" class="text-xs text-slate-400 font-mono mt-0.5">UPC: {{ product.upc }}</div>
                <div v-if="product.product_desc" class="text-[11px] text-slate-500 line-clamp-1 max-w-xs mt-0.5" :title="product.product_desc">{{ product.product_desc }}</div>
              </td>
              
              <td class="p-4">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-700">
                  <i class="fas fa-building text-[10px] text-slate-400"></i>
                  <span>{{ getCustomerName(product.customer_id) }}</span>
                </span>
              </td>

              <td class="p-4">
                <div v-if="product.packing_mode === 'weight_scale'" class="space-y-1">
                  <span class="inline-flex items-center gap-1 text-xs font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                    <i class="fas fa-weight-scale text-[11px] text-emerald-600"></i>
                    <span>Cân: {{ product.min_weight?.toFixed(3) }} - {{ product.max_weight?.toFixed(3) }} kg</span>
                  </span>
                </div>
                <div v-else class="space-y-1">
                  <span class="inline-flex items-center gap-1 text-xs font-bold text-blue-800 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200">
                    <i class="fas fa-barcode text-[11px] text-blue-600"></i>
                    <span>Quét sê-ri con</span>
                  </span>
                  <div v-if="product.allow_partial" class="text-[10px] font-bold text-amber-600">Cho phép đóng thiếu</div>
                </div>
              </td>

              <td class="p-4 text-center">
                <span class="inline-block px-3 py-1 bg-slate-100 rounded-lg font-black font-mono text-slate-800">
                  {{ product.packed_qty }}
                </span>
              </td>

              <td class="p-4">
                <div v-if="product.template_type === 'erro_05'" class="text-xs font-mono space-y-0.5">
                  <div><span class="text-slate-400">Prefix:</span> <span class="font-bold text-emerald-600">{{ product.pkg_prefix || 'MC220TW1' }}</span></div>
                  <div><span class="text-slate-400">Factory item:</span> <span class="text-slate-700 font-semibold">{{ product.factory_item_code || '-' }}</span></div>
                  <div class="text-[11px] text-slate-500 truncate max-w-[180px]" :title="product.product_desc">{{ product.product_desc }}</div>
                </div>
                <div v-else-if="product.template_type === 'erro_04'" class="text-xs font-mono space-y-0.5">
                  <div><span class="text-slate-400">Carton ID:</span> <span class="font-bold text-rose-600">{{ product.carton_id_prefix || '-' }}...</span></div>
                  <div><span class="text-slate-400">Factory item:</span> <span class="text-slate-700 font-semibold">{{ product.factory_item_code || '-' }}</span></div>
                  <div><span class="text-slate-400">P/N:</span> <span class="text-slate-700 font-semibold">{{ product.mfr_pn || '-' }}</span></div>
                  <div><span class="text-slate-400">Rev:</span> <span class="font-bold text-purple-700">{{ product.revision || '-' }}</span></div>
                </div>
                <div v-else-if="product.template_type === 'erro_03'" class="text-xs font-mono space-y-0.5">
                  <div><span class="text-slate-400">Supplier:</span> <span class="font-bold text-amber-600">{{ product.pkg_prefix || '1012665' }}</span></div>
                  <div v-if="product.revision"><span class="text-slate-400">Rev:</span> <span class="font-bold text-purple-700">{{ product.revision }}</span></div>
                </div>
                <div v-else-if="product.template_type === 'erro_02'" class="text-xs font-mono space-y-0.5">
                  <div><span class="text-slate-400">SSCC:</span> <span class="font-bold text-indigo-600">0{{ product.pkg_prefix || '37033907' }}...</span></div>
                  <div><span class="text-slate-400">P/N:</span> <span class="text-slate-700 font-semibold">{{ product.mfr_pn || '-' }}</span></div>
                  <div v-if="product.asin"><span class="text-slate-400">ASIN:</span> <span class="font-bold text-amber-600">{{ product.asin }}</span></div>
                </div>
                <div v-else-if="product.packing_mode === 'weight_scale'" class="text-xs font-mono space-y-0.5">
                  <div><span class="text-slate-400">Prefix:</span> <span class="font-bold text-indigo-600">{{ product.pkg_prefix || '-' }}</span></div>
                  <div><span class="text-slate-400">MFR:</span> <span class="text-slate-700 font-semibold">{{ product.mfr_pn || '-' }}</span></div>
                  <div v-if="product.revision"><span class="text-slate-400">Rev:</span> <span class="font-bold text-purple-700">{{ product.revision }}</span></div>
                </div>
                <div v-else class="text-xs font-mono space-y-0.5">
                  <div><span class="text-slate-400">Start:</span> <span class="font-bold text-indigo-600">{{ product.start_part || '-' }}</span></div>
                  <div><span class="text-slate-400">Middle:</span> <span class="text-slate-700 font-semibold">{{ product.middle_part || '-' }}</span></div>
                </div>
              </td>

              <td class="p-4">
                <div class="space-y-1">
                  <span :class="[
                    'px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider inline-block',
                    product.template_type === 'erro_05' ? 'bg-teal-100 text-teal-800 border border-teal-200' :
                    product.template_type === 'erro_04' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                    product.template_type === 'erro_03' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                    product.template_type === 'erro_02' ? 'bg-sky-100 text-sky-800 border border-sky-200' :
                    product.template_type === 'erro_01' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                    product.template_type === 'detailed' ? 'bg-amber-100 text-amber-800 border border-amber-200' : 
                    'bg-indigo-100 text-indigo-800 border border-indigo-200'
                  ]">
                    {{ product.template_type === 'erro_05' ? 'Erro 05' : (product.template_type === 'erro_04' ? 'Erro 04' : (product.template_type === 'erro_03' ? 'Erro 03' : (product.template_type === 'erro_02' ? 'Erro 02' : (product.template_type === 'erro_01' ? 'Erro 01' : (product.template_type || 'standard'))))) }}
                  </span>
                  <div class="text-[11px] text-slate-400 font-mono truncate max-w-[140px]" :title="product.template_path">
                    {{ product.template_path || 'Mặc định' }}
                  </div>
                </div>
              </td>

              <td v-if="authStore.isAdmin" class="p-4 text-right">
                <div class="flex justify-end gap-1.5">
                  <button 
                    @click="openEditModal(product)" 
                    class="p-2 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all cursor-pointer" 
                    title="Chỉnh sửa sản phẩm"
                  >
                    <Edit2 class="w-4 h-4" />
                  </button>
                  <button 
                    @click="confirmDelete(product)" 
                    class="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all cursor-pointer" 
                    title="Xóa sản phẩm"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="filteredProducts.length === 0">
              <td colspan="7" class="p-12 text-center text-slate-400 italic">
                <i class="fas fa-inbox text-3xl mb-2 block opacity-40"></i>
                <span>Không tìm thấy sản phẩm nào phù hợp với bộ lọc.</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Product Form Modal Component -->
    <ProductFormModal 
      :show="showModal"
      :is-edit="isEdit"
      :is-submitting="isSubmitting"
      :customers="customers"
      :initial-data="selectedProduct"
      @close="showModal = false"
      @submit="handleSaveProduct"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Plus, Search, Edit2, Trash2 } from 'lucide-vue-next';
import catalogApi from '../../features/catalog/api';
import ProductFormModal, { type ProductFormData } from '../../features/catalog/components/ProductFormModal.vue';
import { useSystemStore } from '../../core/stores/system';
import { useAuthStore } from '../../core/stores/auth';
import type { Product, Customer } from '../../types/api';

const system = useSystemStore();
const authStore = useAuthStore();
const products = ref<Product[]>([]);
const customers = ref<Customer[]>([]);
const searchQuery = ref<string>('');
const selectedCustomerId = ref<number | null>(null);
const selectedPackingMode = ref<string | null>(null);
const showModal = ref<boolean>(false);
const isEdit = ref<boolean>(false);
const isSubmitting = ref<boolean>(false);
const currentId = ref<number | null>(null);
const selectedProduct = ref<Product | null>(null);

const filteredProducts = computed(() => {
  let list = products.value;
  if (selectedCustomerId.value) {
    list = list.filter(p => p.customer_id === selectedCustomerId.value);
  }
  if (selectedPackingMode.value) {
    list = list.filter(p => p.packing_mode === selectedPackingMode.value);
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(p => 
      p.item_name.toLowerCase().includes(q) || 
      (p.upc && p.upc.toLowerCase().includes(q)) ||
      (p.pkg_prefix && p.pkg_prefix.toLowerCase().includes(q)) ||
      (p.mfr_pn && p.mfr_pn.toLowerCase().includes(q)) ||
      (p.asin && p.asin.toLowerCase().includes(q)) ||
      (p.product_desc && p.product_desc.toLowerCase().includes(q))
    );
  }
  return list;
});

const fetchData = async () => {
  try {
    const [prodRes, custRes] = await Promise.all([
      catalogApi.getAllProducts(),
      catalogApi.getCustomers()
    ]);
    products.value = prodRes.data;
    customers.value = custRes.data;
  } catch (err) {
    system.showNotification('Không thể tải danh sách sản phẩm', 'error');
  }
};

const getCustomerName = (id: number) => {
  const c = customers.value.find(c => c.id === id);
  return c ? c.name : 'Unknown';
};

const openCreateModal = () => {
  isEdit.value = false;
  currentId.value = null;
  selectedProduct.value = null;
  showModal.value = true;
};

const openEditModal = (product: Product) => {
  isEdit.value = true;
  currentId.value = product.id;
  selectedProduct.value = product;
  showModal.value = true;
};

const handleSaveProduct = async (formData: ProductFormData) => {
  if (!formData.customer_id) {
    system.showNotification('Vui lòng chọn khách hàng', 'error');
    return;
  }
  isSubmitting.value = true;
  try {
    if (isEdit.value && currentId.value !== null) {
      await catalogApi.updateProduct(currentId.value, formData as any);
      system.showNotification('Đã cập nhật sản phẩm thành công', 'success');
    } else {
      await catalogApi.createProduct(formData as any);
      system.showNotification('Đã thêm sản phẩm mới thành công', 'success');
    }
    showModal.value = false;
    await fetchData();
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Lỗi khi lưu dữ liệu sản phẩm';
    system.showNotification(msg, 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const confirmDelete = async (product: Product) => {
  if (confirm(`Bạn có chắc chắn muốn xóa sản phẩm "${product.item_name}"?`)) {
    try {
      await catalogApi.deleteProduct(product.id);
      system.showNotification('Đã xóa sản phẩm thành công', 'success');
      await fetchData();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Không thể xóa sản phẩm này (có thể đã có lịch sử đóng thùng)';
      system.showNotification(msg, 'error');
    }
  }
};

onMounted(fetchData);
</script>
