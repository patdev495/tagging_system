<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="glass-card modal-content settings-modal">
      <div class="modal-header-modern">
        <div class="header-title"><i class="fas fa-cog"></i><h2>{{ t('settings.title') }}</h2></div>
        <button @click="$emit('close')" class="btn-close-modern"><i class="fas fa-times"></i></button>
      </div>
      <div class="modal-body-scrollable">
        <p class="subtitle">{{ t('settings.subtitle') }}</p>
        
        <!-- Print Mode Selection -->
        <div class="print-mode-selector mb-6">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{{ t('settings.print_mode') }}</label>
          <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-xl">
            <button 
              @click="store.printMode = 'centralized'"
              :class="['flex flex-col items-center gap-1 py-3 rounded-lg transition-all', store.printMode === 'centralized' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50']"
            >
              <i class="fas fa-server text-lg"></i>
              <span class="text-[10px] font-black uppercase">{{ t('settings.centralized') }}</span>
            </button>
            <button 
              @click="store.printMode = 'local'"
              :class="['flex flex-col items-center gap-1 py-3 rounded-lg transition-all', store.printMode === 'local' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50']"
            >
              <i class="fas fa-desktop text-lg"></i>
              <span class="text-[10px] font-black uppercase">{{ t('settings.local_agent') }}</span>
            </button>
          </div>
        </div>

        <!-- Language Selection -->
        <div class="form-group">
          <label><i class="fas fa-globe" style="margin-right:6px; color:#10b981"></i>{{ t('settings.language') }}</label>
          <div class="input-with-hint">
            <select v-model="store.language" class="modern-input">
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div v-if="store.printMode === 'centralized'" class="print-banner centralized-banner fade-in">
          <i class="fas fa-server"></i>
          <div>
            <strong>{{ t('settings.centralized_title') }}</strong>
            <small>{{ t('settings.centralized_desc') }}</small>
          </div>
        </div>

        <div v-else class="print-banner local-banner fade-in">
          <i class="fas fa-bolt"></i>
          <div>
            <strong>{{ t('settings.local_title') }}</strong>
            <small>{{ t('settings.local_desc') }}</small>
          </div>
        </div>

        <!-- Agent Configuration (Only if local) -->
        <div v-if="store.printMode === 'local'" class="local-config animate-in slide-in-from-top-2 duration-300">
          <div class="form-group">
            <label><i class="fas fa-link" style="margin-right:6px; color:#3b82f6"></i>{{ t('settings.agent_url') }}</label>
            <div class="input-with-hint">
              <div style="display: flex; gap: 8px;">
                <input 
                  :value="detectingAgent ? t('settings.detecting_agent') : store.agentUrl" 
                  type="text" 
                  readonly 
                  class="modern-input font-mono readonly-input" 
                  style="flex: 1; color: #475569;" 
                />
                <button 
                  @click="discoverAgent" 
                  class="btn-refresh-printers" 
                  title="Auto-detect Agent" 
                  :disabled="detectingAgent"
                  style="width: 42px; background: #e0e7ff; color: #4f46e5; border-color: #c7d2fe;"
                >
                  <i class="fas fa-search" :class="{'fa-spin': detectingAgent}"></i>
                </button>
              </div>
              <small class="hint-text">{{ t('settings.agent_url_hint') }}</small>
            </div>
          </div>
          <div class="form-group">
            <label><i class="fas fa-folder-open" style="margin-right:6px; color:#f59e0b"></i>{{ t('settings.local_folder') }}</label>
            <input 
              v-model="store.localTemplateDir" 
              type="text" 
              placeholder="C:\NY_Templates\" 
              class="modern-input font-mono" 
              :class="{ 'field-error-input': dirError }"
            />
            <small v-if="dirError" class="error-text-msg">{{ dirError }}</small>
            <small class="hint-text" v-else>{{ t('settings.local_folder_hint') }}</small>
          </div>
        </div>

        <div class="form-group">
          <label> {{ t('settings.station_id') }} </label>
          <div class="mac-display">
            <i class="fas fa-fingerprint"></i>
            <input :value="system.stationId || t('settings.detecting')" readonly class="modern-input readonly-input" />
            <span class="badge-auto">AUTO</span>
          </div>
        </div>

        <!-- Printer Selection -->
        <div class="form-group">
          <label><i class="fas fa-print" style="margin-right:6px; color:#2563eb"></i>{{ t('settings.printer_name') }}</label>
          <div class="input-with-hint">
            <div class="printer-select-wrapper">
              <select v-model="store.printerName" class="modern-input">
                <option value="">-- {{ t('settings.default_printer') }} --</option>
                <option v-for="p in availablePrinters" :key="typeof p === 'string' ? p : p.name" :value="typeof p === 'string' ? p : p.name">
                  🖨️ {{ typeof p === 'string' ? p : p.name }} {{ typeof p === 'string' ? '' : `(${p.port})` }}
                </option>
              </select>
              <button @click="loadPrinters" class="btn-refresh-printers" :title="store.printMode === 'local' ? 'Refresh Local Printers' : 'Refresh Server Printers'">
                <i class="fas fa-sync-alt" :class="{'fa-spin': loadingPrinters}"></i>
              </button>
            </div>
            <small v-if="availablePrinters.length === 0 && !loadingPrinters" class="hint-text">
              {{ t('settings.no_printers_found', { mode: store.printMode === 'local' ? t('settings.agent') : t('settings.server') }) }}
            </small>
            <small v-else>{{ t('settings.printer_list_source', { mode: store.printMode === 'local' ? t('settings.local_agent') : t('settings.backend_server') }) }}</small>
          </div>
        </div>

        <!-- Template Path (Client Fallback) -->
        <div class="form-group" v-if="store.printMode === 'centralized'">
          <label><i class="fas fa-file-alt" style="margin-right:6px; color:#f59e0b"></i>{{ t('settings.fallback_template') }}</label>
          <div class="input-with-hint">
            <input v-model="store.templatePath" type="text" placeholder="D:\Templates\label.btw" class="modern-input font-mono text-xs" />
            <small class="hint-text">{{ t('settings.fallback_template_hint') }}</small>
          </div>
        </div>

        <div class="form-group">
          <label>{{ t('settings.audio_output') }}</label>
          <div class="input-with-hint">
            <select v-model="store.audioDeviceId" class="modern-input"><option value="">{{ t('settings.audio_output_default') }}</option><option v-for="d in audioDevices" :key="d.id" :value="d.id">{{ d.label }}</option></select>
            <small class="hint-text">{{ t('settings.audio_output_hint') }}</small>
          </div>
        </div>
      </div>
      <div class="modal-actions-sticky">
        <button @click="$emit('close')" class="btn-text">{{ t('settings.close') }}</button>
        <button @click="handleSave" class="btn-primary">{{ t('settings.save') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import printApi from '../../print/api';

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);
const { t } = useI18n();
const store = useSettingsStore();
const system = useSystemStore();
const audioDevices = ref([]);
const availablePrinters = ref([]);
const loadingPrinters = ref(false);
const detectingAgent = ref(false);

const discoverAgent = async () => {
  if (store.printMode !== 'local') return;
  detectingAgent.value = true;
  
  // Quét dải cổng rộng hơn để linh hoạt (8000-8010, 8080-8090, 9000-9010)
  const portsToScan = [];
  for (let i = 8000; i <= 8010; i++) portsToScan.push(i);
  for (let i = 8080; i <= 8090; i++) portsToScan.push(i);
  for (let i = 9000; i <= 9010; i++) portsToScan.push(i);
  
  let foundUrl = null;
  
  for (const port of portsToScan) {
    try {
      // Sử dụng 127.0.0.1 thay vì localhost để tránh lỗi phân giải IPv6 trên Windows
      const url = `http://127.0.0.1:${port}`;
      const resp = await fetch(`${url}/status`, { signal: AbortSignal.timeout(500) });
      if (resp.ok) {
        foundUrl = url;
        break;
      }
    } catch (e) {
      // Bỏ qua lỗi timeout
    }
  }
  
  if (foundUrl) {
    store.agentUrl = foundUrl;
    system.showNotification(`Found Agent on port ${foundUrl.split(':').pop()}`, 'success');
    loadPrinters();
    validateDir(store.localTemplateDir);
  } else {
    system.showNotification('Could not detect Agent. Is it running?', 'error');
  }
  detectingAgent.value = false;
};

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
    if (store.printMode === 'local') {
      // Fetch from Local Agent
      try {
        const resp = await fetch(`${store.agentUrl}/printers`);
        if (resp.ok) {
          availablePrinters.value = await resp.json();
          system.showNotification('Đã cập nhật danh sách máy in từ Agent cục bộ', 'success');
        } else {
          throw new Error('Agent trả về lỗi');
        }
      } catch (e) {
        system.showNotification('Không thể kết nối tới Agent! Hãy đảm bảo agent.py đang chạy.', 'error');
        throw e;
      }
    } else {
      // Fetch from Backend Server
      const res = await printApi.getAvailablePrinters();
      if (res.data?.printers) {
        availablePrinters.value = res.data.printers;
      }
    }
  } catch (e) { 
    console.warn('Failed to load printers:', e); 
    availablePrinters.value = [];
  } finally { 
    loadingPrinters.value = false; 
  }
};

const handleSave = () => {
  store.saveSettings();
  emit('close');
  system.showNotification('Settings saved locally', 'success');
};

// Thêm biến để lưu lỗi thư mục
const dirError = ref('');
const validatingDir = ref(false);

const validateDir = async (path) => {
  if (!path || store.printMode !== 'local') {
    dirError.value = '';
    return;
  }
  validatingDir.value = true;
  try {
    const resp = await fetch(`${store.agentUrl}/check-dir?path=${encodeURIComponent(path)}`);
    if (resp.ok) {
      const data = await resp.json();
      dirError.value = data.exists ? '' : 'Thư mục không tồn tại trên máy client!';
    } else {
      dirError.value = 'Không thể kiểm tra thư mục (Lỗi Agent)';
    }
  } catch (e) {
    dirError.value = 'Không thể kết nối tới Agent để kiểm tra thư mục';
  } finally {
    validatingDir.value = false;
  }
};

// Theo dõi sự thay đổi của printMode để load máy in tương ứng ngay lập tức
watch(() => store.printMode, async (newVal) => {
  if (newVal === 'local') {
    await discoverAgent();
  } else {
    loadPrinters();
  }
});

// Theo dõi thư mục để validate ngay khi gõ
watch(() => store.localTemplateDir, (newVal) => {
  validateDir(newVal);
});

watch(() => props.show, async (val) => { 
  if (val) { 
    loadAudioDevices(); 
    if (store.printMode === 'local') {
      await discoverAgent();
    } else {
      loadPrinters(); 
    }
  } 
});
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
.central-print-banner { background: linear-gradient(135deg, #ecfdf5, #d1fae5); border: 1px solid #a7f3d0; color: #065f46; }
.central-print-banner i { color: #10b981; }

.local-banner { background: linear-gradient(135deg, #eff6ff, #dbeafe); border: 1px solid #bfdbfe; color: #1e40af; }
.local-banner i { color: #3b82f6; }

.print-banner { border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: flex-start; gap: 14px; }
.print-banner i { font-size: 1.4rem; margin-top: 2px; }
.print-banner strong { display: block; font-size: 0.9rem; }
.print-banner small { display: block; margin-top: 4px; font-size: 0.75rem; opacity: 0.8; }

.printer-select-wrapper { display: flex; gap: 8px; align-items: center; }
.printer-select-wrapper select { flex: 1; }
.btn-refresh-printers { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #64748b; flex-shrink: 0; }
.btn-refresh-printers:hover { background: #e2e8f0; color: #2563eb; }
.field-error-input {
  border-color: #ef4444 !important;
  background-color: #fef2f2 !important;
}
.error-text-msg {
  color: #ef4444;
  font-size: 0.75rem;
  font-weight: 700;
  margin-top: 4px;
  display: block;
}
</style>
