<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="glass-card modal-content settings-modal">
      <div class="modal-header-modern">
        <div class="header-title"><i class="fas fa-cog"></i><h2>Station Settings</h2></div>
        <button @click="$emit('close')" class="btn-close-modern"><i class="fas fa-times"></i></button>
      </div>
      <div class="modal-body-scrollable">
        <p class="subtitle">Configure the printer and sound settings for this scanning station.</p>
        
        <div class="central-print-banner">
          <i class="fas fa-server"></i>
          <div>
            <strong>Centralized Printing</strong>
            <small>The print command is sent via the server to the printer you select below.</small>
          </div>
        </div>

        <div class="form-group">
          <label> Station IP </label>
          <div class="mac-display">
            <i class="fas fa-fingerprint"></i>
            <input :value="system.stationId || 'Detecting...'" readonly class="modern-input readonly-input" />
            <span class="badge-auto">AUTO</span>
          </div>
          <small class="hint-text"></small>
        </div>

        <!-- Printer Selection -->
        <div class="form-group">
          <label><i class="fas fa-print" style="margin-right:6px; color:#2563eb"></i>Select printer</label>
          <div class="input-with-hint">
            <div class="printer-select-wrapper">
              <select v-model="store.printerName" class="modern-input">
                <option value="">-- Máy in mặc định (trong file .btw) --</option>
                <option v-for="p in availablePrinters" :key="p.name" :value="p.name">
                  🖨️ {{ p.name }} ({{ p.port }})
                </option>
              </select>
              <button @click="loadPrinters" class="btn-refresh-printers" title="Làm mới danh sách">
                <i class="fas fa-sync-alt" :class="{'fa-spin': loadingPrinters}"></i>
              </button>
            </div>
            <small v-if="availablePrinters.length === 0 && !loadingPrinters" class="hint-text">
              Không tìm thấy máy in nào. Nhấn nút 🔄 để thử lại.
            </small>
            <small v-else>Select the printer you want to use. Leave blank to use the default printer.</small>
          </div>
        </div>

        <!-- Template Path (Client Fallback) -->
        <div class="form-group">
          <label><i class="fas fa-file-alt" style="margin-right:6px; color:#f59e0b"></i>Fallback Template Path (Client)</label>
          <div class="input-with-hint">
            <input v-model="store.templatePath" type="text" placeholder="D:\PAT\Templates\carton.ui.btw" class="modern-input font-mono text-xs" />
            <small class="hint-text">This path is used if the product has not been configured with a template in the system.</small>
          </div>
        </div>

        <div class="form-group"><label>Alert Speaker (Audio Output)</label><div class="input-with-hint">
          <select v-model="store.audioDeviceId" class="modern-input"><option value="">Default System Output</option><option v-for="d in audioDevices" :key="d.id" :value="d.id">{{ d.label }}</option></select>
          <small class="hint-text">Speaker that plays an alert sound when an incorrect scan occurs.</small>
        </div></div>
      </div>
      <div class="modal-actions-sticky">
        <button @click="$emit('close')" class="btn-text">Cancel</button>
        <button @click="handleSave" class="btn-primary">Save Settings</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import printApi from '../../print/api';

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);
const store = useSettingsStore();
const system = useSystemStore();
const audioDevices = ref([]);
const availablePrinters = ref([]);
const loadingPrinters = ref(false);

const loadAudioDevices = async () => {
  if (!navigator.mediaDevices?.enumerateDevices) return;
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    audioDevices.value = devices.filter(d => d.kind === 'audiooutput').map(d => ({ id: d.deviceId, label: d.label || `Speaker (${d.deviceId.slice(0, 5)}...)` }));
  } catch (e) { console.warn('Error loading audio devices:', e); }
};

const loadPrinters = async () => {
  loadingPrinters.value = true;
  try {
    const res = await printApi.getAvailablePrinters();
    if (res.data?.printers) availablePrinters.value = res.data.printers;
  } catch (e) { console.warn('Failed to load printers:', e); }
  finally { loadingPrinters.value = false; }
};

const handleSave = () => {
  store.saveSettings();
  emit('close');
  system.showNotification('Settings saved locally', 'success');
};

watch(() => props.show, (val) => { if (val) { loadAudioDevices(); loadPrinters(); } });
onMounted(() => { loadAudioDevices(); });
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 2000; }
.modal-content { background: white; padding: 0; border-radius: 16px; width: 90%; max-width: 500px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); color: #1e293b; overflow: hidden; }
.settings-modal { max-height: 90vh; display: flex; flex-direction: column; }
.modal-header-modern { padding: 20px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: white; }
.header-title { display: flex; align-items: center; gap: 12px; color: #0f172a; }
.header-title h2 { margin: 0; font-size: 1.25rem; }
.btn-close-modern { background: transparent; border: none; color: #64748b; font-size: 1.25rem; cursor: pointer; }
.btn-close-modern:hover { color: #ef4444; }
.modal-body-scrollable { padding: 20px 24px; overflow-y: auto; flex: 1; }
.subtitle { color: #64748b; margin-bottom: 24px; font-size: 0.9rem; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.85rem; color: #475569; }
.modern-input { width: 100%; box-sizing: border-box; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; background: #f8fafc; color: #1e293b; outline: none; }
.modern-input:focus { border-color: #3b82f6; background: white; }
.input-with-hint small { display: block; margin-top: 4px; font-size: 0.75rem; color: #2563eb; }
.mac-display { position: relative; display: flex; align-items: center; }
.mac-display i { position: absolute; left: 12px; color: #3b82f6; font-size: 0.9rem; }
.mac-display .modern-input { padding-left: 36px; padding-right: 60px; }
.readonly-input { background: #f1f5f9 !important; color: #64748b; cursor: not-allowed; border-style: dashed; }
.badge-auto { position: absolute; right: 10px; background: #dcfce7; color: #16a34a; font-size: 0.65rem; font-weight: 900; padding: 2px 6px; border-radius: 4px; border: 1px solid #bbf7d0; }
.input-with-hint small.hint-text { color: #64748b; background: #f1f5f9; padding: 8px; border-radius: 6px; margin-top: 6px; line-height: 1.4; }
.modal-actions-sticky { padding: 16px 24px; border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 16px; margin-top: auto; }
.btn-text { background: transparent; color: #64748b; border: none; padding: 10px 20px; cursor: pointer; font-weight: 500; }
.btn-text:hover { color: #1e293b; }
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }
.btn-primary:hover { background: #1d4ed8; }
.central-print-banner { background: linear-gradient(135deg, #ecfdf5, #d1fae5); border: 1px solid #a7f3d0; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: flex-start; gap: 14px; color: #065f46; }
.central-print-banner i { font-size: 1.4rem; margin-top: 2px; color: #10b981; }
.central-print-banner strong { display: block; font-size: 0.9rem; }
.central-print-banner small { display: block; margin-top: 4px; font-size: 0.75rem; color: #047857; }
.printer-select-wrapper { display: flex; gap: 8px; align-items: center; }
.printer-select-wrapper select { flex: 1; }
.btn-refresh-printers { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #64748b; flex-shrink: 0; }
.btn-refresh-printers:hover { background: #e2e8f0; color: #2563eb; }
</style>
