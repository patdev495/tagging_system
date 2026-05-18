<template>
  <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-[2000]" @click.self="$emit('close')">
    <div class="bg-white p-0 rounded-2xl w-[90%] max-w-[500px] shadow-2xl text-slate-800 overflow-hidden max-h-[90vh] flex flex-col animate-in">
      <div class="px-6 py-5 border-b border-slate-200 flex justify-between items-center bg-white">
        <div class="flex items-center gap-3 text-slate-900"><i class="fas fa-cog"></i><h2 class="m-0 text-[1.25rem] font-bold">{{ t('settings.title') }}</h2></div>
        <button @click="$emit('close')" class="bg-transparent border-none text-slate-400 text-[1.25rem] cursor-pointer transition-colors hover:text-rose-500"><i class="fas fa-times"></i></button>
      </div>
      <div class="px-6 py-5 overflow-y-auto flex-1 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
        <p class="text-slate-500 mb-6 text-[0.9rem]">{{ t('settings.subtitle') }}</p>
        
        <!-- Print Mode Selection -->
        <div class="mb-6">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{{ t('settings.print_mode') }}</label>
          <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-xl">
            <button 
              @click="formData.printMode = 'centralized'"
              :class="['flex flex-col items-center gap-1 py-3 rounded-lg transition-all', formData.printMode === 'centralized' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50']"
            >
              <i class="fas fa-server text-lg"></i>
              <span class="text-[10px] font-black uppercase">{{ t('settings.centralized') }}</span>
            </button>
            <button 
              @click="formData.printMode = 'local'"
              :class="['flex flex-col items-center gap-1 py-3 rounded-lg transition-all', formData.printMode === 'local' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50']"
            >
              <i class="fas fa-desktop text-lg"></i>
              <span class="text-[10px] font-black uppercase">{{ t('settings.local_agent') }}</span>
            </button>
          </div>
        </div>

        <!-- Language Selection -->
        <div class="mb-4">
          <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600"><i class="fas fa-globe mr-1.5 text-emerald-500"></i>{{ t('settings.language') }}</label>
          <div class="input-with-hint">
            <select v-model="formData.language" class="w-full px-3.5 py-2.5 border border-slate-200 rounded-lg text-[0.95rem] bg-slate-50 text-slate-800 outline-none transition-all focus:border-blue-500 focus:bg-white">
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div v-if="formData.printMode === 'centralized'" class="rounded-xl p-3.5 md:p-4.5 mb-5 flex items-start gap-3.5 bg-linear-to-br from-emerald-50 to-emerald-100 border border-emerald-200 text-emerald-900 animate-in">
          <i class="fas fa-server text-[1.4rem] mt-0.5 text-emerald-500"></i>
          <div>
            <strong class="block text-[0.9rem] font-bold">{{ t('settings.centralized_title') }}</strong>
            <small class="block mt-1 text-[0.75rem] opacity-80">{{ t('settings.centralized_desc') }}</small>
          </div>
        </div>

        <div v-else class="rounded-xl p-3.5 md:p-4.5 mb-5 flex items-start gap-3.5 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 text-blue-900 animate-in">
          <i class="fas fa-bolt text-[1.4rem] mt-0.5 text-blue-500"></i>
          <div>
            <strong class="block text-[0.9rem] font-bold">{{ t('settings.local_title') }}</strong>
            <small class="block mt-1 text-[0.75rem] opacity-80">{{ t('settings.local_desc') }}</small>
          </div>
        </div>

        <!-- Agent Configuration (Only if local) -->
        <div v-if="formData.printMode === 'local'" class="animate-in slide-in-from-top-2 duration-300">
          <div class="mb-4">
            <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600"><i class="fas fa-link mr-1.5 text-blue-500"></i>{{ t('settings.agent_url') }}</label>
            <div class="input-with-hint">
              <div class="flex gap-2">
                <input 
                  :value="detectingAgent ? t('settings.detecting_agent') : formData.agentUrl" 
                  type="text" 
                  readonly 
                  class="flex-1 px-3.5 py-2.5 border border-slate-200 rounded-lg text-[0.95rem] bg-slate-100 text-slate-500 outline-none transition-all font-mono border-dashed cursor-not-allowed" 
                />
                <button 
                  @click="discoverAgent" 
                  class="w-[42px] h-[42px] bg-indigo-50 text-indigo-600 border border-indigo-200 rounded-lg flex items-center justify-center cursor-pointer transition-all hover:bg-indigo-100 disabled:opacity-50" 
                  title="Auto-detect Agent" 
                  :disabled="detectingAgent"
                >
                  <i class="fas fa-search" :class="{'fa-spin': detectingAgent}"></i>
                </button>
              </div>
              <small class="block mt-1.5 text-[0.75rem] text-slate-500 bg-slate-100 p-2 rounded-md leading-relaxed">{{ t('settings.agent_url_hint') }}</small>
            </div>
          </div>
          <div class="mb-4">
            <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600"><i class="fas fa-folder-open mr-1.5 text-orange-500"></i>{{ t('settings.local_folder') }}</label>
            <input 
              v-model="formData.localTemplateDir" 
              type="text" 
              placeholder="C:\NY_Templates\" 
              class="w-full px-3.5 py-2.5 border border-slate-200 rounded-lg text-[0.95rem] bg-slate-50 text-slate-800 outline-none transition-all font-mono focus:border-blue-500 focus:bg-white" 
              :class="{ 'border-rose-500 bg-rose-50': dirError }"
            />
            <small v-if="dirError" class="block mt-1 text-rose-500 text-[0.75rem] font-bold">{{ dirError }}</small>
            <small class="block mt-1.5 text-[0.75rem] text-slate-500 bg-slate-100 p-2 rounded-md leading-relaxed" v-else>{{ t('settings.local_folder_hint') }}</small>
          </div>
        </div>

        <div class="mb-4">
          <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600"> {{ t('settings.station_id') }} </label>
          <div class="relative flex items-center">
            <i class="fas fa-fingerprint absolute left-3 text-blue-500 text-[0.9rem]"></i>
            <input :value="system.stationId || t('settings.detecting')" readonly class="w-full pl-9 pr-15 py-2.5 border border-slate-200 rounded-lg text-[0.95rem] bg-slate-100 text-slate-500 outline-none transition-all border-dashed cursor-not-allowed" />
            <span class="absolute right-2.5 bg-emerald-50 text-emerald-600 text-[0.65rem] font-black px-1.5 py-0.5 rounded border border-emerald-100">AUTO</span>
          </div>
        </div>

        <!-- Printer Selection -->
        <div class="mb-4">
          <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600"><i class="fas fa-print mr-1.5 text-blue-600"></i>{{ t('settings.printer_name') }}</label>
          <div class="input-with-hint">
            <div class="flex gap-2 items-center">
              <select v-model="formData.printerName" class="flex-1 px-3.5 py-2.5 border border-slate-200 rounded-lg text-[0.95rem] bg-slate-50 text-slate-800 outline-none transition-all focus:border-blue-500 focus:bg-white">
                <option value="">-- {{ t('settings.default_printer') }} --</option>
                <option v-if="formData.printerName && !availablePrinters.some(p => (typeof p === 'string' ? p : p.name) === formData.printerName)" :value="formData.printerName">
                  🖨️ {{ formData.printerName }} ({{ t('settings.selected') || 'Selected' }})
                </option>
                <option v-for="p in availablePrinters" :key="typeof p === 'string' ? p : (p.name || Math.random().toString())" :value="typeof p === 'string' ? p : p.name">
                  🖨️ {{ typeof p === 'string' ? p : (p.name || 'Unknown Printer') }} {{ typeof p === 'string' ? '' : (p.port ? `(${p.port})` : '') }}
                </option>
              </select>
              <button @click="loadPrinters" class="w-10 h-10 flex-shrink-0 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-center cursor-pointer text-slate-500 transition-all hover:bg-slate-100 hover:text-blue-600" :title="formData.printMode === 'local' ? 'Refresh Local Printers' : 'Refresh Server Printers'">
                <i class="fas fa-sync-alt" :class="{'fa-spin': loadingPrinters}"></i>
              </button>
            </div>
            <small v-if="availablePrinters.length === 0 && !loadingPrinters" class="block mt-1.5 text-[0.75rem] text-slate-500 bg-slate-100 p-2 rounded-md leading-relaxed">
              {{ t('settings.no_printers_found', { mode: formData.printMode === 'local' ? t('settings.agent') : t('settings.server') }) }}
            </small>
            <small class="block mt-1 text-[0.75rem] text-blue-600" v-else>{{ t('settings.printer_list_source', { mode: formData.printMode === 'local' ? t('settings.local_agent') : t('settings.backend_server') }) }}</small>
          </div>
        </div>

        <!-- Template Path (Client Fallback) -->
        <div class="mb-4" v-if="formData.printMode === 'centralized'">
          <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600"><i class="fas fa-file-alt mr-1.5 text-orange-500"></i>{{ t('settings.fallback_template') }}</label>
          <div class="input-with-hint">
            <input v-model="formData.templatePath" type="text" placeholder="D:\Templates\label.btw" class="w-full px-3.5 py-2.5 border border-slate-200 rounded-lg text-xs bg-slate-50 text-slate-800 outline-none transition-all font-mono focus:border-blue-500 focus:bg-white" />
            <small class="block mt-1.5 text-[0.75rem] text-slate-500 bg-slate-100 p-2 rounded-md leading-relaxed">{{ t('settings.fallback_template_hint') }}</small>
          </div>
        </div>

        <div class="mb-4">
          <label class="block mb-1.5 font-semibold text-[0.85rem] text-slate-600">{{ t('settings.audio_output') }}</label>
          <div class="input-with-hint">
            <select v-model="formData.audioDeviceId" class="w-full px-3.5 py-2.5 border border-slate-200 rounded-lg text-[0.95rem] bg-slate-50 text-slate-800 outline-none transition-all focus:border-blue-500 focus:bg-white"><option value="">{{ t('settings.audio_output_default') }}</option><option v-for="d in audioDevices" :key="d.id" :value="d.id">{{ d.label }}</option></select>
            <small class="block mt-1.5 text-[0.75rem] text-slate-500 bg-slate-100 p-2 rounded-md leading-relaxed">{{ t('settings.audio_output_hint') }}</small>
          </div>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-slate-200 bg-slate-50 flex justify-end gap-4 mt-auto">
        <button @click="$emit('close')" class="bg-transparent text-slate-500 border-none px-5 py-2.5 cursor-pointer font-medium transition-colors hover:text-slate-900">{{ t('settings.close') }}</button>
        <button @click="handleSave" class="bg-blue-600 text-white px-5 py-2.5 rounded-lg border-none font-semibold cursor-pointer transition-colors hover:bg-blue-700">{{ t('settings.save') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import printApi from '../../print/api';

const props = defineProps<{
  show: boolean
}>();

const emit = defineEmits<{
  (e: 'close'): void
}>();

const { t } = useI18n();
const store = useSettingsStore();
const system = useSystemStore();

interface AudioDevice {
  id: string;
  label: string;
}

interface Printer {
  name: string;
  port?: string;
}

const audioDevices = ref<AudioDevice[]>([]);
const availablePrinters = ref<(string | Printer)[]>([]);
const loadingPrinters = ref<boolean>(false);
const detectingAgent = ref<boolean>(false);

const formData = ref({
  printMode: store.printMode,
  language: store.language,
  agentUrl: store.agentUrl,
  localTemplateDir: store.localTemplateDir,
  printerName: store.printerName,
  templatePath: store.templatePath,
  audioDeviceId: store.audioDeviceId
});

const discoverAgent = async () => {
  if (formData.value.printMode !== 'local') return;
  availablePrinters.value = [];
  detectingAgent.value = true;
  
  const portsToScan: number[] = [8080, 8081, 8082, 8001, 8000, 9000];
  
  let foundUrl: string | null = null;
  
  for (const port of portsToScan) {
    try {
      const url = `http://127.0.0.1:${port}`;
      // @ts-ignore - AbortSignal.timeout is relatively new
      const resp = await fetch(`${url}/status`, { signal: (AbortSignal as any).timeout ? (AbortSignal as any).timeout(500) : undefined });
      if (resp.ok) {
        const data = await resp.json();
        // Verify this is actually the Print Agent (Agent returns mode: 'COM')
        if (data.mode === 'COM') {
          foundUrl = url;
          break;
        }
      }
    } catch (e) {
      // Ignore
    }
  }
  
  if (foundUrl) {
    formData.value.agentUrl = foundUrl;
    system.showNotification(`Found Agent on port ${foundUrl.split(':').pop()}`, 'success');
    loadPrinters();
    validateDir(formData.value.localTemplateDir);
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
// Consolidated watcher for print mode below

const loadPrinters = async () => {
  loadingPrinters.value = true;
  try {
    if (formData.value.printMode === 'local') {
      try {
        const resp = await fetch(`${formData.value.agentUrl}/printers`);
        if (resp.ok) {
          const raw = await resp.json();
          // Agent returns list directly or {"printers": [...]}
          const list = (Array.isArray(raw) ? raw : (raw.printers || [])) as (string | Printer)[];
          availablePrinters.value = list.filter(p => p && (typeof p === 'string' || (typeof p === 'object' && (p as any).name)));
          system.showNotification('Đã cập nhật danh sách máy in từ Agent cục bộ', 'success');
        } else {
          throw new Error('Agent trả về lỗi');
        }
      } catch (e) {
        system.showNotification('Không thể kết nối tới Agent! Hãy đảm bảo agent.py đang chạy.', 'error');
        throw e;
      }
    } else {
      const res = await printApi.getAvailablePrinters();
      const data = res.data as any;
      const list = (Array.isArray(data) ? data : (data.printers || [])) as (string | Printer)[];
      availablePrinters.value = list.filter(p => p && (typeof p === 'string' || (typeof p === 'object' && (p as any).name)));
    }
  } catch (e) { 
    console.warn('Failed to load printers:', e); 
    availablePrinters.value = [];
  } finally { 
    loadingPrinters.value = false; 
  }
};

const handleSave = () => {
  store.printMode = formData.value.printMode;
  store.language = formData.value.language;
  store.agentUrl = formData.value.agentUrl;
  store.localTemplateDir = formData.value.localTemplateDir;
  store.printerName = formData.value.printerName;
  store.templatePath = formData.value.templatePath;
  store.audioDeviceId = formData.value.audioDeviceId;
  
  store.saveSettings();
  emit('close');
  system.showNotification('Settings saved locally', 'success');
};

const dirError = ref<string>('');
const validatingDir = ref<boolean>(false);

const validateDir = async (path: string) => {
  if (!path || store.printMode !== 'local') {
    dirError.value = '';
    return;
  }
  validatingDir.value = true;
  try {
    const resp = await fetch(`${formData.value.agentUrl}/check-dir?path=${encodeURIComponent(path)}`);
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

watch(() => formData.value.printMode, async (newVal) => {
  // Immediately clear printers when switching modes
  availablePrinters.value = [];
  formData.value.printerName = ''; 
  
  if (newVal === 'local') {
    await discoverAgent();
  } else {
    await loadPrinters();
  }
});

watch(() => formData.value.localTemplateDir, (newVal) => {
  validateDir(newVal);
});

watch(() => props.show, async (val) => { 
  if (val) { 
    // Reset formData to current store state
    formData.value = {
      printMode: store.printMode,
      language: store.language,
      agentUrl: store.agentUrl,
      localTemplateDir: store.localTemplateDir,
      printerName: store.printerName,
      templatePath: store.templatePath,
      audioDeviceId: store.audioDeviceId
    };
    
    loadAudioDevices(); 
    if (formData.value.printMode === 'local') {
      await discoverAgent();
    } else {
      loadPrinters(); 
    }
  } 
});
onMounted(() => { loadAudioDevices(); });
</script>
