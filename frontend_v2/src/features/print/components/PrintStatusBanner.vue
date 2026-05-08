<template>
  <div class="mb-4 animate-in" v-if="lastCarton">
    <div 
      class="p-4 rounded-xl flex items-center gap-4 animate-in transition-colors" 
      :class="{ 
        'bg-rose-100 text-rose-800': lastCarton.status === 'FAILED', 
        'bg-blue-100 text-blue-800': lastCarton.status === 'PRINTING',
        'bg-emerald-100 text-emerald-800': lastCarton.status === 'SUCCESS'
      }"
    >
      <i class="fas" :class="{ 'fa-check-circle': lastCarton.status === 'SUCCESS', 'fa-exclamation-triangle': lastCarton.status === 'FAILED', 'fa-spinner fa-spin': lastCarton.status === 'PRINTING' }"></i>
      <span>
        <template v-if="lastCarton.status === 'PRINTING'">{{ t('print.printing_carton') }}: <strong>{{ lastCarton.carton_sn }}</strong>...</template>
        <template v-else-if="lastCarton.status === 'SUCCESS'">{{ t('print.last_carton') }}: <strong>{{ lastCarton.carton_sn }}</strong></template>
        <template v-else>{{ t('print.attempt_failed') }}: <strong class="line-through opacity-70">{{ lastCarton.carton_sn }}</strong>
          <span v-if="agentErrorMessage" class="text-[0.85rem] font-normal ml-1"> - {{ agentErrorMessage }}</span>
        </template>
      </span>
      <div class="flex gap-2.5 ml-auto" v-if="lastCarton.status !== 'PRINTING'">
        <a v-if="lastCarton.status === 'SUCCESS'" :href="downloadUrl" class="bg-emerald-700 text-white border-none px-4 py-2 rounded-lg cursor-pointer flex items-center gap-2 font-semibold transition-all no-underline hover:bg-emerald-800" download>
          <i class="fas fa-file-download"></i> {{ t('print.manual_download') }}
        </a>
        <button 
          @click="$emit('retry')" 
          class="border-none px-4 py-2 rounded-lg cursor-pointer flex items-center gap-2 font-semibold transition-all no-underline" 
          :class="lastCarton.status === 'SUCCESS' ? 'bg-white text-emerald-700 border border-emerald-700 hover:bg-emerald-50' : 'bg-rose-500 text-white hover:bg-rose-600'"
        >
          <i class="fas fa-redo"></i> {{ lastCarton.status === 'SUCCESS' ? t('print.reprint') : t('print.try_again') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const props = defineProps({
  lastCarton: Object,
  agentErrorMessage: { type: String, default: '' }
});
defineEmits(['retry']);
const downloadUrl = computed(() => props.lastCarton ? `/api/v1/print/carton/${props.lastCarton.id}/btxml` : '');
</script>
