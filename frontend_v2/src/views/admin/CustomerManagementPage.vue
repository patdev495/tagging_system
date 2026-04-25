<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Quản lý Khách hàng</h1>
        <p class="text-slate-500">Thêm, sửa hoặc xóa thông tin khách hàng trong hệ thống.</p>
      </div>
      <button @click="openCreateModal" class="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700 transition-colors shadow-md">
        <Plus class="w-5 h-5" />
        Thêm Khách hàng
      </button>
    </div>

    <!-- Search bar -->
    <div class="mb-6 relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
      <input 
        v-model="searchQuery"
        type="text" 
        placeholder="Tìm kiếm theo mã hoặc tên..." 
        class="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
      >
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200">
            <th class="p-4 font-semibold text-slate-700">ID</th>
            <th class="p-4 font-semibold text-slate-700">Mã khách hàng</th>
            <th class="p-4 font-semibold text-slate-700">Tên khách hàng</th>
            <th class="p-4 font-semibold text-slate-700 text-right">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in filteredCustomers" :key="customer.id" class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="p-4 text-slate-500 text-sm">#{{ customer.id }}</td>
            <td class="p-4 font-bold text-indigo-900">{{ customer.code }}</td>
            <td class="p-4 text-slate-700">{{ customer.name }}</td>
            <td class="p-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openEditModal(customer)" class="p-2 text-slate-400 hover:text-indigo-600 transition-colors" title="Sửa">
                  <Edit2 class="w-5 h-5" />
                </button>
                <button @click="confirmDelete(customer)" class="p-2 text-slate-400 hover:text-red-600 transition-colors" title="Xóa">
                  <Trash2 class="w-5 h-5" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredCustomers.length === 0">
            <td colspan="4" class="p-12 text-center text-slate-400 italic">Không tìm thấy khách hàng nào.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-indigo-900 text-white">
          <h2 class="text-xl font-bold">{{ isEdit ? 'Cập nhật Khách hàng' : 'Thêm Khách hàng mới' }}</h2>
          <button @click="showModal = false" class="hover:bg-white/20 p-1 rounded-lg transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <form @submit.prevent="saveCustomer" class="p-6 space-y-4">
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-700">Mã khách hàng (Code)</label>
            <input 
              v-model="form.code"
              type="text" 
              required
              placeholder="Ví dụ: APPLE, SAMSUNG..." 
              class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
              :disabled="isEdit"
            >
            <p class="text-xs text-slate-400">Mã này thường là viết tắt, không dấu, dùng để sinh mã thùng.</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-semibold text-slate-700">Tên khách hàng</label>
            <input 
              v-model="form.name"
              type="text" 
              required
              placeholder="Nhập tên đầy đủ..." 
              class="w-full p-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
            >
          </div>

          <div class="pt-4 flex gap-3">
            <button type="button" @click="showModal = false" class="flex-1 px-4 py-3 rounded-lg border border-slate-200 font-semibold text-slate-600 hover:bg-slate-50 transition-colors">
              Hủy
            </button>
            <button type="submit" :disabled="isSubmitting" class="flex-1 px-4 py-3 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors shadow-md disabled:opacity-50">
              {{ isSubmitting ? 'Đang lưu...' : 'Lưu thông tin' }}
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
const customers = ref([]);
const searchQuery = ref('');
const showModal = ref(false);
const isEdit = ref(false);
const isSubmitting = ref(false);
const currentId = ref(null);

const form = ref({
  code: '',
  name: ''
});

const filteredCustomers = computed(() => {
  if (!searchQuery.value) return customers.value;
  const q = searchQuery.value.toLowerCase();
  return customers.value.filter(c => 
    c.code.toLowerCase().includes(q) || 
    c.name.toLowerCase().includes(q)
  );
});

const fetchCustomers = async () => {
  try {
    const res = await catalogApi.getCustomers();
    customers.value = res.data;
  } catch (err) {
    system.showNotification('Không thể tải danh sách khách hàng', 'error');
  }
};

const openCreateModal = () => {
  isEdit.value = false;
  currentId.value = null;
  form.value = { code: '', name: '' };
  showModal.value = true;
};

const openEditModal = (customer) => {
  isEdit.value = true;
  currentId.value = customer.id;
  form.value = { ...customer };
  showModal.value = true;
};

const saveCustomer = async () => {
  isSubmitting.value = true;
  try {
    if (isEdit.value) {
      await catalogApi.updateCustomer(currentId.value, form.value);
      system.showNotification('Cập nhật khách hàng thành công', 'success');
    } else {
      await catalogApi.createCustomer(form.value);
      system.showNotification('Thêm khách hàng thành công', 'success');
    }
    showModal.value = false;
    await fetchCustomers();
  } catch (err) {
    const msg = err.response?.data?.detail || 'Lỗi khi lưu dữ liệu';
    system.showNotification(msg, 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const confirmDelete = async (customer) => {
  if (confirm(`Bạn có chắc chắn muốn xóa khách hàng "${customer.name}"? Hành động này không thể hoàn tác.`)) {
    try {
      await catalogApi.deleteCustomer(customer.id);
      system.showNotification('Đã xóa khách hàng', 'success');
      await fetchCustomers();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Không thể xóa khách hàng này (có thể do đang có dữ liệu liên quan)';
      system.showNotification(msg, 'error');
    }
  }
};

onMounted(fetchCustomers);
</script>
