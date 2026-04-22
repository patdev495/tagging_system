<template>
  <div class="input-area">
    <div class="input-row">
      <input 
        type="text" 
        :value="scanBuffer"
        @input="$emit('update:scanBuffer', $event.target.value)"
        @keyup.enter="$emit('scan')"
        :placeholder="!jobOrder ? '⚠️ PLEASE ENTER JOB ORDER FIRST...' : (awaitingNext ? '⚠️ BOX FULL! CLICK NEXT CARTON...' : 'Scan Item S/N...')"
        ref="scanInput"
        class="scan-input"
        :class="{ 'input-locked': !jobOrder || awaitingNext }"
      />
      <button 
        v-if="awaitingNext" 
        @click="$emit('next-carton')" 
        class="btn-next-carton pulse-animation"
        title="Start New Carton"
      >
        <i class="fas fa-plus-circle"></i> Next Carton
      </button>
    </div>
    <p class="hint" v-if="jobOrder && !awaitingNext">Waiting for scanner input (Enter to submit)</p>
    <p class="hint success" v-else-if="awaitingNext">Box Complete! Please move to next box and click button above</p>
    <p class="hint warning" v-else>Please fill in the Job Order field at the top first</p>

    <!-- Invalid Scans Area -->
    <div v-if="invalidScans.length > 0" class="invalid-scans-area fade-in">
      <div class="invalid-header">
        <span><i class="fas fa-exclamation-circle"></i> Invalid Scans</span>
        <button @click="$emit('clear-invalid')" class="btn-clear-small">Clear</button>
      </div>
      <div class="invalid-list">
        <div v-for="(err, idx) in [...invalidScans].reverse()" :key="idx" class="invalid-item" :class="`type-${err.type || 'generic'}`">
          <div class="bad-info">
            <span class="bad-sn">{{ err.sn }}</span>
            <span class="bad-reason">{{ err.reason }}</span>
          </div>
          <span class="bad-time">{{ err.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  scanBuffer: { type: String, default: '' },
  jobOrder: { type: String, default: '' },
  awaitingNext: { type: Boolean, default: false },
  invalidScans: { type: Array, default: () => [] }
});

defineEmits(['update:scanBuffer', 'scan', 'next-carton', 'clear-invalid']);

const scanInput = ref(null);

const focusScan = () => {
  if (scanInput.value) scanInput.value.focus({ preventScroll: true });
};

defineExpose({ focusScan });
</script>

<style scoped>
.scan-input {
  box-sizing: border-box;
  padding: 16px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
  transition: all 0.2s;
  flex: 1;
  min-width: 0;
}
.scan-input:focus {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  outline: none;
}
.scan-input.input-locked {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #64748b;
  cursor: not-allowed;
  flex: 1;
  min-width: 0;
}
.input-row { display: flex; gap: 12px; align-items: flex-start; }
.hint { text-align: center; color: #94a3b8; font-size: 0.85rem; }
.hint.warning { color: #ef4444; font-weight: 600; }
.hint.success { color: #059669; font-weight: 700; }
.btn-next-carton {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0 24px;
  height: 58px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  transition: all 0.2s;
}
.btn-next-carton:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}
.pulse-animation { animation: pulse-green 2s infinite; }
@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
.invalid-scans-area {
  margin-top: 20px;
  background: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.invalid-header {
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #feb2b2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c53030;
  font-size: 0.85rem;
  font-weight: 700;
}
.invalid-header i { margin-right: 6px; }
.btn-clear-small {
  background: transparent;
  border: 1px solid #feb2b2;
  color: #c53030;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-clear-small:hover { background: #fff5f5; border-color: #c53030; }
.invalid-list { max-height: 150px; overflow-y: auto; padding: 8px; }
.invalid-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: white;
  border-radius: 6px;
  margin-bottom: 4px;
  border: 1px solid #fed7d7;
}
.bad-sn { font-family: monospace; font-weight: 600; color: #e53e3e; }
.bad-reason {
  font-size: 0.7rem;
  background: #fecaca;
  color: #b91c1c;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.bad-info { display: flex; align-items: center; }
.bad-time { font-size: 0.75rem; color: #a0aec0; }
.type-pattern .bad-reason { background: #ffedd5; color: #9a3412; }
.type-duplicate .bad-reason { background: #f3e8ff; color: #6b21a8; }
.type-pattern { border-left: 4px solid #f97316; }
.type-duplicate { border-left: 4px solid #a855f7; }
.type-excess { border-left: 4px solid #ef4444; }
.type-generic { border-left: 4px solid #ef4444; }
.type-lockdown { border-left: 4px solid #ef4444; }
</style>
