<template>
  <div class="flex flex-col gap-2 mb-3 px-3 md:px-5 py-2 md:py-3 bg-linear-to-br from-slate-50 to-white rounded-2xl border border-slate-100 shadow-sm">
    <div class="flex items-center gap-3 md:gap-4 w-full pb-2 border-b border-dashed border-slate-300">
      <button @click="$emit('back')" class="w-8 h-8 md:w-9 md:h-9 flex items-center justify-center bg-white border border-slate-200 text-slate-500 rounded-[10px] cursor-pointer transition-all duration-300 ease-out shadow-xs hover:bg-slate-50 hover:text-blue-600 hover:border-blue-500 hover:-translate-x-1 hover:shadow-blue-500/10" :title="t('packing.back')">
        <i class="fas fa-arrow-left text-[0.8rem] md:text-[1rem]"></i>
      </button>
      <div class="flex-1">
        <h2 class="m-0 text-[1.1rem] md:text-[1.25rem] font-extrabold text-slate-900 tracking-tight">{{ product.item_name }}</h2>
        <div class="flex gap-2 mt-0.5">
          <span class="inline-flex items-center px-2 py-0.5 border border-slate-200 rounded-md text-[0.7rem] font-semibold text-slate-600 bg-slate-50">UPC: {{ product.upc }}</span>
          <span class="inline-flex items-center px-2 py-0.5 border border-slate-200 rounded-md text-[0.7rem] font-semibold text-slate-600 bg-slate-50">{{ t('packing.target') }}: {{ product.packed_qty }}</span>
        </div>
      </div>
    </div>
    
    <div class="flex flex-wrap gap-2 md:gap-3 items-end w-full">
      <!-- Công Lệnh (Readonly) -->
      <div class="flex flex-col gap-1 flex-1 min-w-[150px] max-w-[200px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.job_order') }}</label>
        <div class="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-[0.95rem] font-mono font-bold text-slate-700 cursor-not-allowed select-all">
          {{ jobOrder }}
        </div>
      </div>

      <!-- Xuất Xứ (Origin) -->
      <div class="flex flex-col gap-1 flex-none w-20">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.origin') }}</label>
        <select 
          :value="cartonOrigin"
          @change="onOriginChange"
          class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-[0.95rem] font-bold text-slate-800 outline-none transition-all duration-200 ease-out focus:border-blue-500 focus:ring-4 focus:ring-blue-500/8 focus:shadow-sm"
        >
          <option value="VN">VN</option>
          <option value="CN">CN</option>
        </select>
      </div>

      <!-- Chọn Số Thùng (Box Number) -->
      <div class="flex flex-col gap-1 flex-1 min-w-[180px] max-w-[240px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">
          {{ t('packing.enter_box_number', { range: `1 -> ${totalBoxes || 0}` }) }}
        </label>
        <div class="relative flex items-center">
          <input 
            :value="boxNumberStr"
            @input="onBoxNumberInput"
            @keydown.enter.prevent="onBoxNumberSubmit"
            type="text"
            inputmode="numeric"
            placeholder="Ví dụ: 20" 
            class="w-full px-3 py-2 bg-white border rounded-lg text-[0.95rem] font-bold outline-none transition-all duration-200 ease-out focus:ring-4 focus:shadow-sm"
            :class="hasBoxNumberError 
              ? 'border-rose-500 text-rose-600 focus:border-rose-500 focus:ring-rose-500/10 shadow-[0_0_0_4px_rgba(239,68,68,0.1)] font-extrabold bg-rose-50/10' 
              : 'border-slate-200 text-slate-800 focus:border-blue-500 focus:ring-blue-500/8'"
            ref="boxInput"
          />
        </div>
        <div 
          v-if="hasBoxNumberError && boxNumberErrorText"
          class="text-[0.75rem] text-rose-600 mt-1 bg-rose-50 px-2.5 py-1.5 rounded-md border border-rose-100 font-bold flex items-center gap-1.5 animate-in"
        >
          <i class="fas fa-exclamation-circle text-rose-500"></i>
          <span>{{ boxNumberErrorText }}</span>
        </div>
        <div 
          v-else-if="snPreview"
          class="text-[0.7rem] text-emerald-500 mt-1 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-100"
        >
           Sê-ri Thùng: <strong class="font-mono text-[0.8rem]">{{ snPreview }}</strong>
        </div>
      </div>

      <!-- Tiền tố quét (Pattern) -->
      <div class="flex flex-col gap-1 flex-none w-[90px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.sn_pattern') }}</label>
        <input 
          :value="snPattern"
          @input="onPatternInput"
          placeholder="Ví dụ: AS" 
          class="w-full px-3 py-2 bg-white rounded-lg text-[0.95rem] font-bold outline-none transition-all duration-200 ease-out focus:ring-4 focus:shadow-sm border-blue-300 text-blue-800 focus:border-blue-500 focus:ring-blue-500/8 focus:bg-blue-50!"
          @keyup.enter="$emit('focus-scan')"
        />
      </div>

      <!-- Tháng/Năm tem (YYMM) -->
      <div class="flex flex-col gap-1 flex-none w-[90px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.manual_date') }}</label>
        <div class="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-[0.95rem] font-mono font-bold text-slate-600 text-center cursor-not-allowed">
          {{ customYYMM || '-' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Product } from '../../../types/api';

const { t } = useI18n();

const props = defineProps<{
  product: Product;
  jobOrder: string;
  cartonOrigin: string;
  boxNumberStr: string;
  totalBoxes: number;
  snPreview: string;
  snPattern: string;
  customYYMM: string;
  hasBoxNumberError?: boolean;
  boxNumberErrorText?: string;
}>();

const emit = defineEmits<{
  (e: 'back'): void;
  (e: 'focus-scan'): void;
  (e: 'update:cartonOrigin', val: string): void;
  (e: 'update:boxNumberStr', val: string): void;
  (e: 'update:snPattern', val: string): void;
  (e: 'submit-box-number'): void;
  (e: 'clear-box-error'): void;
}>();

const boxInput = ref<HTMLInputElement | null>(null);

const onOriginChange = (e: Event) => {
  emit('update:cartonOrigin', (e.target as HTMLSelectElement).value);
  emit('focus-scan');
};
const onBoxNumberInput = (e: Event) => {
  emit('update:boxNumberStr', (e.target as HTMLInputElement).value);
  emit('clear-box-error');
};
const onPatternInput = (e: Event) => emit('update:snPattern', (e.target as HTMLInputElement).value);

const onBoxNumberSubmit = () => {
  emit('submit-box-number');
};

const focusBoxInput = () => {
  if (boxInput.value) boxInput.value.focus();
};

defineExpose({ focusBoxInput });
</script>
