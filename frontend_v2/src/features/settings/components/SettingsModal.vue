<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="glass-card modal-content settings-modal">
      <div class="modal-header-modern">
        <div class="header-title"><i class="fas fa-cog"></i><h2>Station Settings</h2></div>
        <button @click="$emit('close')" class="btn-close-modern"><i class="fas fa-times"></i></button>
      </div>
      <div class="modal-body-scrollable">
        <p class="subtitle">Configure local printer and template paths for this station.</p>
        <div class="form-group">
          <label>Hardware Station ID (MAC)</label>
          <div class="mac-display">
            <i class="fas fa-fingerprint"></i>
            <input :value="system.stationId || 'Detecting...'" readonly class="modern-input readonly-input" />
            <span class="badge-auto">AUTO</span>
          </div>
          <small class="hint-text">This unique ID is fixed to this computer's network hardware for full traceability.</small>
        </div>
        <div class="form-group"><label>Template Path (.btw)</label><div class="input-with-hint"><input v-model="store.templatePath" placeholder="D:\Labels\carton_ui.btw" class="modern-input" /><small>Hint: Shift + Right Click on file -> "Copy as path" then paste here.</small></div></div>
        <div class="form-group"><label>Print Job Folder</label><div class="input-with-hint"><input v-model="store.printFolder" placeholder="D:\print_test" class="modern-input" /><small class="hint-text">Folder where XML files will be saved for BarTender to watch.</small></div></div>
        <div class="form-group checkbox-group"><label class="modern-checkbox"><input type="checkbox" v-model="store.serverPrint" /><span>Process Print on Server</span></label><small class="hint-text">If OFF, the local Agent or Browser Download will be used.</small></div>
        <div class="form-group"><label>Printer Name (Windows)</label><div class="input-with-hint"><input v-model="store.printerName" placeholder="Leave blank for BarTender Default" class="modern-input" /><small>Hint: If blank, BarTender will use the printer saved in the .btw file.</small></div></div>
        <div class="form-group"><label>Alert Speaker (Audio Output)</label><div class="input-with-hint">
          <select v-model="store.audioDeviceId" class="modern-input"><option value="">Default System Output</option><option v-for="d in audioDevices" :key="d.id" :value="d.id">{{ d.label }}</option></select>
          <small class="hint-text">Choose which speaker should play the "Invalid Scan" alert sound.</small>
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

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);
const store = useSettingsStore();
const system = useSystemStore();
const audioDevices = ref([]);

const loadAudioDevices = async () => {
  if (!navigator.mediaDevices?.enumerateDevices) return;
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    audioDevices.value = devices.filter(d => d.kind === 'audiooutput').map(d => ({ id: d.deviceId, label: d.label || `Speaker (${d.deviceId.slice(0, 5)}...)` }));
  } catch (e) { console.warn('Error loading audio devices:', e); }
};

const handleSave = async () => {
  store.saveSettings();
  emit('close');
  system.showNotification('Settings saved locally', 'success');
  if (system.isAgentConnected) {
    try { await fetch('http://127.0.0.1:1234/print', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'config', path: store.printFolder }) }); } catch (e) { console.warn('Failed to notify agent'); }
  }
};

watch(() => props.show, (val) => { if (val) loadAudioDevices(); });
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
.checkbox-group { margin-top: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; }
.modern-checkbox { display: flex; align-items: center; gap: 10px; cursor: pointer; font-weight: 600; color: #1e293b; }
.modern-checkbox input { width: 18px; height: 18px; cursor: pointer; }
.modal-actions-sticky { padding: 16px 24px; border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 16px; margin-top: auto; }
.btn-text { background: transparent; color: #64748b; border: none; padding: 10px 20px; cursor: pointer; font-weight: 500; }
.btn-text:hover { color: #1e293b; }
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }
.btn-primary:hover { background: #1d4ed8; }
</style>
