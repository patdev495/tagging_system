<template>
  <div 
    v-if="show" 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in"
  >
    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-6 border border-slate-100 flex flex-col gap-5">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div class="flex items-center gap-2.5">
          <i class="fas fa-tags text-indigo-600 text-lg"></i>
          <h2 class="font-bold text-lg text-slate-900">Cấu Hình PO & LOT Đóng Hàng</h2>
        </div>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg">
          <i class="fas fa-times text-lg"></i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Mã Đơn Hàng (PO Number) {{ isTem3 ? '(Tùy chọn)' : '*' }}
          </label>
          <input
            v-model="formPo"
            type="text"
            :required="!isTem3"
            :placeholder="isTem3 ? 'Ví dụ: B432-22156381 (hoặc để trống)' : 'Ví dụ: B432-22156381'"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Mã Số Lô (Lot Number) *
          </label>
          <input
            v-model="formLot"
            type="text"
            required
            placeholder="Ví dụ: 92607933"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm font-mono"
          />
        </div>

        <div class="flex justify-end gap-2.5 pt-2">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-all cursor-pointer"
          >
            Hủy
          </button>
          <button
            type="submit"
            class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-all cursor-pointer shadow-md shadow-indigo-600/20"
          >
            Lưu Thông Tin
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  show: boolean;
  po: string;
  lot: string;
  isTem3?: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: { po: string; lot: string }): void;
}>();

const formPo = ref(props.po);
const formLot = ref(props.lot);

watch(
  () => props.show,
  (isShown) => {
    if (isShown) {
      formPo.value = props.po;
      formLot.value = props.lot;
    }
  }
);

const handleSubmit = () => {
  if (!formLot.value.trim()) return;
  if (!props.isTem3 && !formPo.value.trim()) return;
  emit('save', {
    po: formPo.value.trim(),
    lot: formLot.value.trim(),
  });
};
</script>
