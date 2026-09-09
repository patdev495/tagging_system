<template>
  <div v-if="show" class="fixed inset-0 bg-slate-900/75 flex justify-center items-center z-[2000] p-3 md:p-6" @click.self="$emit('close')" role="dialog" aria-modal="true">
    <div class="bg-white rounded-xl w-full max-w-[620px] shadow-2xl text-slate-800 border border-slate-300 overflow-hidden max-h-[90vh] flex flex-col animate-in">
      <!-- Header -->
      <div class="px-5 py-3.5 border-b border-slate-200 flex justify-between items-center bg-slate-50 shrink-0">
        <div class="flex items-center gap-2.5 text-slate-900">
          <div class="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
            <i class="fas fa-sliders text-sm"></i>
          </div>
          <div>
            <h2 class="m-0 text-base font-black text-slate-900 leading-tight">{{ t('settings.title') }}</h2>
            <p class="m-0 text-xs text-slate-500">{{ t('settings.subtitle') }}</p>
          </div>
        </div>
        <button 
          @click="$emit('close')" 
          class="w-8 h-8 rounded-lg bg-white hover:bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-500 hover:text-slate-800 cursor-pointer transition-colors"
          title="Đóng (Esc)"
        >
          <i class="fas fa-times text-sm"></i>
        </button>
      </div>

      <!-- Tab Navigation Bar -->
      <div class="px-5 pt-2 border-b border-slate-200 bg-slate-100/60 flex gap-2 shrink-0">
        <button 
          type="button"
          @click="activeTab = 'print'" 
          :class="['px-3.5 py-2 font-bold text-xs rounded-t-lg transition-colors border-t border-x cursor-pointer flex items-center gap-1.5', activeTab === 'print' ? 'bg-white border-slate-200 text-blue-700 -mb-px shadow-2xs' : 'bg-transparent border-transparent text-slate-600 hover:text-slate-900']"
        >
          <i class="fas fa-print"></i>
          <span>Máy In & BarTender</span>
        </button>
        <button 
          type="button"
          @click="activeTab = 'scale'" 
          :class="['px-3.5 py-2 font-bold text-xs rounded-t-lg transition-colors border-t border-x cursor-pointer flex items-center gap-1.5', activeTab === 'scale' ? 'bg-white border-slate-200 text-emerald-700 -mb-px shadow-2xs' : 'bg-transparent border-transparent text-slate-600 hover:text-slate-900']"
        >
          <i class="fas fa-weight-scale"></i>
          <span>Cân Điện Tử (RS-232)</span>
        </button>
        <button 
          type="button"
          @click="activeTab = 'system'" 
          :class="['px-3.5 py-2 font-bold text-xs rounded-t-lg transition-colors border-t border-x cursor-pointer flex items-center gap-1.5', activeTab === 'system' ? 'bg-white border-slate-200 text-slate-900 -mb-px shadow-2xs' : 'bg-transparent border-transparent text-slate-600 hover:text-slate-900']"
        >
          <i class="fas fa-gear"></i>
          <span>Hệ Thống & Thiết Bị</span>
        </button>
      </div>

      <!-- Tab Content Area (Scrollable) -->
      <div class="px-6 py-4 overflow-y-auto flex-1 space-y-4 text-xs">
        
        <!-- ================= TAB 1: MÁY IN & BARTENDER ================= -->
        <div v-show="activeTab === 'print'" class="space-y-4 animate-in">
          <!-- Print Mode Toggle -->
          <div>
            <label class="block font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              {{ t('settings.print_mode') }}
            </label>
            <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-lg border border-slate-200">
              <button 
                type="button"
                @click="formData.printMode = 'centralized'"
                :class="['flex items-center justify-center gap-2 py-2 rounded-md font-bold transition-colors cursor-pointer', formData.printMode === 'centralized' ? 'bg-white text-blue-700 shadow-xs border border-slate-200' : 'text-slate-600 hover:bg-slate-200/50']"
              >
                <i class="fas fa-server"></i>
                <span>{{ t('settings.centralized') }}</span>
              </button>
              <button 
                type="button"
                @click="formData.printMode = 'local'"
                :class="['flex items-center justify-center gap-2 py-2 rounded-md font-bold transition-colors cursor-pointer', formData.printMode === 'local' ? 'bg-white text-blue-700 shadow-xs border border-slate-200' : 'text-slate-600 hover:bg-slate-200/50']"
              >
                <i class="fas fa-desktop"></i>
                <span>{{ t('settings.local_agent') }}</span>
              </button>
            </div>
          </div>

          <!-- Mode Info Banner -->
          <div v-if="formData.printMode === 'centralized'" class="rounded-lg p-3 bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-start gap-2.5">
            <i class="fas fa-server text-base text-emerald-600 mt-0.5"></i>
            <div>
              <strong class="block font-bold">{{ t('settings.centralized_title') }}</strong>
              <span class="block mt-0.5 text-slate-600">{{ t('settings.centralized_desc') }}</span>
            </div>
          </div>

          <div v-else class="rounded-lg p-3 bg-blue-50 border border-blue-200 text-blue-900 flex items-start gap-2.5">
            <i class="fas fa-bolt text-base text-blue-600 mt-0.5"></i>
            <div>
              <strong class="block font-bold">{{ t('settings.local_title') }}</strong>
              <span class="block mt-0.5 text-slate-600">{{ t('settings.local_desc') }}</span>
            </div>
          </div>

          <!-- Agent URL & Template Folder (if local) -->
          <div v-if="formData.printMode === 'local'" class="space-y-3 bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <div>
              <label class="block mb-1 font-bold text-slate-700">
                <i class="fas fa-link mr-1 text-blue-600"></i>{{ t('settings.agent_url') }}
              </label>
              <div class="flex gap-2">
                <input 
                  :value="detectingAgent ? t('settings.detecting_agent') : formData.agentUrl" 
                  type="text" 
                  readonly 
                  class="flex-1 h-9 px-3 border border-slate-300 rounded-lg bg-slate-100 text-slate-600 font-barcode-mono font-bold cursor-not-allowed" 
                />
                <button 
                  type="button"
                  @click="discoverAgent" 
                  class="h-9 px-3 bg-blue-50 text-blue-700 border border-blue-300 rounded-lg font-bold flex items-center gap-1.5 cursor-pointer hover:bg-blue-100 disabled:opacity-50" 
                  title="Tự động tìm kiếm Print Agent" 
                  :disabled="detectingAgent"
                >
                  <i class="fas fa-search" :class="{'fa-spin': detectingAgent}"></i>
                  <span>Dò Agent</span>
                </button>
              </div>
            </div>

            <div>
              <label class="block mb-1 font-bold text-slate-700">
                <i class="fas fa-folder-open mr-1 text-amber-600"></i>{{ t('settings.local_folder') }}
              </label>
              <input 
                v-model="formData.localTemplateDir" 
                type="text" 
                placeholder="C:\NY_Templates\" 
                class="w-full h-9 px-3 border border-slate-300 rounded-lg bg-white text-slate-900 font-barcode-mono" 
                :class="{ 'border-rose-500 bg-rose-50': dirError }"
              />
              <small v-if="dirError" class="block mt-1 text-rose-600 font-bold">{{ dirError }}</small>
            </div>
          </div>

          <!-- Printer Selection -->
          <div>
            <label class="block mb-1 font-bold text-slate-700">
              <i class="fas fa-print mr-1 text-blue-600"></i>{{ t('settings.printer_name') }}
            </label>
            <div class="flex gap-2 items-center">
              <select v-model="formData.printerName" class="flex-1 h-9 px-3 border border-slate-300 rounded-lg bg-white text-slate-900 font-medium">
                <option value="">-- {{ t('settings.default_printer') }} --</option>
                <option v-if="formData.printerName && !availablePrinters.some(p => (typeof p === 'string' ? p : p.name) === formData.printerName)" :value="formData.printerName">
                  🖨️ {{ formData.printerName }} ({{ t('settings.selected') || 'Selected' }})
                </option>
                <option v-for="p in availablePrinters" :key="typeof p === 'string' ? p : (p.name || Math.random().toString())" :value="typeof p === 'string' ? p : p.name">
                  🖨️ {{ typeof p === 'string' ? p : (p.name || 'Unknown Printer') }} {{ typeof p === 'string' ? '' : (p.port ? `(${p.port})` : '') }}
                </option>
              </select>
              <button 
                type="button"
                @click="loadPrinters" 
                class="h-9 px-3 bg-slate-100 border border-slate-300 rounded-lg flex items-center gap-1 cursor-pointer text-slate-700 hover:bg-slate-200" 
                title="Làm mới danh sách máy in"
              >
                <i class="fas fa-sync-alt" :class="{'fa-spin': loadingPrinters}"></i>
                <span>Tải lại</span>
              </button>
            </div>
          </div>

          <!-- BarTender Engine Diagnostics -->
          <div class="p-3.5 rounded-lg border border-slate-200 bg-slate-50 space-y-2">
            <div class="flex items-center justify-between">
              <label class="font-bold text-slate-800 flex items-center gap-1.5 m-0">
                <i class="fas fa-stethoscope text-indigo-600"></i>
                <span>Chẩn Đoán BarTender COM Engine</span>
              </label>
              <span :class="['text-[10px] font-black uppercase px-2 py-0.5 rounded-full flex items-center gap-1', bartenderStatus === 'ready' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-rose-100 text-rose-800 border border-rose-300']">
                <span class="w-1.5 h-1.5 rounded-full" :class="bartenderStatus === 'ready' ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                <span>{{ bartenderStatus === 'ready' ? 'Sẵn Sàng' : 'Offline' }}</span>
              </span>
            </div>
            
            <p class="text-[11px] text-slate-500 m-0 leading-relaxed">
              Trạng thái tích hợp BarTender COM. Nếu lệnh in bị đứng do tiến trình <code class="font-mono text-slate-700 bg-slate-200 px-1 rounded">bartend.exe</code> bị treo, quản trị viên có thể bấm khởi động lại để giải phóng.
            </p>

            <div v-if="authStore.isAdmin" class="pt-1">
              <button 
                type="button"
                @click="handleRestartEngine" 
                :disabled="isRestartingEngine"
                class="h-8 w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer border-none"
              >
                <i class="fas fa-arrows-rotate" :class="{ 'fa-spin': isRestartingEngine }"></i>
                <span>{{ isRestartingEngine ? 'Đang giải phóng bartend.exe...' : 'Khởi Động Lại BarTender COM Engine' }}</span>
              </button>
            </div>
            <div v-else class="text-[10px] text-slate-400 italic">
              (Chức năng khởi động lại Engine chỉ áp dụng cho quyền Admin)
            </div>
          </div>
        </div>

        <!-- ================= TAB 2: CÂN ĐIỆN TỬ (RS-232) ================= -->
        <div v-show="activeTab === 'scale'" class="space-y-4 animate-in">
          <div>
            <label class="block mb-1 font-bold text-slate-700">
              <i class="fas fa-weight-scale mr-1 text-emerald-600"></i>Cổng COM Cân Điện Tử (Scale Port)
            </label>
            <div class="flex gap-2 items-center">
              <select v-model="formData.scalePort" class="flex-1 h-9 px-3 border border-slate-300 rounded-lg bg-white text-slate-900 font-medium">
                <option value="">-- Mặc định / Tự động nhận diện --</option>
                <option v-if="formData.scalePort && !availableScalePorts.some(p => p.device === formData.scalePort)" :value="formData.scalePort">
                  ⚖️ {{ formData.scalePort }} (Đang chọn)
                </option>
                <option v-for="p in availableScalePorts" :key="p.device" :value="p.device">
                  ⚖️ {{ p.device }} ({{ p.description || 'Cổng COM' }})
                </option>
              </select>
              <button 
                type="button"
                @click="loadScaleStatus" 
                class="h-9 px-3 bg-slate-100 border border-slate-300 rounded-lg flex items-center gap-1 cursor-pointer text-slate-700 hover:bg-slate-200" 
                title="Quét lại các cổng COM"
              >
                <i class="fas fa-sync-alt" :class="{'fa-spin': loadingScale}"></i>
                <span>Quét Cổng</span>
              </button>
            </div>
            <small class="block mt-1.5 text-slate-500 text-[11px]">
              Đảm bảo đầu cân được kết nối qua cáp RS-232 / USB-Serial ở chế độ phát luồng liên tục (Continuous Streaming).
            </small>
          </div>

          <!-- Scale Live Diagnostic Card -->
          <div class="p-3.5 rounded-lg border border-slate-200 bg-slate-50 space-y-2">
            <span class="font-bold text-slate-800 block">Thông số kỹ thuật chuẩn:</span>
            <ul class="list-disc pl-4 space-y-1 text-slate-600 text-[11px]">
              <li>Tốc độ truyền (Baudrate): <strong>9600 bps</strong></li>
              <li>Data Bits: <strong>8</strong> • Stop Bits: <strong>1</strong> • Parity: <strong>None</strong></li>
              <li>Thao tác trừ bì (Tare) và trả về điểm 0 (Zero) thực hiện trực tiếp trên bàn phím vật lý của đầu cân.</li>
            </ul>
          </div>
        </div>

        <!-- ================= TAB 3: HỆ THỐNG & THIẾT BỊ ================= -->
        <div v-show="activeTab === 'system'" class="space-y-4 animate-in">
          <!-- Language -->
          <div>
            <label class="block mb-1 font-bold text-slate-700">
              <i class="fas fa-globe mr-1 text-blue-600"></i>{{ t('settings.language') }}
            </label>
            <select v-model="formData.language" class="w-full h-9 px-3 border border-slate-300 rounded-lg bg-white text-slate-900 font-medium">
              <option value="vi">Tiếng Việt (Mặc định)</option>
              <option value="en">English</option>
            </select>
          </div>

          <!-- Station ID -->
          <div>
            <label class="block mb-1 font-bold text-slate-700">
              <i class="fas fa-fingerprint mr-1 text-slate-600"></i>{{ t('settings.station_id') }}
            </label>
            <div class="relative flex items-center">
              <input 
                :value="system.stationId || t('settings.detecting')" 
                readonly 
                class="w-full h-9 px-3 border border-slate-300 rounded-lg bg-slate-100 text-slate-600 font-barcode-mono font-bold cursor-not-allowed" 
              />
              <span class="absolute right-2.5 bg-slate-200 text-slate-700 text-[10px] font-black px-1.5 py-0.5 rounded">
                AUTO
              </span>
            </div>
          </div>

          <!-- Audio Device Output -->
          <div>
            <label class="block mb-1 font-bold text-slate-700">
              <i class="fas fa-volume-high mr-1 text-emerald-600"></i>{{ t('settings.audio_output') }}
            </label>
            <select v-model="formData.audioDeviceId" class="w-full h-9 px-3 border border-slate-300 rounded-lg bg-white text-slate-900 font-medium">
              <option value="">{{ t('settings.audio_output_default') }}</option>
              <option v-for="d in audioDevices" :key="d.id" :value="d.id">{{ d.label }}</option>
            </select>
            <small class="block mt-1 text-slate-500 text-[11px]">{{ t('settings.audio_output_hint') }}</small>
          </div>
        </div>

      </div>

      <!-- Pinned Footer Buttons -->
      <div class="px-5 py-3 border-t border-slate-200 bg-slate-100 flex justify-end gap-2.5 shrink-0">
        <button 
          type="button"
          @click="$emit('close')" 
          class="h-9 px-4 rounded-lg border border-slate-300 bg-white text-slate-700 font-bold cursor-pointer transition-colors hover:bg-slate-50 hover:text-slate-900 text-xs"
        >
          {{ t('settings.close') }}
        </button>
        <button 
          type="button"
          @click="handleSave" 
          class="h-9 px-5 rounded-lg bg-blue-600 text-white font-bold cursor-pointer transition-colors hover:bg-blue-700 text-xs shadow-xs active:scale-95"
        >
          {{ t('settings.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import { useAuthStore } from '../../../core/stores/auth';
import printApi from '../../print/api';
import scaleApi from '../../packing/scaleApi';

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const { t } = useI18n();
const store = useSettingsStore();
const system = useSystemStore();
const authStore = useAuthStore();

const activeTab = ref<'print' | 'scale' | 'system'>('print');
const bartenderStatus = ref<'ready' | 'offline'>('offline');
const isRestartingEngine = ref<boolean>(false);

const checkEngineStatus = async () => {
  try {
    const res = await printApi.getPrintConfig();
    bartenderStatus.value = res.data.bartender_ready ? 'ready' : 'offline';
  } catch (err) {
    bartenderStatus.value = 'offline';
  }
};

const handleRestartEngine = async () => {
  if (!confirm('Bạn có chắc chắn muốn giải phóng tiến trình bartend.exe và khởi động lại BarTender COM Engine?')) {
    return;
  }
  isRestartingEngine.value = true;
  try {
    const res = await printApi.restartEngine();
    if (res.data.success) {
      bartenderStatus.value = res.data.bartender_ready ? 'ready' : 'offline';
      system.showNotification('Đã khởi động lại BarTender COM Engine thành công!', 'success');
      loadPrinters();
    } else {
      system.showNotification('Khởi động lại thất bại: ' + (res.data.message || 'Lỗi không xác định'), 'error');
    }
  } catch (err: any) {
    system.showNotification('Lỗi khi gọi khởi động lại BarTender Engine: ' + (err.message || ''), 'error');
  } finally {
    isRestartingEngine.value = false;
  }
};

interface Printer {
  name: string;
  port?: string;
}

const formData = ref({
  printMode: store.printMode,
  language: store.language,
  agentUrl: store.agentUrl,
  localTemplateDir: store.localTemplateDir,
  printerName: store.printerName,
  templatePath: store.templatePath,
  audioDeviceId: store.audioDeviceId,
  scalePort: '',
});

const audioDevices = ref<{ id: string; label: string }[]>([]);
const availablePrinters = ref<(string | Printer)[]>([]);
const loadingPrinters = ref<boolean>(false);
const detectingAgent = ref<boolean>(false);

const availableScalePorts = ref<{ device: string; description: string }[]>([]);
const loadingScale = ref<boolean>(false);

const loadScaleStatus = async () => {
  loadingScale.value = true;
  try {
    const targetUrl = formData.value.printMode === 'local' 
      ? (formData.value.agentUrl || 'http://127.0.0.1:8080')
      : 'http://127.0.0.1:8080';
    const res = await scaleApi.getScalePorts(targetUrl);
    availableScalePorts.value = res.ports || [];
  } catch (err) {
    availableScalePorts.value = [];
  } finally {
    loadingScale.value = false;
  }
};

const loadAudioDevices = async () => {
  try {
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
      const devices = await navigator.mediaDevices.enumerateDevices();
      audioDevices.value = devices
        .filter(d => d.kind === 'audiooutput')
        .map((d, index) => ({
          id: d.deviceId,
          label: d.label || `Thiết bị phát ${index + 1}`
        }));
    }
  } catch (e) {
    console.warn('Cannot enumerate audio devices:', e);
  }
};

const discoverAgent = async () => {
  detectingAgent.value = true;
  const testPorts = [8080, 8081, 8082];
  let found = false;
  for (const port of testPorts) {
    const url = `http://127.0.0.1:${port}`;
    try {
      const res = await fetch(`${url}/health`, { signal: AbortSignal.timeout(1000) });
      if (res.ok) {
        formData.value.agentUrl = url;
        found = true;
        system.showNotification(`Đã tìm thấy Local Agent tại ${url}`, 'success');
        break;
      }
    } catch {}
  }
  if (!found) {
    system.showNotification('Không tìm thấy Local Agent đang chạy (Cổng 8080, 8081, 8082)', 'warning');
  }
  detectingAgent.value = false;
  if (found) loadPrinters();
};

const loadPrinters = async () => {
  loadingPrinters.value = true;
  try {
    if (formData.value.printMode === 'local') {
      const targetUrl = formData.value.agentUrl || 'http://127.0.0.1:8080';
      const res = await fetch(`${targetUrl}/printers`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        availablePrinters.value = data.printers || [];
      } else {
        availablePrinters.value = [];
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

const handleSave = async () => {
  store.printMode = formData.value.printMode;
  store.language = formData.value.language;
  store.agentUrl = formData.value.agentUrl;
  store.localTemplateDir = formData.value.localTemplateDir;
  store.printerName = formData.value.printerName;
  store.templatePath = formData.value.templatePath;
  store.audioDeviceId = formData.value.audioDeviceId;
  
  if (formData.value.scalePort) {
    try {
      await scaleApi.updateScaleConfig(
        { port: formData.value.scalePort },
        formData.value.agentUrl || 'http://127.0.0.1:8080'
      );
    } catch (err: any) {
      console.warn('Could not update scale port on agent:', err);
    }
  }

  store.saveSettings();
  emit('close');
  system.showNotification('Cài đặt đã được lưu thành công', 'success');
};

const dirError = ref<string>('');

watch(() => formData.value.printMode, async (newVal) => {
  availablePrinters.value = [];
  formData.value.printerName = ''; 
  if (newVal === 'local') {
    await discoverAgent();
  } else {
    await loadPrinters();
  }
});

watch(() => props.show, async (val) => { 
  if (val) { 
    formData.value = {
      printMode: store.printMode,
      language: store.language,
      agentUrl: store.agentUrl,
      localTemplateDir: store.localTemplateDir,
      printerName: store.printerName,
      templatePath: store.templatePath,
      audioDeviceId: store.audioDeviceId,
      scalePort: formData.value.scalePort || '',
    };
    
    loadAudioDevices(); 
    loadScaleStatus();
    checkEngineStatus();
    if (formData.value.printMode === 'local') {
      await discoverAgent();
    } else {
      loadPrinters(); 
    }
  } 
});

onMounted(() => { 
  loadAudioDevices(); 
  loadScaleStatus();
  checkEngineStatus();
});
</script>
