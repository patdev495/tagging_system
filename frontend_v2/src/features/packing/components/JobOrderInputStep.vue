<template>
  <div class="flex-1 flex flex-col justify-center items-center py-16 md:py-24">
    <div class="w-full max-w-[480px] bg-slate-50 border border-slate-200/60 rounded-3xl p-6 md:p-8 shadow-xl">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-blue-600">
          <i class="fas fa-file-invoice text-[2rem]"></i>
        </div>
        <h2 class="text-[1.5rem] font-black text-slate-900 mb-2">{{ t('packing.enter_job_order_title', 'Nhập Số Công Lệnh') }}</h2>
        <p class="text-slate-500 text-[0.9rem]">{{ t('packing.enter_job_order_desc', 'Vui lòng quét hoặc nhập mã công lệnh sản xuất để bắt đầu đóng thùng.') }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="relative">
          <input
            ref="inputRef"
            :value="modelValue"
            @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
            :placeholder="t('packing.job_order_placeholder', 'Nhập số công lệnh...')"
            class="w-full border rounded-2xl px-5 py-4 text-[1.1rem] outline-none bg-white font-mono transition-all text-center tracking-wider"
            :class="hasError
              ? 'border-rose-500 text-rose-600 focus:border-rose-500 focus:ring-rose-500/10 shadow-[0_0_0_4px_rgba(239,68,68,0.1)] bg-rose-50/10'
              : 'border-slate-200 focus:border-blue-500 focus:ring-blue-500/10 text-slate-800'"
            autocomplete="off"
            :disabled="isLoading"
          />
        </div>

        <!-- Job Order Error Alert -->
        <div 
          v-if="hasError && errorText"
          class="text-[0.85rem] text-rose-600 bg-rose-50 px-4 py-3 rounded-2xl border border-rose-100 font-bold flex items-center gap-2 animate-in"
        >
          <i class="fas fa-exclamation-circle text-rose-500"></i>
          <span>{{ errorText }}</span>
        </div>

        <button
          type="submit"
          :disabled="!modelValue.trim() || isLoading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 text-white disabled:text-slate-400 font-bold py-4 px-6 rounded-2xl transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-blue-500/10"
        >
          <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-arrow-right"></i>
          <span>{{ t('packing.confirm', 'Xác Nhận') }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

defineProps<{
  modelValue: string;
  isLoading?: boolean;
  hasError?: boolean;
  errorText?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'submit'): void;
}>();

const { t } = useI18n();
const inputRef = ref<HTMLInputElement | null>(null);

const handleSubmit = () => {
  emit('submit');
};

const focusInput = () => {
  if (inputRef.value) {
    inputRef.value.focus();
  }
};

defineExpose({
  focusInput,
});
</script>
