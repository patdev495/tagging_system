<template>
  <div class="flex-1 flex flex-col justify-center items-center py-16 md:py-24 animate-in">
    <div class="w-full max-w-[550px] space-y-6">
      <div class="flex justify-between items-center px-2">
        <span class="text-[0.9rem] text-slate-500 font-medium">
          {{ t('packing.job_order', 'Công lệnh') }}: <strong class="font-mono text-slate-800">{{ jobOrder }}</strong>
        </span>
        <button @click="$emit('changeJobOrder')" class="text-blue-600 hover:text-blue-800 border-none bg-transparent font-bold cursor-pointer text-[0.9rem] flex items-center gap-1.5">
          <i class="fas fa-exchange-alt"></i> {{ t('packing.change_job_order', 'Đổi công lệnh') }}
        </button>
      </div>

      <!-- Product Card -->
      <div 
        @click="$emit('enterScanning')"
        class="bg-linear-to-br from-slate-900 to-slate-800 text-white rounded-[24px] p-8 shadow-2xl hover:scale-[1.02] cursor-pointer transition-all duration-300 relative overflow-hidden group border border-slate-700/30"
      >
        <div class="absolute -right-10 -bottom-10 opacity-5 text-[10rem] pointer-events-none group-hover:scale-110 transition-transform duration-500">
          <i class="fas fa-box-open"></i>
        </div>
        
        <div class="flex justify-between items-start mb-6">
          <span class="bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-xl px-3 py-1 text-[0.8rem] font-bold uppercase tracking-wider">
            Product Info
          </span>
          <div class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white/80 group-hover:bg-white/20 transition-colors">
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>

        <h3 class="text-[1.8rem] font-black leading-tight mb-2 tracking-wide text-white group-hover:text-blue-200 transition-colors">
          {{ jobOrderDetails?.product.item_name }}
        </h3>
        
        <p class="text-slate-400 font-mono text-[1rem] mb-6">
          UPC: {{ jobOrderDetails?.product.upc || 'N/A' }}
        </p>

        <div class="grid grid-cols-3 gap-2 border-t border-white/10 pt-6">
          <div>
            <span class="text-slate-400 text-[0.8rem] uppercase font-bold block mb-1">Quy cách / Thùng</span>
            <span class="text-[1.3rem] font-black text-white">QTY: {{ jobOrderDetails?.product.packed_qty }}</span>
          </div>
          <div class="border-x border-white/10 px-2 text-center">
            <span class="text-slate-400 text-[0.8rem] uppercase font-bold block mb-1">{{ t('packing.total_qty', 'Tổng Số Lượng') }}</span>
            <span class="text-[1.3rem] font-black text-emerald-400">{{ jobOrderDetails?.total_qty }} con</span>
          </div>
          <div class="text-right">
            <span class="text-slate-400 text-[0.8rem] uppercase font-bold block mb-1">{{ t('packing.total_cartons', 'Tổng Số Thùng') }}</span>
            <span class="text-[1.3rem] font-black text-blue-400">{{ jobOrderDetails?.total_cartons }} Thùng</span>
          </div>
        </div>
      </div>
      
      <p class="text-center text-slate-400 text-[0.85rem] italic">
        Bấm vào thẻ sản phẩm ở trên để vào giao diện quét mã
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { JobOrderDetails } from '../../../types/api';

defineProps<{
  jobOrder: string;
  jobOrderDetails: JobOrderDetails | null;
}>();

defineEmits<{
  (e: 'changeJobOrder'): void;
  (e: 'enterScanning'): void;
}>();

const { t } = useI18n();
</script>
