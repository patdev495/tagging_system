<template>
  <div class="flex flex-col gap-3 mb-4 px-5 py-3 bg-linear-to-br from-slate-50 to-white rounded-2xl border border-slate-100 shadow-sm">
    <div class="flex items-center gap-4 w-full pb-3 border-b border-dashed border-slate-300">
      <button @click="$emit('back')" class="w-9 h-9 flex items-center justify-center bg-white border border-slate-200 text-slate-500 rounded-[10px] cursor-pointer transition-all duration-300 ease-out shadow-xs hover:bg-slate-50 hover:text-blue-600 hover:border-blue-500 hover:-translate-x-1 hover:shadow-blue-500/10" :title="t('packing.back')">
        <i class="fas fa-arrow-left"></i>
      </button>
      <div class="flex-1">
        <h2 class="m-0 text-[1.25rem] font-extrabold text-slate-900 tracking-tight">{{ product.item_name }}</h2>
        <div class="flex gap-2 mt-1">
          <span class="inline-flex items-center px-2.5 py-0.5 border border-slate-200 rounded-md text-[0.75rem] font-semibold text-slate-600 bg-slate-50">UPC: {{ product.upc }}</span>
          <span class="inline-flex items-center px-2.5 py-0.5 border border-slate-200 rounded-md text-[0.75rem] font-semibold text-slate-600 bg-slate-50">{{ t('packing.target') }}: {{ product.packed_qty }}</span>
        </div>
      </div>
    </div>
    
    <div class="flex flex-wrap gap-3 items-start w-full">
      <div class="flex flex-col gap-1 flex-1 min-w-[180px] max-w-[300px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.job_order') }}</label>
        <input 
          :value="jobOrder" 
          @input="$emit('update:jobOrder', $event.target.value)"
          :placeholder="t('packing.job_order_placeholder')" 
          class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-[0.95rem] font-bold text-slate-800 outline-none transition-all duration-200 ease-out focus:border-blue-500 focus:ring-4 focus:ring-blue-500/8 focus:shadow-sm"
          ref="jobOrderInput"
          @keyup.enter="$emit('focus-scan')"
        />
      </div>
      <div class="flex flex-col gap-1 flex-none w-20">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.origin') }}</label>
        <select 
          :value="cartonOrigin"
          @change="$emit('update:cartonOrigin', $event.target.value); $emit('focus-scan')"
          class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-[0.95rem] font-bold text-slate-800 outline-none transition-all duration-200 ease-out focus:border-blue-500 focus:ring-4 focus:ring-blue-500/8 focus:shadow-sm"
        >
          <option value="VN">VN</option>
          <option value="CN">CN</option>
        </select>
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[180px] max-w-[250px]">
        <div class="relative flex items-center">
          <input 
            :value="customSN"
            @input="$emit('update:customSN', $event.target.value)"
            type="number"
            :placeholder="suggestedSNValue || '00001'" 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-[0.95rem] font-bold text-slate-800 outline-none transition-all duration-200 ease-out focus:border-blue-500 focus:ring-4 focus:ring-blue-500/8 focus:shadow-sm pr-[70px]!"
            :class="{ 
              'bg-emerald-50! border-emerald-500! text-emerald-600! cursor-default': !isSNManual, 
              'border-rose-500! bg-rose-50! ring-rose-500/10!': isSNManual && snExists 
            }"
            :readonly="!isSNManual"
            @keyup.enter="$emit('focus-scan')"
            ref="snInput"
          />
          <button 
            class="absolute right-1 top-1 bottom-1 border-none bg-slate-200 text-slate-500 text-[0.65rem] font-extrabold px-2 rounded-md cursor-pointer transition-all hover:scale-105" 
            :class="{ 'bg-emerald-500! text-white!': !isSNManual }"
            @click="toggleMode"
            :title="!isSNManual ? t('packing.switch_manual') : t('packing.switch_auto')"
          >
            {{ !isSNManual ? t('packing.auto') : t('packing.manual') }}
          </button>
        </div>
        <div class="text-[0.7rem] text-emerald-500 mt-1 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-100" v-if="snPreview">
           {{ t('packing.preview') }}: <strong class="font-mono text-[0.8rem]" :class="{ 'text-rose-500!': snExists }">{{ snExists ? '⚠️ ' + t('packing.sn_exists_short') : snPreview }}</strong>
        </div>
      </div>
      <div class="flex flex-col gap-1 flex-none w-[90px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.sn_pattern') }}</label>
        <input 
          :value="snPattern"
          @input="$emit('update:snPattern', $event.target.value)"
          placeholder="e.g. AS" 
          class="w-full px-3 py-2 bg-white rounded-lg text-[0.95rem] font-bold outline-none transition-all duration-200 ease-out focus:ring-4 focus:shadow-sm border-blue-300 text-blue-800 focus:border-blue-500 focus:ring-blue-500/8 focus:bg-blue-50!"
          @keyup.enter="$emit('focus-scan')"
        />
      </div>
      <div class="flex flex-col gap-1 flex-none w-[90px]">
        <label class="text-[0.7rem] text-slate-500 font-bold uppercase tracking-wider pl-0.5">{{ t('packing.manual_date') }}</label>
        <input 
          :value="customYYMM"
          @input="$emit('update:customYYMM', $event.target.value)"
          placeholder="e.g. 2604" 
          maxlength="4"
          class="w-full px-3 py-2 bg-white border rounded-lg text-[0.95rem] font-bold outline-none transition-all duration-200 ease-out focus:ring-4 focus:shadow-sm border-amber-500 text-amber-800 focus:border-amber-600 focus:bg-amber-50! focus:ring-amber-500/8"
          @keyup.enter="$emit('focus-scan')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Product } from '../../../types/api';

const { t } = useI18n();

const props = defineProps<{
  product: Product;
  jobOrder: string;
  cartonOrigin: string;
  customSN: string;
  isSNManual: boolean;
  snPattern: string;
  customYYMM: string;
  suggestedSNValue: number;
  snPreview: string;
  snExists: boolean;
}>();

const emit = defineEmits<{
  (e: 'back'): void;
  (e: 'focus-scan'): void;
  (e: 'update:jobOrder', val: string): void;
  (e: 'update:cartonOrigin', val: string): void;
  (e: 'update:customSN', val: string): void;
  (e: 'update:isSNManual', val: boolean): void;
  (e: 'update:snPattern', val: string): void;
  (e: 'update:customYYMM', val: string): void;
}>();

const jobOrderInput = ref<HTMLInputElement | null>(null);
const snInput = ref<HTMLInputElement | null>(null);

const focusJobOrder = () => {
  if (jobOrderInput.value) jobOrderInput.value.focus({ preventScroll: true });
};

const toggleMode = () => {
  if (!props.isSNManual) {
    // Switch to manual
    emit('update:isSNManual', true);
    emit('update:customSN', props.suggestedSNValue.toString());
    nextTick(() => { if (snInput.value) snInput.value.focus(); });
  } else {
    // Switch to auto
    emit('update:isSNManual', false);
    emit('update:customSN', '');
  }
};

defineExpose({ focusJobOrder });
</script>
