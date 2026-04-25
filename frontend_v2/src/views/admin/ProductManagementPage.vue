<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Quản lý Sản phẩm</h1>
        <p class="text-slate-500">Cấu hình thông tin SKU, quy cách đóng gói và mẫu tem.</p>
      </div>
      <button @click="openCreateModal" class="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700 transition-colors shadow-md">
        <Plus class="w-5 h-5" />
        Thêm Sản phẩm
      </button>
    </div>

    <!-- Filters -->
    <div class="flex gap-4 mb-6">
      <div class="flex-1 relative">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Tìm kiếm theo tên sản phẩm hoặc UPC..." 
          class="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
        >
      </div>
      <select 
        v-model="selectedCustomerId" 
        class="w-64 p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm bg-white"
      >
        <option :value="null">Tất cả khách hàng</option>
        <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200">
              <th class="p-4 font-semibold text-slate-700 whitespace-nowrap">Tên sản phẩm</th>
              <th class="p-4 font-semibold text-slate-700">Khách hàng</th>
              <th class="p-4 font-semibold text-slate-700">UPC</th>
              <th class="p-4 font-semibold text-slate-700">Định mức QTY</th>
              <th class="p-4 font-semibold text-slate-700">Prefix (SN)</th>
              <th class="p-4 font-semibold text-slate-700">Tem</th>
              <th class="p-4 font-semibold text-slate-700 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.id" class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td class="p-4 font-bold text-indigo-900">{{ product.item_name }}</td>
              <td class="p-4 text-slate-600 text-sm">{{ getCustomerName(product.customer_id) }}</td>
              <td class="p-4 text-slate-500 font-mono text-xs">{{ product.upc || '-' }}</td>
              <td class="p-4 text-slate-700">
                <span class="bg-slate-100 px-2 py-1 rounded font-bold">{{ product.packed_qty }}</span>
              </td>
              <td class="p-4">
                <div class="flex flex-col text-xs">
                  <span class="text-indigo-600 font-bold">{{ product.start_part }}</span>
                  <span class="text-slate-400">{{ product.middle_part }}</span>
                </div>
              </td>
              <td class="p-4">
                <span :class="['px-2 py-1 rounded-full text-[10px] font-bold uppercase', (product.template_type || 'standard') === 'detailed' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700']">
                  {{ product.template_type || 'standard' }}
                </span>
              </td>
              <td class="p-4 text-right">
                <div class="flex justify-end gap-1">
                  <button @click="openEditModal(product)" class="p-2 text-slate-400 hover:text-indigo-600 transition-colors">
                    <Edit2 class="w-4 h-4" />
                  </button>
                  <button @click="confirmDelete(product)" class="p-2 text-slate-400 hover:text-red-600 transition-colors">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredProducts.length === 0">
              <td colspan="7" class="p-12 text-center text-slate-400 italic">Không tìm thấy sản phẩm nào.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-indigo-900 text-white">
          <h2 class="text-xl font-bold">{{ isEdit ? 'Cập nhật Sản phẩm' : 'Thêm Sản phẩm mới' }}</h2>
          <button @click="showModal = false" class="hover:bg-white/20 p-1 rounded-lg transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <form @submit.prevent="saveProduct" class="p-6">
          <div class="grid md:grid-cols-2 gap-6">
            <!-- Left Col -->
            <div class="space-y-4">
              <div class="space-y-1">
                <label class="text-sm font-semibold text-slate-700">Khách hàng</label>
                <select v-model="form.customer_id" required class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none bg-white">
                  <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>

              <div class="space-y-1">
                <label class="text-sm font-semibold text-slate-700">Tên sản phẩm (Item Name)</label>
                <input v-model="form.item_name" type="text" required class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none">
              </div>

              <div class="space-y-1">
                <label class="text-sm font-semibold text-slate-700">UPC / GTIN</label>
                <input v-model="form.upc" type="text" class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none">
              </div>

              <div class="space-y-1">
                <label class="text-sm font-semibold text-slate-700">Định mức đóng gói (Packed QTY)</label>
                <input v-model.number="form.packed_qty" type="number" required min="1" class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none">
              </div>
            </div>

            <!-- Right Col -->
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1">
                  <label class="text-sm font-semibold text-slate-700">S/N Start Part</label>
                  <input v-model="form.start_part" type="text" placeholder="CN/VN" class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div class="space-y-1">
                  <label class="text-sm font-semibold text-slate-700">S/N Middle Part</label>
                  <input v-model="form.middle_part" type="text" placeholder="11, 16..." class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
              </div>

              <div class="space-y-1">
                <label class="text-sm font-semibold text-slate-700">Loại mẫu tem (Template Type)</label>
                <select v-model="form.template_type" class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none bg-white">
                  <option value="standard">Standard (Cơ bản)</option>
                  <option value="detailed">Detailed (Chi tiết)</option>
                </select>
              </div>

              <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <label class="flex items-center gap-3 cursor-pointer">
                  <input v-model="form.allow_partial" type="checkbox" :true-value="1" :false-value="0" class="w-5 h-5 rounded text-indigo-600">
                  <span class="text-sm font-semibold text-slate-700">Cho phép đóng thùng lẻ (Partial)</span>
                </label>
                <p class="text-xs text-slate-400 mt-2">Nếu bật, người dùng có thể nhấn "Pack Now" dù chưa đủ số lượng QTY.</p>
              </div>
            </div>
          </div>

          <div class="pt-8 flex gap-3">
            <button type="button" @click="showModal = false" class="flex-1 px-4 py-3 rounded-lg border border-slate-200 font-semibold text-slate-600 hover:bg-slate-50 transition-colors">
              Hủy
            </button>
            <button type="submit" :disabled="isSubmitting" class="flex-1 px-4 py-3 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors shadow-md disabled:opacity-50">
              {{ isSubmitting ? 'Đang lưu...' : 'Lưu sản phẩm' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-vue-next';
import catalogApi from '../../features/catalog/api';
import { useSystemStore } from '../../core/stores/system';

const system = useSystemStore();
const products = ref([]);
const customers = ref([]);
const searchQuery = ref('');
const selectedCustomerId = ref(null);
const showModal = ref(false);
const isEdit = ref(false);
const isSubmitting = ref(false);
const currentId = ref(null);

const form = ref({
  item_name: '',
  upc: '',
  packed_qty: 1,
  start_part: 'VN',
  middle_part: '',
  template_type: 'standard',
  allow_partial: 0,
  customer_id: null
});

const filteredProducts = computed(() => {
  let list = products.value;
  if (selectedCustomerId.value) {
    list = list.filter(p => p.customer_id === selectedCustomerId.value);
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(p => 
      p.item_name.toLowerCase().includes(q) || 
      (p.upc && p.upc.toLowerCase().includes(q))
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
    system.showNotification('Không thể tải dữ liệu sản phẩm', 'error');
  }
};

const getCustomerName = (id) => {
  const c = customers.value.find(c => c.id === id);
  return c ? c.name : 'Unknown';
};

const openCreateModal = () => {
  isEdit.value = false;
  currentId.value = null;
  form.value = {
    item_name: '',
    upc: '',
    packed_qty: 1,
    start_part: 'VN',
    middle_part: '',
    template_type: 'standard',
    allow_partial: 0,
    customer_id: customers.value.length > 0 ? customers.value[0].id : null
  };
  showModal.value = true;
};

const openEditModal = (product) => {
  isEdit.value = true;
  currentId.value = product.id;
  form.value = { ...product };
  showModal.value = true;
};

const saveProduct = async () => {
  if (!form.value.customer_id) {
    system.showNotification('Vui lòng chọn khách hàng', 'error');
    return;
  }
  isSubmitting.value = true;
  try {
    if (isEdit.value) {
      await catalogApi.updateProduct(currentId.value, form.value);
      system.showNotification('Cập nhật sản phẩm thành công', 'success');
    } else {
      await catalogApi.createProduct(form.value);
      system.showNotification('Thêm sản phẩm thành công', 'success');
    }
    showModal.value = false;
    await fetchData();
  } catch (err) {
    const msg = err.response?.data?.detail || 'Lỗi khi lưu dữ liệu';
    system.showNotification(msg, 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const confirmDelete = async (product) => {
  if (confirm(`Bạn có chắc muốn xóa sản phẩm "${product.item_name}"?`)) {
    try {
      await catalogApi.deleteProduct(product.id);
      system.showNotification('Đã xóa sản phẩm', 'success');
      await fetchData();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Không thể xóa sản phẩm (đã có dữ liệu đóng gói)';
      system.showNotification(msg, 'error');
    }
  }
};

onMounted(fetchData);
</script>
