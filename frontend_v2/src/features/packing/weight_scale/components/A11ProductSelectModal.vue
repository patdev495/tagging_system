<template>
  <div 
    v-if="show" 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 select-none animate-in"
    role="dialog"
    aria-modal="true"
  >
    <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-5 border border-slate-300 flex flex-col gap-4">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-3 border-b border-slate-200">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
            <i class="fas fa-boxes text-sm"></i>
          </div>
          <div>
            <h2 class="font-bold text-base text-slate-900 leading-tight">Chọn Sản Phẩm Khách Hàng Erro</h2>
            <p class="text-xs text-slate-500 m-0">Chọn mã sản phẩm để thiết lập dải trọng lượng cân</p>
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <button 
            @click="$emit('reload')" 
            :disabled="isLoading" 
            class="w-8 h-8 rounded-lg border border-slate-300 text-slate-600 hover:text-emerald-700 hover:bg-slate-50 flex items-center justify-center transition-colors cursor-pointer disabled:opacity-50"
            title="Làm mới danh sách sản phẩm từ CSDL"
          >
            <i :class="['fas fa-rotate text-xs', isLoading ? 'animate-spin text-emerald-600' : '']"></i>
          </button>
          <button 
            @click="$emit('close')" 
            class="w-8 h-8 rounded-lg border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-50 flex items-center justify-center transition-colors cursor-pointer"
            title="Đóng (Esc)"
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        </div>
      </div>

      <!-- Products List or States -->
      <div class="space-y-2 max-h-[60vh] overflow-y-auto">
        <!-- Loading State -->
        <div v-if="isLoading" class="py-10 flex flex-col items-center justify-center text-slate-500 gap-2">
          <i class="fas fa-spinner fa-spin text-2xl text-emerald-600"></i>
          <span class="text-xs font-semibold">Đang tải danh sách sản phẩm Erro từ CSDL...</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="!products || products.length === 0" class="py-8 px-4 text-center bg-slate-50 rounded-xl border border-slate-200">
          <div class="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 text-slate-400 flex items-center justify-center mx-auto mb-2">
            <i class="fas fa-box-open text-lg"></i>
          </div>
          <h4 class="font-bold text-sm text-slate-800 mb-1">Chưa có sản phẩm Erro nào</h4>
          <p class="text-xs text-slate-500 max-w-xs mx-auto leading-relaxed mb-3">
            Hệ thống chưa tìm thấy sản phẩm nào được gán cho Khách hàng Erro trong cơ sở dữ liệu.
          </p>
          <button 
            @click="$emit('reload')"
            class="px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-bold text-slate-700 hover:bg-slate-50 cursor-pointer inline-flex items-center gap-1.5"
          >
            <i class="fas fa-rotate text-[10px]"></i>
            <span>Tải Lại CSDL</span>
          </button>
        </div>

        <!-- List Items -->
        <div
          v-else
          v-for="p in products"
          :key="p.id"
          @click="$emit('select', p)"
          :class="[
            'p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between',
            selectedProduct?.id === p.id
              ? 'border-emerald-600 bg-emerald-50/70 shadow-xs'
              : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
          ]"
        >
          <div>
            <div class="flex items-center gap-2">
              <h4 class="font-black text-sm md:text-base text-slate-900 font-barcode-mono">{{ p.item_name }}</h4>
              <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-bold">{{ p.packed_qty }} PCS</span>
            </div>
            <p class="text-xs text-slate-500 mt-1 mb-0.5">
              Mfr P/N: <strong class="text-slate-700 font-barcode-mono">{{ p.mfr_pn || 'NYS5998' }}</strong> | 
              Tiền tố: <strong class="text-slate-700 font-barcode-mono">{{ p.pkg_prefix || 'VHK0010237' }}</strong>
            </p>
            <p class="text-xs text-emerald-700 font-barcode-mono font-bold mt-0.5 mb-0">
              Dung sai cân: {{ p.min_weight?.toFixed(3) || '0.000' }}kg - {{ p.max_weight?.toFixed(3) || '0.000' }}kg
            </p>
          </div>
          <div v-if="selectedProduct?.id === p.id" class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs shrink-0">
            <i class="fas fa-check"></i>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end pt-2 border-t border-slate-200">
        <button
          @click="$emit('close')"
          class="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors cursor-pointer"
        >
          Đóng
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product } from '../../../../types/api';

defineProps<{
  show: boolean;
  products: Product[];
  selectedProduct: Product | null;
  isLoading?: boolean;
}>();

defineEmits<{
  (e: 'close'): void;
  (e: 'select', product: Product): void;
  (e: 'reload'): void;
}>();
</script>
