<template>
  <div 
    v-if="show" 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in"
  >
    <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full p-6 border border-slate-100 flex flex-col gap-5">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div class="flex items-center gap-2.5">
          <i class="fas fa-boxes text-indigo-600 text-lg"></i>
          <h2 class="font-bold text-lg text-slate-900">Chọn Sản Phẩm Khách Hàng A11</h2>
        </div>
        <div class="flex items-center gap-1.5">
          <button 
            @click="$emit('reload')" 
            :disabled="isLoading" 
            class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-slate-100 transition-all cursor-pointer"
            title="Làm mới danh sách sản phẩm từ CSDL"
          >
            <i :class="['fas fa-rotate', isLoading ? 'animate-spin text-indigo-600' : '']"></i>
          </button>
          <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg">
            <i class="fas fa-times text-lg"></i>
          </button>
        </div>
      </div>

      <div class="space-y-3 max-h-[60vh] overflow-y-auto">
        <div
          v-for="p in products"
          :key="p.id"
          @click="$emit('select', p)"
          :class="[
            'p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between',
            selectedProduct?.id === p.id
              ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
              : 'border-slate-200 hover:border-indigo-200 hover:bg-slate-50'
          ]"
        >
          <div>
            <div class="flex items-center gap-2">
              <h4 class="font-black text-base text-slate-900 font-mono">{{ p.item_name }}</h4>
              <span class="px-2 py-0.5 rounded-md bg-indigo-100 text-indigo-700 text-xs font-bold">{{ p.packed_qty }} PCS</span>
            </div>
            <p class="text-xs text-slate-500 mt-1">
              Mfr P/N: <strong class="text-slate-700">{{ p.mfr_pn || 'NYS5998' }}</strong> | 
              Tiền tố: <strong class="text-slate-700">{{ p.pkg_prefix || 'VHK0010237' }}</strong>
            </p>
            <p class="text-xs text-emerald-700 font-mono mt-0.5">
              Dải trọng lượng: {{ p.min_weight?.toFixed(3) || '12.300' }}kg - {{ p.max_weight?.toFixed(3) || '12.700' }}kg
            </p>
          </div>
          <div v-if="selectedProduct?.id === p.id" class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs">
            <i class="fas fa-check"></i>
          </div>
        </div>
      </div>

      <div class="flex justify-end pt-2">
        <button
          @click="$emit('close')"
          class="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-all cursor-pointer"
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
