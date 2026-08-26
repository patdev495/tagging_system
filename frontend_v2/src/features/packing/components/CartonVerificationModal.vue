<template>
  <div v-if="show" class="fixed inset-0 bg-black/70 backdrop-blur-md flex justify-center items-center z-[2000]">
    <div class="w-[95%] max-w-[600px] bg-white rounded-[24px] overflow-hidden shadow-2xl flex flex-col animate-in border border-slate-100" :class="{ 'ring-4 ring-rose-500/20 border-rose-300 animate-shake': verificationError }">
      
      <!-- Header -->
      <div class="flex justify-between items-center px-8 pt-6 pb-4 border-b border-slate-100">
        <div class="flex items-center gap-3 text-slate-800">
          <i class="fas fa-barcode text-[1.5rem] text-blue-600 animate-pulse"></i>
          <h2 class="m-0 text-[1.5rem] font-black text-slate-900">{{ t('packing.verification_title', 'Quét Xác Thực Mã Thùng') }}</h2>
        </div>
      </div>

      <!-- Body -->
      <div class="px-8 py-6 flex-1">
        <p class="text-slate-500 text-[0.95rem] mb-6">
          {{ t('packing.verification_desc', 'Vui lòng dùng máy quét barcode quét lại mã vạch trên con tem vừa in để hoàn tất.') }}
        </p>

        <!-- Expected SN display -->
        <div class="mb-6">
          <span class="text-[0.75rem] uppercase tracking-wider text-slate-400 font-bold block mb-2">{{ t('packing.expected_sn', 'Sê-ri Thùng Cần Khớp') }}</span>
          <div class="bg-slate-50 border border-slate-200 rounded-2xl p-5 text-center shadow-inner-sm">
            <span class="font-mono text-[2rem] font-bold text-slate-900 select-all tracking-wider">
              {{ carton?.carton_sn }}
            </span>
          </div>
        </div>

        <!-- Product info details -->
        <div class="grid grid-cols-2 gap-4 mb-6 bg-slate-50/50 p-4 rounded-xl border border-slate-100">
          <div>
            <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">{{ t('admin.product', 'Sản phẩm') }}</span>
            <span class="text-slate-700 font-medium text-[0.85rem] truncate block">{{ currentProduct?.item_name || 'N/A' }}</span>
          </div>
          <div>
            <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">{{ t('packing.job_order', 'Công lệnh') }}</span>
            <span class="text-slate-700 font-medium text-[0.85rem]">{{ carton?.job_order || 'N/A' }}</span>
          </div>
          <div>
            <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">{{ t('print.items', 'Số con') }}</span>
            <span class="text-slate-700 font-medium text-[0.85rem]">{{ carton?.items?.length || scannedCount }} pcs</span>
          </div>
          <div>
            <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">Status</span>
            <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[0.75rem] font-semibold bg-amber-50 text-amber-700 border border-amber-200/60 mt-0.5">
              <i class="fas fa-print"></i> PRINTED
            </span>
          </div>
        </div>

        <!-- Scan input field -->
        <div class="relative">
          <div class="border rounded-xl p-1 flex gap-2 bg-white transition-all duration-300" 
               :class="verificationError ? 'border-rose-500 shadow-[0_0_0_4px_rgba(239,68,68,0.1)]' : 'border-slate-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10'">
            <div class="flex-1 flex items-center pl-3">
              <i class="fas fa-barcode text-slate-400 text-[1.1rem]"></i>
              <input 
                ref="verificationInputRef" 
                v-model="verificationScanBuffer" 
                @keydown.enter.prevent="handleScan" 
                :placeholder="t('packing.verification_placeholder', 'Quét barcode mã thùng...')" 
                class="w-full border-none px-3.5 py-3 text-[1rem] text-slate-800 outline-none bg-transparent font-mono" 
                autocomplete="off"
              />
            </div>
          </div>
          
          <!-- Wrong scan error popup -->
          <div v-if="verificationError" class="absolute left-0 right-0 -bottom-10 text-center text-rose-600 text-[0.85rem] font-bold animate-in">
            <i class="fas fa-exclamation-circle mr-1"></i> {{ t('packing.verification_error', 'Mã quét không khớp với thùng hiện tại!') }}
          </div>
        </div>
      </div>

      <!-- Footer with home button -->
      <div class="px-8 py-5 bg-slate-50 border-t border-slate-100 flex justify-between items-center gap-3">
        <button 
          @click="$emit('resetSession')" 
          class="bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 px-4 py-2 rounded-xl text-[0.85rem] font-semibold cursor-pointer transition-all flex items-center gap-1.5 active:scale-95"
        >
          <i class="fas fa-home text-slate-500"></i>
          <span>{{ t('packing.back_home', 'Về Trang Chủ') }}</span>
        </button>
        
        <span class="text-slate-400 text-[0.85rem] flex items-center gap-1.5">
          <i class="fas fa-keyboard animate-pulse"></i> {{ t('packing.waiting_scanner', 'Đang đợi máy quét barcode...') }}
        </span>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Carton, Product } from '../../../types/api';

const props = defineProps<{
  show: boolean;
  carton: (Carton & { status?: string, items?: { item_sn: string }[] }) | null;
  currentProduct: Product | null;
  scannedCount?: number;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'verified', carton: Carton): void;
  (e: 'resetSession'): void;
  (e: 'scanAlert'): void;
}>();

const { t } = useI18n();
const verificationScanBuffer = ref<string>('');
const verificationInputRef = ref<HTMLInputElement | null>(null);
const verificationError = ref<boolean>(false);

const focusInput = () => {
  nextTick(() => {
    if (verificationInputRef.value) {
      verificationInputRef.value.focus();
    }
  });
};

watch(() => props.show, (newVal) => {
  if (newVal) {
    verificationScanBuffer.value = '';
    verificationError.value = false;
    focusInput();
  }
});

const handleScan = () => {
  const scannedVal = verificationScanBuffer.value.trim();
  if (!scannedVal || !props.carton) return;

  const expectedVal = props.carton.carton_sn.trim();
  if (scannedVal.toLowerCase() === expectedVal.toLowerCase()) {
    verificationError.value = false;
    emit('verified', props.carton);
  } else {
    emit('scanAlert');
    verificationError.value = true;
    verificationScanBuffer.value = '';
    setTimeout(() => {
      verificationError.value = false;
    }, 1500);
  }
};

defineExpose({
  focusInput,
});
</script>
