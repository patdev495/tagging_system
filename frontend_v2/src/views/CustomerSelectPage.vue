<template>
  <div class="min-h-screen w-full p-4 md:p-8 flex items-center justify-center bg-slate-100 text-slate-900 selection:bg-indigo-600 selection:text-white relative">
    
    <!-- Top-Right Admin Button -->
    <div class="absolute top-4 right-4 md:top-6 md:right-8 z-10">
      <router-link
        to="/admin"
        class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-slate-200/90 text-slate-700 hover:text-indigo-600 hover:border-indigo-300 font-bold text-xs shadow-xs hover:shadow-md transition-all duration-200 group"
        title="Truy cập Trang Quản Trị Hệ Thống"
      >
        <div class="w-6 h-6 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors">
          <i class="fas fa-shield-alt text-xs"></i>
        </div>
        <span>Quản Trị Hệ Thống</span>
      </router-link>
    </div>

    <div class="w-full max-w-[960px] flex flex-col items-center">
      
      <!-- Top Header -->
      <div class="text-center mb-8 md:mb-12 animate-in">
        <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs mb-3 tracking-wider uppercase shadow-xs">
          <span class="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></span>
          <span>NY Tagging System V2.0</span>
        </div>
        
        <h1 class="text-4xl md:text-5xl font-black tracking-tight text-slate-900 mb-2">
          Chọn Khách Hàng
        </h1>
        
        <p class="text-slate-500 font-medium text-sm md:text-base max-w-[480px] mx-auto">
          Chọn trạm đóng gói phù hợp với quy trình sản xuất của mã hàng
        </p>
      </div>

      <!-- Customer Selection Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-[840px]">
        
        <!-- Card 1: Khách hàng UI (item_scan) -->
        <div
          @click="selectCustomer('UI')"
          class="group relative bg-white hover:bg-slate-50/80 border-2 border-slate-200/90 hover:border-blue-500 rounded-3xl p-6 md:p-8 cursor-pointer transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-blue-500/10 hover:-translate-y-1.5 flex flex-col justify-between min-h-[290px] overflow-hidden"
        >
          <!-- Subtle watermark icon -->
          <div class="absolute -right-6 -bottom-6 opacity-5 group-hover:opacity-10 transition-opacity duration-500 text-blue-600 text-9xl pointer-events-none">
            <i class="fas fa-barcode"></i>
          </div>

          <div>
            <div class="flex items-center justify-between mb-5">
              <div class="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 group-hover:scale-110 group-hover:bg-blue-600 group-hover:text-white transition-all duration-300 shadow-md shadow-blue-500/10">
                <i class="fas fa-barcode text-2xl"></i>
              </div>
              <span class="px-3 py-1 text-xs font-black rounded-full bg-blue-50 text-blue-700 border border-blue-200 uppercase tracking-wider">
                Quét Sê-ri Con
              </span>
            </div>

            <h2 class="text-2xl font-black text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
              {{ uiCustomerName }}
            </h2>
            <p class="text-slate-600 text-sm leading-relaxed mb-4">
              Quy trình đóng gói quét từng mã sê-ri sản phẩm con vào thùng theo Job Order ERP. Mẫu tem Standard / Detailed.
            </p>
          </div>

          <div class="flex items-center text-blue-600 font-black text-sm gap-2 group-hover:gap-3 transition-all pt-4 border-t border-slate-100">
            <span>Mở Trạm Đóng Hàng</span>
            <i class="fas fa-arrow-right text-xs transition-transform group-hover:translate-x-1"></i>
          </div>
        </div>

        <!-- Card 2: Khách hàng A11 (weight_scale) -->
        <div
          @click="selectCustomer('A11')"
          class="group relative bg-white hover:bg-slate-50/80 border-2 border-slate-200/90 hover:border-emerald-500 rounded-3xl p-6 md:p-8 cursor-pointer transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-emerald-500/10 hover:-translate-y-1.5 flex flex-col justify-between min-h-[290px] overflow-hidden"
        >
          <!-- Subtle watermark icon -->
          <div class="absolute -right-6 -bottom-6 opacity-5 group-hover:opacity-10 transition-opacity duration-500 text-emerald-600 text-9xl pointer-events-none">
            <i class="fas fa-weight-scale"></i>
          </div>

          <div>
            <div class="flex items-center justify-between mb-5">
              <div class="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 group-hover:scale-110 group-hover:bg-emerald-600 group-hover:text-white transition-all duration-300 shadow-md shadow-emerald-500/10">
                <i class="fas fa-weight-scale text-2xl"></i>
              </div>
              <span class="px-3 py-1 text-xs font-black rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase tracking-wider">
                Đóng Gói Theo Cân
              </span>
            </div>

            <h2 class="text-2xl font-black text-slate-900 mb-2 group-hover:text-emerald-600 transition-colors">
              {{ a11CustomerName }}
            </h2>
            <p class="text-slate-600 text-sm leading-relaxed mb-4">
              Quy trình đóng gói theo cân điện tử (RS-232), kiểm soát dung sai trọng lượng, nhập PO/LOT và in tem tiêu chuẩn A11.
            </p>
          </div>

          <div class="flex items-center text-emerald-600 font-black text-sm gap-2 group-hover:gap-3 transition-all pt-4 border-t border-slate-100">
            <span>Mở Trạm Cân Đóng Hàng</span>
            <i class="fas fa-arrow-right text-xs transition-transform group-hover:translate-x-1"></i>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import catalogApi from '../features/catalog/api';
import type { Customer } from '../types/api';

const router = useRouter();
const customers = ref<Customer[]>([]);
const isLoading = ref(true);

const fetchCustomers = async () => {
  try {
    isLoading.value = true;
    const res = await catalogApi.getCustomers();
    customers.value = res.data || [];
  } catch (error) {
    console.error('Failed to load customers:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchCustomers();
});

const uiCustomerName = computed(() => {
  const found = customers.value.find(c => c.code?.trim().toUpperCase() === 'UI');
  return found?.name || 'Khách Hàng UI';
});

const a11CustomerName = computed(() => {
  const found = customers.value.find(c => {
    const code = c.code?.trim().toUpperCase();
    return code === 'A11' || code === 'UX';
  });
  return found?.name || 'Khách Hàng A11';
});

const selectCustomer = (code: 'UI' | 'A11' | 'UX') => {
  localStorage.setItem('selected_customer', code === 'UX' ? 'A11' : code);
  if (code === 'UI') {
    router.push('/packing/ui');
  } else {
    router.push('/packing/a11');
  }
};
</script>
