<template>
  <div v-if="show" class="fixed inset-0 bg-black/75 backdrop-blur-md flex justify-center items-center z-[2000] p-4">
    <div class="w-full max-w-[800px] bg-white rounded-[24px] overflow-hidden shadow-2xl flex flex-col border border-slate-100 max-h-[90vh]">
      <!-- Header -->
      <div class="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-slate-50">
        <div class="flex items-center gap-2.5 text-slate-800">
          <i class="fas fa-boxes text-[1.2rem] text-blue-600"></i>
          <h2 class="m-0 text-[1.2rem] font-black text-slate-900">{{ t('packing.carton_slots_title', 'Chi Tiết Vị Trí Thùng') }} ({{ totalCartons }} {{ t('packing.cartons_unit', 'thùng') }})</h2>
        </div>
        <button @click="$emit('close')" class="w-8 h-8 rounded-full bg-slate-200/50 hover:bg-slate-200 flex items-center justify-center text-slate-500 hover:text-slate-800 border-none cursor-pointer transition-colors">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1 bg-slate-50/30">
        <!-- Summary card inside modal -->
        <div class="flex justify-between items-center mb-4 bg-white p-4 rounded-xl border border-slate-100">
          <span class="text-[0.9rem] font-bold text-slate-600">
            {{ t('packing.job_order', 'Công lệnh') }}: <strong class="font-mono text-slate-900">{{ jobOrder }}</strong>
          </span>
          <span class="text-[0.9rem] font-bold text-slate-600">
            {{ t('packing.scanned', 'Đã quét') }}: <strong class="text-blue-600">{{ scannedCount }}</strong> / <strong>{{ totalCartons }}</strong>
          </span>
        </div>

        <!-- Slots Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <div
            v-for="slot in slots"
            :key="slot.id"
            @click="handleSlotClick(slot)"
            class="slot-card relative py-3.5 px-2 text-center rounded-xl cursor-pointer font-bold border transition-all flex flex-col justify-center items-center min-h-[68px] shadow-xs active:scale-95"
            :class="[
              slot.status === 'SCANNED'
                ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed pointer-events-none opacity-60'
                : 'bg-white border-slate-200 text-slate-700 hover:border-blue-300 hover:bg-blue-50/30',
              selectedSlotId === slot.id ? 'ring-3 ring-blue-500 border-blue-500 bg-blue-500/5 font-extrabold scale-102' : ''
            ]"
          >
            <span class="font-mono text-[0.9rem] sm:text-[0.95rem] font-black tracking-tight" :class="slot.status === 'SCANNED' ? 'text-slate-400/80' : 'text-slate-800'">{{ slot.carton_sn }}</span>
            <span class="text-[0.7rem] sm:text-[0.75rem] leading-none mt-1.5 font-bold" :class="slot.status === 'SCANNED' ? 'text-slate-400/50' : 'text-slate-400'">{{ t('packing.carton', 'Thùng') }} {{ slot.carton_number }}/{{ totalCartons }}</span>
            <i v-if="slot.status === 'SCANNED'" class="fas fa-check-circle text-emerald-500 text-[0.85rem] absolute top-1.5 right-1.5"></i>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
        <button @click="$emit('close')" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-xl transition-all shadow-lg shadow-blue-500/10 cursor-pointer text-[0.85rem]">
          {{ t('settings.close', 'Đóng') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { JobOrderSlot } from '../../../types/api';

defineProps<{
  show: boolean;
  jobOrder: string;
  totalCartons?: number;
  scannedCount?: number;
  slots: JobOrderSlot[];
  selectedSlotId?: number | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'selectSlot', slot: JobOrderSlot): void;
}>();

const { t } = useI18n();

const handleSlotClick = (slot: JobOrderSlot) => {
  if (slot.status === 'SCANNED') return;
  emit('selectSlot', slot);
};
</script>
