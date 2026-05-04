<template>
  <div class="session-info">
    <div class="session-header-row">
      <button @click="$emit('back')" class="btn-back-icon" title="Change Product">
        <i class="fas fa-arrow-left"></i>
      </button>
      <div class="active-product">
        <h2>{{ product.item_name }}</h2>
        <div class="meta">
          <span class="badge-outline">UPC: {{ product.upc }}</span>
          <span class="badge-outline">Target: {{ product.packed_qty }}</span>
        </div>
      </div>
      <div class="header-inputs">
        <div class="job-order-input">
          <label>Job Order</label>
          <input 
            :value="jobOrder" 
            @input="$emit('update:jobOrder', $event.target.value)"
            placeholder="Enter Job Order..." 
            class="modern-input-small"
            ref="jobOrderInput"
            @keyup.enter="$emit('focus-scan')"
          />
        </div>
        <div class="job-order-input">
          <label>Origin</label>
          <select 
            :value="cartonOrigin"
            @change="$emit('update:cartonOrigin', $event.target.value); $emit('focus-scan')"
            class="modern-input-small origin-select"
          >
            <option value="VN">VN</option>
            <option value="CN">CN</option>
          </select>
        </div>
        <div class="job-order-input">
          <div class="input-with-toggle">
            <input 
              :value="customSN"
              @input="$emit('update:customSN', $event.target.value)"
              type="number"
              :placeholder="suggestedSNValue || '00001'" 
              class="modern-input-small sn-input"
              :class="{ 'is-auto': !isSNManual }"
              :readonly="!isSNManual"
              @keyup.enter="$emit('focus-scan')"
              ref="snInput"
            />
            <button 
              class="btn-auto-toggle" 
              :class="{ 'active': !isSNManual }"
              @click="toggleMode"
              :title="!isSNManual ? 'Switch to Manual Entry' : 'Switch to Auto Assignment'"
            >
              {{ !isSNManual ? 'AUTO' : 'MANUAL' }}
            </button>
          </div>
          <div class="sn-preview" v-if="snPreview">
             Preview: <strong :class="{ 'text-danger': snExists }">{{ snExists ? '⚠️ S/N ALREADY EXISTS!' : snPreview }}</strong>
          </div>
        </div>
        <div class="job-order-input">
          <label>SN Pattern</label>
          <input 
            :value="snPattern"
            @input="$emit('update:snPattern', $event.target.value)"
            placeholder="e.g. AS" 
            class="modern-input-small sn-pattern-input"
            @keyup.enter="$emit('focus-scan')"
          />
        </div>
        <div class="job-order-input">
          <label>Manual Date (YYMM)</label>
          <input 
            :value="customYYMM"
            @input="$emit('update:customYYMM', $event.target.value)"
            placeholder="e.g. 2604" 
            maxlength="4"
            class="modern-input-small date-input"
            @keyup.enter="$emit('focus-scan')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const props = defineProps({
  product: { type: Object, required: true },
  jobOrder: { type: String, default: '' },
  cartonOrigin: { type: String, default: 'VN' },
  customSN: { type: String, default: '' },
  isSNManual: { type: Boolean, default: false },
  snPattern: { type: String, default: '' },
  customYYMM: { type: String, default: '' },
  suggestedSNValue: { type: Number, default: 0 },
  snPreview: { type: String, default: '' },
  snExists: { type: Boolean, default: false }
});

const emit = defineEmits(['back', 'focus-scan', 'update:jobOrder', 'update:cartonOrigin', 'update:customSN', 'update:isSNManual', 'update:snPattern', 'update:customYYMM']);

const jobOrderInput = ref(null);
const snInput = ref(null);

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

<style scoped>
.session-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f8fafc, #ffffff);
  border-radius: 20px;
  border: 1px solid #eef2f6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.session-header-row {
  display: flex;
  align-items: center;
  gap: 24px;
  width: 100%;
}
.btn-back-icon {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #64748b;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.btn-back-icon:hover {
  background: #f8fafc;
  color: #2563eb;
  border-color: #3b82f6;
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}
.active-product { flex: 1; }
.active-product h2 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}
.meta { 
  display: flex;
  gap: 10px;
  margin-top: 8px; 
}
.badge-outline {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  background: #f8fafc;
}
.header-inputs { 
  display: flex; 
  gap: 16px; 
  align-items: flex-end;
}
.job-order-input { display: flex; flex-direction: column; gap: 6px; }
.job-order-input label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding-left: 2px;
}
.modern-input-small {
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  outline: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  min-width: 80px;
}
.origin-select {
  width: 80px;
}
.sn-input {
  width: 160px;
  padding-right: 70px !important;
}
.modern-input-small:focus {
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08), 0 1px 2px rgba(0,0,0,0.05);
}
.modern-input-small.input-err {
  border-color: #ef4444 !important;
  background: #fff1f2 !important;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
.input-error-hint {
  color: #e11d48;
  font-size: 0.65rem;
  font-weight: 600;
  margin-top: 2px;
  display: block;
}
.sn-preview {
  font-size: 0.7rem;
  color: #10b981;
  margin-top: 4px;
  background: #f0fdf4;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #dcfce7;
}
.sn-preview strong {
  font-family: monospace;
  font-size: 0.8rem;
}
.sn-pattern-input {
  width: 100px;
  border-color: #93c5fd;
  color: #1e40af;
}
.date-input {
  width: 90px;
  border-color: #f59e0b;
  color: #92400e;
}
.date-input:focus {
  border-color: #d97706;
  background: #fffbeb;
}
.text-danger {
  color: #ef4444 !important;
}
.sn-pattern-input:focus {
  border-color: #2563eb;
  background: #eff6ff;
}
.input-with-toggle {
  position: relative;
  display: flex;
  align-items: center;
}
.sn-input {
  padding-right: 70px !important;
}
.sn-input.is-auto {
  background: #f0fdf4;
  border-color: #10b981;
  color: #059669;
  cursor: default;
}
.btn-auto-toggle {
  position: absolute;
  right: 4px;
  top: 4px;
  bottom: 4px;
  border: none;
  background: #e2e8f0;
  color: #64748b;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-auto-toggle.active {
  background: #10b981;
  color: white;
}
.btn-auto-toggle:hover {
  transform: scale(1.05);
}

@media (max-width: 600px) {
  .session-info { flex-direction: column; align-items: flex-start; }
}
</style>
