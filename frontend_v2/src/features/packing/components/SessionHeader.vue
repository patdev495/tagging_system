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
          <label>Start S/N</label>
          <input 
            :value="customSN"
            @input="$emit('update:customSN', $event.target.value)"
            type="number"
            :placeholder="suggestedSNValue || '00001'" 
            class="modern-input-small"
            :class="{ 'input-err': customSN && parseInt(customSN) < suggestedSNValue }"
            @keyup.enter="$emit('focus-scan')"
          />
          <div class="sn-preview" v-if="snPreview">
             Preview: <strong>{{ snPreview }}</strong>
          </div>
          <span v-if="customSN && parseInt(customSN) < suggestedSNValue" class="input-error-hint">
             Min: {{ suggestedSNValue }} (Next Carton)
          </span>
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  product: { type: Object, required: true },
  jobOrder: { type: String, default: '' },
  cartonOrigin: { type: String, default: 'VN' },
  customSN: { type: String, default: '' },
  snPattern: { type: String, default: '' },
  suggestedSNValue: { type: Number, default: 0 },
  snPreview: { type: String, default: '' }
});

defineEmits(['back', 'focus-scan', 'update:jobOrder', 'update:cartonOrigin', 'update:customSN', 'update:snPattern']);

const jobOrderInput = ref(null);

const focusJobOrder = () => {
  if (jobOrderInput.value) jobOrderInput.value.focus({ preventScroll: true });
};

defineExpose({ focusJobOrder });
</script>

<style scoped>
.session-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
  margin-bottom: 16px;
  padding: 12px 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.session-header-row {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  width: 100%;
}
.btn-back-icon {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #64748b;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-top: 4px;
}
.btn-back-icon:hover {
  background: #e2e8f0;
  color: #1e293b;
  transform: translateX(-2px);
}
.active-product { flex: 1; }
.active-product h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #1e3a8a;
  line-height: 1.2;
}
.meta { color: #64748b; margin-top: 4px; }
.meta span { margin-right: 16px; }
.badge-outline {
  display: inline-block;
  padding: 2px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #64748b;
  margin-right: 8px;
  background: white;
}
.header-inputs { display: flex; gap: 12px; }
.job-order-input { display: flex; flex-direction: column; gap: 4px; }
.job-order-input label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.modern-input-small {
  padding: 10px 14px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}
.modern-input-small:focus {
  background: white;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
.sn-pattern-input:focus {
  border-color: #2563eb;
  background: #eff6ff;
}

@media (max-width: 600px) {
  .session-info { flex-direction: column; align-items: flex-start; }
}
</style>
