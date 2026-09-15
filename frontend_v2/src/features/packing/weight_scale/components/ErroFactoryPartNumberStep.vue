<template>
  <div class="flex-1 flex flex-col justify-center items-center py-10 md:py-16">
    <div class="w-full max-w-[500px] bg-white border border-slate-300 rounded-xl p-6 md:p-8 shadow-md">
      <div class="text-center mb-6">
        <div class="w-14 h-14 bg-indigo-50 border border-indigo-200 rounded-xl flex items-center justify-center mx-auto mb-3 text-indigo-600">
          <i class="fas fa-barcode text-2xl"></i>
        </div>
        <h2 class="text-xl font-black text-slate-900 mb-1.5">Nhập Factory P/N</h2>
        <p class="text-slate-500 text-xs leading-relaxed max-w-sm mx-auto">
          Quét hoặc nhập Factory P/N để xác thực mã hàng Erro trước khi vào trạm cân.
        </p>
      </div>

      <form class="space-y-4" @submit.prevent="resolve">
        <div>
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 pl-0.5">
            Factory P/N:
          </label>
          <input
            ref="inputRef"
            v-model="value"
            type="text"
            autocomplete="off"
            autocorrect="off"
            spellcheck="false"
            placeholder="Ví dụ: 1LAE0009D2U004MAAR"
            class="w-full h-14 border-2 rounded-xl px-4 text-xl outline-none bg-white font-barcode-mono font-black transition-all text-center tracking-wider shadow-xs uppercase"
            :class="error ? 'border-rose-500 text-rose-700 focus:border-rose-500 focus:ring-4 focus:ring-rose-500/15 bg-rose-50/20' : 'border-slate-300 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-500/10 text-slate-900'"
            :disabled="isResolving"
          />
        </div>

        <div v-if="error" class="text-xs text-rose-700 bg-rose-50 p-3 rounded-lg border border-rose-200 font-medium flex items-start gap-2">
          <i class="fas fa-circle-exclamation text-rose-600 mt-0.5 shrink-0 text-sm"></i>
          <div>
            <strong class="block font-bold text-rose-800">{{ error }}</strong>
            <span class="text-[11px] text-rose-600 mt-0.5 block">Kiểm tra lại Factory P/N hoặc liên hệ quản trị để cấu hình mã hàng.</span>
          </div>
        </div>

        <button
          type="submit"
          :disabled="!value.trim() || isResolving"
          class="w-full h-12 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white disabled:text-slate-400 font-bold text-sm rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer shadow-xs active:scale-98"
        >
          <i v-if="isResolving" class="fas fa-spinner fa-spin"></i>
          <span v-else>Xác Nhận Mã Hàng</span>
          <span class="text-xs font-barcode-mono font-black px-1.5 py-0.5 bg-black/20 rounded">ENTER ↵</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue';
import catalogApi from '../../../catalog/api';
import type { Product } from '../../../../types/api';

const emit = defineEmits<{
  (e: 'resolved', product: Product): void;
}>();

const inputRef = ref<HTMLInputElement | null>(null);
const value = ref('');
const error = ref('');
const isResolving = ref(false);

const focusInput = () => {
  inputRef.value?.focus();
  inputRef.value?.select();
};

const resolve = async () => {
  const factoryPartNumber = value.value.trim();
  if (!factoryPartNumber || isResolving.value) return;

  error.value = '';
  isResolving.value = true;
  try {
    const response = await catalogApi.resolveErroProductByInternalFactoryPartNumber(factoryPartNumber);
    emit('resolved', response.data);
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.response?.data?.error || 'Không thể tra Factory P/N.';
    await nextTick();
    focusInput();
  } finally {
    isResolving.value = false;
  }
};

onMounted(focusInput);

defineExpose({ focusInput });
</script>
