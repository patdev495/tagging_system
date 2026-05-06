<template>
  <div class="result-actions fade-in" v-if="lastCarton">
    <div class="success-banner" :class="{ 'error-banner': lastCarton.status === 'FAILED', 'printing-banner': lastCarton.status === 'PRINTING' }">
      <i class="fas" :class="{ 'fa-check-circle': lastCarton.status === 'SUCCESS', 'fa-exclamation-triangle': lastCarton.status === 'FAILED', 'fa-spinner fa-spin': lastCarton.status === 'PRINTING' }"></i>
      <span>
        <template v-if="lastCarton.status === 'PRINTING'">{{ t('print.printing_carton') }}: <strong>{{ lastCarton.carton_sn }}</strong>...</template>
        <template v-else-if="lastCarton.status === 'SUCCESS'">{{ t('print.last_carton') }}: <strong>{{ lastCarton.carton_sn }}</strong></template>
        <template v-else>{{ t('print.attempt_failed') }}: <strong class="text-strike">{{ lastCarton.carton_sn }}</strong>
          <span v-if="agentErrorMessage" class="error-detail"> - {{ agentErrorMessage }}</span>
        </template>
      </span>
      <div class="banner-actions" v-if="lastCarton.status !== 'PRINTING'">
        <a v-if="lastCarton.status === 'SUCCESS'" :href="downloadUrl" class="btn-reprint" download>
          <i class="fas fa-file-download"></i> {{ t('print.manual_download') }}
        </a>
        <button @click="$emit('retry')" class="btn-reprint" :class="lastCarton.status === 'SUCCESS' ? 'secondary' : 'primary-err'">
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

<style scoped>
.result-actions { margin-bottom: 16px; }
.success-banner { background: #dcfce7; color: #166534; padding: 16px; border-radius: 12px; display: flex; align-items: center; gap: 16px; animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
.success-banner.error-banner { background: #fee2e2; color: #991b1b; }
.text-strike { text-decoration: line-through; opacity: 0.7; }
.error-detail { font-size: 0.85rem; font-weight: normal; margin-left: 5px; }
.btn-reprint { margin-left: auto; background: #166534; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; transition: all 0.2s; text-decoration: none; }
.btn-reprint.primary-err { background: #ef4444; }
.btn-reprint.primary-err:hover { background: #dc2626; }
.btn-reprint.secondary { background: white; color: #166534; border: 1px solid #166534; }
.banner-actions { display: flex; gap: 10px; margin-left: auto; }
@keyframes bounceIn { 0% { transform: scale(0.3); opacity: 0; } 50% { transform: scale(1.05); opacity: 1; } 70% { transform: scale(0.9); } 100% { transform: scale(1); } }
</style>
