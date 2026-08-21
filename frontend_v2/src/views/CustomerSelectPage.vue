<template>
  <div class="min-h-screen w-full p-4 md:p-8 flex items-center justify-center bg-slate-100 text-slate-900 selection:bg-indigo-600 selection:text-white">
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
        
        <!-- Card 1: Khách hàng UI -->
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
              Khách Hàng UI
            </h2>
            <p class="text-slate-600 text-sm leading-relaxed mb-4">
              Quy trình đóng gói quét từng mã sê-ri sản phẩm con vào thùng theo Job Order ERP. Mẫu tem Standard / Detailed.
            </p>
          </div>

          <div class="flex items-center text-blue-600 font-black text-sm gap-2 group-hover:gap-3 transition-all pt-4 border-t border-slate-100">
            <span>Mở Trạm Đóng Hàng UI</span>
            <i class="fas fa-arrow-right text-xs transition-transform group-hover:translate-x-1"></i>
          </div>
        </div>

        <!-- Card 2: Khách hàng UX -->
        <div
          @click="selectCustomer('UX')"
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
              Khách Hàng UX
            </h2>
            <p class="text-slate-600 text-sm leading-relaxed mb-4">
              Quy trình đóng gói theo cân điện tử (RS-232), kiểm soát dung sai trọng lượng, nhập PO/LOT và in tem tiêu chuẩn A11.
            </p>
          </div>

          <div class="flex items-center text-emerald-600 font-black text-sm gap-2 group-hover:gap-3 transition-all pt-4 border-t border-slate-100">
            <span>Mở Trạm Cân Đóng Hàng UX</span>
            <i class="fas fa-arrow-right text-xs transition-transform group-hover:translate-x-1"></i>
          </div>
        </div>
      </div>

      <!-- Admin Access Link -->
      <div class="mt-10 text-center">
        <router-link
          to="/admin"
          class="text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors flex items-center gap-1.5 justify-center py-1.5 px-3 rounded-lg hover:bg-slate-200/60"
        >
          <i class="fas fa-shield-alt text-[0.85rem] text-slate-400"></i>
          <span>Trang Quản Trị Hệ Thống (Admin)</span>
        </router-link>
      </div>

    </div>
  </div>
</template>


<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const selectCustomer = (code: 'UI' | 'UX') => {
  localStorage.setItem('selected_customer', code);
  if (code === 'UI') {
    router.push('/packing/ui');
  } else {
    router.push('/packing/ux');
  }
};
</script>
