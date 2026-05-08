<template>
  <div class="mb-4">
    <div class="flex gap-3 items-start">
      <textarea 
        :value="scanBuffer"
        @input="$emit('update:scanBuffer', $event.target.value)"
        @keyup.enter="$emit('scan')"
        :placeholder="disabled ? placeholder : (!jobOrder ? t('packing.scan_prompt_job') : (awaitingNext ? t('packing.scan_prompt_overflow') : t('packing.scan_prompt_default')))"
        ref="scanInput"
        :disabled="disabled"
        class="flex-1 min-w-0 px-4 py-3.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-slate-900 text-[1.15rem] font-bold text-center mb-2 transition-all resize-none min-h-[58px] flex items-center outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 shrink-0"
        :class="{ 
          'bg-slate-100 border-slate-300 text-slate-500 cursor-not-allowed': !jobOrder || disabled, 
          'bg-orange-50 border-orange-500 text-orange-900 focus:border-orange-600 focus:bg-orange-50 focus:ring-orange-500/15': awaitingNext && jobOrder && !disabled 
        }"
        rows="1"
      ></textarea>
      <button 
        v-if="awaitingNext" 
        @click="$emit('next-carton')" 
        class="px-6 h-[58px] bg-linear-to-br from-emerald-500 to-emerald-600 text-white border-none rounded-xl font-bold cursor-pointer flex items-center gap-2 whitespace-nowrap shadow-[0_4px_12px_rgba(16,185,129,0.3)] transition-all hover:-translate-y-0.5 hover:shadow-[0_6px_15px_rgba(16,185,129,0.4)] hover:bg-linear-to-br hover:from-emerald-600 hover:to-emerald-700 animate-pulse-gentle"
        :disabled="disabled"
        :title="t('packing.next_carton_title')"
      >
        <i class="fas fa-plus-circle"></i> {{ t('packing.next_carton') }}
      </button>
      <button 
        v-else-if="allowPartial && scannedCount > 0 && jobOrder" 
        @click="$emit('pack-now')" 
        class="px-6 h-[58px] bg-linear-to-br from-blue-500 to-blue-600 text-white border-none rounded-xl font-bold cursor-pointer flex items-center gap-2 whitespace-nowrap shadow-[0_4px_12px_rgba(59,130,246,0.3)] transition-all hover:-translate-y-0.5 hover:shadow-[0_6px_15px_rgba(59,130,246,0.4)] hover:bg-linear-to-br hover:from-blue-600 hover:to-blue-700"
        :disabled="disabled"
        :title="t('packing.pack_now_title')"
      >
        <i class="fas fa-box-open"></i> {{ t('packing.pack_now') }}
      </button>
    </div>
    <p class="text-center text-slate-400 text-[0.85rem]" v-if="jobOrder && !awaitingNext && !disabled">{{ t('packing.waiting_scanner') }}</p>
    <p class="text-center text-[0.85rem] text-orange-600 font-bold" v-else-if="awaitingNext && !disabled">{{ t('packing.box_complete_hint') }}</p>
    <p class="text-center text-[0.85rem] text-rose-500 font-bold" v-else-if="!jobOrder && !disabled">{{ t('packing.fill_job_order_hint') }}</p>
    <p class="text-center text-[0.85rem] text-rose-500 font-bold" v-else-if="disabled && placeholder.includes('AGENT')">{{ t('packing.agent_offline_hint') }}</p>

    <!-- Overflow Scans Area (excess scans after box full) -->
    <div v-if="overflowScans.length > 0" class="mt-4 bg-orange-50 border-2 border-orange-400 rounded-xl overflow-hidden shadow-[0_4px_12px_rgba(249,115,22,0.15)] transition-opacity animate-in">
      <div class="px-3.5 py-2.5 bg-linear-to-br from-orange-50 to-orange-100 border-b border-orange-400 flex justify-between items-center text-orange-800 text-[0.85rem] font-bold">
        <span><i class="fas fa-exclamation-triangle text-orange-600 mr-1.5"></i> {{ t('packing.overflow_title', { count: overflowScans.length }) }}</span>
        <button @click="$emit('clear-overflow')" class="bg-transparent border border-orange-400 text-orange-800 px-2 py-0.5 rounded-md text-[0.7rem] cursor-pointer transition-all hover:bg-orange-100">{{ t('packing.clear') }}</button>
      </div>
      <div class="max-h-[200px] overflow-y-auto p-2">
        <div v-for="(item, idx) in overflowScans" :key="idx" class="flex justify-between items-center px-3 py-2 bg-white rounded-lg mb-1 border border-orange-200 border-l-4 border-l-orange-500 transition-all hover:bg-amber-50">
          <div class="flex items-center gap-2.5">
            <span class="text-[0.7rem] font-extrabold text-orange-700 bg-orange-100 px-1.5 py-0.5 rounded-sm">#{{ idx + 1 }}</span>
            <span class="font-mono font-bold text-orange-950 text-[0.95rem]">{{ item.sn }}</span>
          </div>
          <span class="text-[0.75rem] text-slate-400">{{ item.time }}</span>
        </div>
      </div>
    </div>

    <!-- Invalid Scans Area -->
    <div v-if="invalidScans.length > 0" class="mt-5 bg-rose-50 border border-rose-200 rounded-xl overflow-hidden shadow-md transition-opacity animate-in">
      <div class="px-3 py-2 bg-white border-b border-rose-200 flex justify-between items-center text-rose-700 text-[0.85rem] font-bold">
        <span><i class="fas fa-exclamation-circle mr-1.5"></i> {{ t('packing.invalid_scans_title') }}</span>
        <button @click="$emit('clear-invalid')" class="bg-transparent border border-rose-200 text-rose-700 px-2 py-0.5 rounded-md text-[0.7rem] cursor-pointer transition-all hover:bg-rose-50 hover:border-rose-700">{{ t('packing.clear') }}</button>
      </div>
      <div class="max-h-[150px] overflow-y-auto p-2">
        <div v-for="(err, idx) in [...invalidScans].reverse()" :key="idx" class="flex justify-between items-center px-2.5 py-1.5 bg-white rounded-md mb-1 border border-rose-100 border-l-4"
          :class="{
            'border-l-orange-500': err.type === 'pattern',
            'border-l-purple-500': err.type === 'duplicate',
            'border-l-rose-500': !['pattern', 'duplicate'].includes(err.type)
          }"
        >
          <div class="flex items-center">
            <span class="font-mono font-semibold text-rose-600">{{ err.sn }}</span>
            <span class="text-[0.7rem] px-1.5 py-0.5 rounded-sm ml-2.5 font-bold uppercase tracking-wider"
              :class="{
                'bg-orange-100 text-orange-800': err.type === 'pattern',
                'bg-purple-100 text-purple-800': err.type === 'duplicate',
                'bg-rose-200 text-rose-900': !['pattern', 'duplicate'].includes(err.type)
              }"
            >{{ err.reason }}</span>
          </div>
          <span class="text-[0.75rem] text-slate-400">{{ item?.time || err.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
  scanBuffer: { type: String, default: '' },
  jobOrder: { type: String, default: '' },
  awaitingNext: { type: Boolean, default: false },
  invalidScans: { type: Array, default: () => [] },
  overflowScans: { type: Array, default: () => [] },
  allowPartial: { type: Boolean, default: false },
  scannedCount: { type: Number, default: 0 },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: '' }
});

defineEmits(['update:scanBuffer', 'scan', 'next-carton', 'pack-now', 'clear-invalid', 'clear-overflow']);

const scanInput = ref(null);

const focusScan = () => {
  if (scanInput.value) scanInput.value.focus({ preventScroll: true });
};

defineExpose({ focusScan });
</script>
