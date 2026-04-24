<template>
  <div class="input-area">
    <div class="input-row">
      <input 
        type="text" 
        :value="scanBuffer"
        @input="$emit('update:scanBuffer', $event.target.value)"
        @keyup.enter="$emit('scan')"
        :placeholder="!jobOrder ? '⚠️ PLEASE ENTER JOB ORDER FIRST...' : (awaitingNext ? '📦 BOX FULL — scan to capture overflow...' : 'Scan Item S/N...')"
        ref="scanInput"
        class="scan-input"
        :class="{ 'input-locked': !jobOrder, 'input-overflow': awaitingNext && jobOrder }"
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
    <p class="hint overflow-hint" v-else-if="awaitingNext">📦 Box Complete! Overflow scans are captured below. Click <strong>Next Carton</strong> when ready.</p>
    <p class="hint warning" v-else>Please fill in the Job Order field at the top first</p>

    <!-- Overflow Scans Area (excess scans after box full) -->
    <div v-if="overflowScans.length > 0" class="overflow-scans-area fade-in">
      <div class="overflow-header">
        <span><i class="fas fa-exclamation-triangle"></i> Overflow Scans ({{ overflowScans.length }}) — Remove these from box!</span>
        <button @click="$emit('clear-overflow')" class="btn-clear-small btn-clear-overflow">Clear</button>
      </div>
      <div class="overflow-list">
        <div v-for="(item, idx) in overflowScans" :key="idx" class="overflow-item">
          <div class="overflow-info">
            <span class="overflow-index">#{{ idx + 1 }}</span>
            <span class="overflow-sn">{{ item.sn }}</span>
          </div>
          <span class="overflow-time">{{ item.time }}</span>
        </div>
      </div>
    </div>

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
  invalidScans: { type: Array, default: () => [] },
  overflowScans: { type: Array, default: () => [] }
});

defineEmits(['update:scanBuffer', 'scan', 'next-carton', 'clear-invalid', 'clear-overflow']);

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
.scan-input.input-overflow {
  background: #fff7ed;
  border-color: #f97316;
  color: #9a3412;
  flex: 1;
  min-width: 0;
}
.scan-input.input-overflow:focus {
  border-color: #ea580c;
  background: #fff7ed;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.15);
}
.input-row { display: flex; gap: 12px; align-items: flex-start; }
.hint { text-align: center; color: #94a3b8; font-size: 0.85rem; }
.hint.warning { color: #ef4444; font-weight: 600; }
.hint.success { color: #059669; font-weight: 700; }
.hint.overflow-hint { color: #ea580c; font-weight: 700; }
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

/* Overflow Scans */
.overflow-scans-area {
  margin-top: 16px;
  background: #fff7ed;
  border: 2px solid #fb923c;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.15);
}
.overflow-header {
  padding: 10px 14px;
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  border-bottom: 1px solid #fb923c;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c2410c;
  font-size: 0.85rem;
  font-weight: 700;
}
.overflow-header i { margin-right: 6px; color: #ea580c; }
.btn-clear-overflow {
  border-color: #fb923c !important;
  color: #c2410c !important;
}
.btn-clear-overflow:hover { background: #ffedd5 !important; }
.overflow-list { max-height: 200px; overflow-y: auto; padding: 8px; }
.overflow-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 4px;
  border: 1px solid #fed7aa;
  border-left: 4px solid #f97316;
  transition: all 0.2s;
}
.overflow-item:hover { background: #fffbeb; }
.overflow-info { display: flex; align-items: center; gap: 10px; }
.overflow-index {
  font-size: 0.7rem;
  font-weight: 800;
  color: #c2410c;
  background: #ffedd5;
  padding: 2px 6px;
  border-radius: 4px;
}
.overflow-sn {
  font-family: monospace;
  font-weight: 700;
  color: #9a3412;
  font-size: 0.95rem;
}
.overflow-time { font-size: 0.75rem; color: #a0aec0; }

/* Invalid Scans */
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
