<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card emergency-modal">
      <div class="modal-header-modern">
        <div class="header-title"><i class="fas fa-search"></i><h2>Find & Reprint</h2></div>
        <button @click="$emit('close')" class="btn-close-modern"><i class="fas fa-times"></i></button>
      </div>
      <div class="modal-body-modern">
        <p class="emergency-hint">Enter an exact Carton S/N to retrieve and reprint its label.</p>
        <div class="search-box-modern">
          <div class="search-input-wrapper"><i class="fas fa-barcode search-icon"></i>
            <input v-model="searchSN" placeholder="e.g. CN26040000001" @keyup.enter="handleSearch" class="modern-search-input" />
          </div>
          <button @click="handleSearch" :disabled="loading" class="btn-search-modern">
            <i class="fas fa-spinner fa-spin" v-if="loading"></i><span v-else>Search</span>
          </button>
        </div>
        <div v-if="result" class="emergency-result-card fade-in">
          <div class="result-header"><div class="status-indicator success"></div><h3>{{ result.carton_sn }}</h3></div>
          <div class="result-details">
            <div class="detail-group"><span class="label">Product</span><span class="value">{{ result.product.item_name }}</span></div>
            <div class="detail-row">
              <div class="detail-group"><span class="label">Job Order</span><span class="value">{{ result.job_order || 'N/A' }}</span></div>
              <div class="detail-group"><span class="label">Items</span><span class="value">{{ result.items ? result.items.length : '?' }} pcs</span></div>
              <div class="detail-group"><span class="label">Date</span><span class="value">{{ new Date(result.created_at).toLocaleDateString() }}</span></div>
            </div>
          </div>
          <div class="result-actions">
            <button @click="$emit('rescan', result)" class="btn-rescan-action">
              <i class="fas fa-redo"></i><span>Rescan Items</span>
            </button>
            <button @click="$emit('reprint', result)" :disabled="loading" class="btn-print-action">
              <i class="fas fa-spinner fa-spin" v-if="loading"></i><i class="fas fa-print" v-else></i><span>Print Label</span>
            </button>
          </div>
        </div>
        <div v-else-if="searchSN && !loading && searched" class="no-result-card">
          <div class="no-result-icon"><i class="fas fa-box-open"></i></div><p>No successful carton found with this S/N.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import printApi from '../api';
import { useSystemStore } from '../../../core/stores/system';

defineProps({ show: Boolean });
defineEmits(['close', 'reprint', 'rescan']);

const system = useSystemStore();
const searchSN = ref('');
const result = ref(null);
const loading = ref(false);
const searched = ref(false);

const handleSearch = async () => {
  if (!searchSN.value) return;
  loading.value = true; result.value = null; searched.value = false;
  try {
    const res = await printApi.searchCarton(searchSN.value.trim());
    if (res.data) result.value = res.data;
    else system.showNotification('Carton not found.', 'warning');
  } catch (err) { system.showNotification('Search failed: ' + (err.response?.data?.detail || err.message), 'error'); }
  finally { loading.value = false; searched.value = true; }
};
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 2000; }
.emergency-modal { width: 95%; max-width: 600px; background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); display: flex; flex-direction: column; }
.modal-header-modern { display: flex; justify-content: space-between; align-items: center; padding: 24px 32px 16px; }
.header-title { display: flex; align-items: center; gap: 12px; color: #1e293b; }
.header-title i { font-size: 1.5rem; color: #2563eb; }
.header-title h2 { margin: 0; font-size: 1.5rem; font-weight: 700; }
.btn-close-modern { background: #f1f5f9; border: none; width: 36px; height: 36px; border-radius: 10px; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-close-modern:hover { background: #e2e8f0; color: #0f172a; transform: rotate(90deg); }
.modal-body-modern { padding: 0 32px 32px; }
.emergency-hint { color: #64748b; font-size: 0.95rem; margin-bottom: 24px; }
.search-box-modern { border: 1px solid #e2e8f0; border-radius: 12px; padding: 6px; display: flex; gap: 8px; background: #fff; margin-bottom: 32px; }
.search-box-modern:focus-within { border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59,130,246,0.1); }
.search-input-wrapper { flex: 1; display: flex; align-items: center; padding-left: 12px; }
.search-icon { color: #94a3b8; font-size: 1.1rem; }
.modern-search-input { width: 100%; border: none; padding: 12px 14px; font-size: 1rem; color: #1e293b; outline: none; background: transparent; }
.btn-search-modern { background: #2563eb; color: white; border: none; padding: 0 24px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-search-modern:hover { background: #1d4ed8; }
.btn-search-modern:disabled { background: #94a3b8; cursor: not-allowed; }
.emergency-result-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; }
.result-header { padding: 16px 20px; background: white; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 12px; }
.status-indicator { width: 10px; height: 10px; border-radius: 50%; }
.status-indicator.success { background: #10b981; box-shadow: 0 0 0 4px rgba(16,185,129,0.1); }
.result-header h3 { margin: 0; font-size: 1.2rem; color: #0f172a; font-family: monospace; }
.result-details { padding: 20px; }
.detail-row { display: flex; gap: 24px; margin-top: 16px; }
.detail-group { display: flex; flex-direction: column; gap: 4px; }
.detail-group .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; font-weight: 600; }
.detail-group .value { color: #1e293b; font-weight: 500; font-size: 0.95rem; }
.result-actions { padding: 16px 20px; background: white; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; }
.btn-print-action { background: #1e293b; color: white; border: none; padding: 12px 24px; border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 10px; }
.btn-print-action:hover:not(:disabled) { background: #0f172a; transform: translateY(-2px); }
.btn-print-action:disabled { opacity: 0.7; cursor: not-allowed; }

.btn-rescan-action { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; padding: 12px 20px; border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; margin-right: auto; }
.btn-rescan-action:hover { background: #e2e8f0; color: #1e293b; }
.no-result-card { text-align: center; padding: 40px 20px; background: #f8fafc; border-radius: 16px; border: 1px dashed #cbd5e1; }
.no-result-icon { font-size: 3rem; color: #cbd5e1; margin-bottom: 16px; }
.no-result-card p { color: #64748b; margin: 0; }
</style>
