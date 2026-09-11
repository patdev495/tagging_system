import { ref, onMounted, watch, type Ref } from 'vue';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import printApi from '../../print/api';
import scaleApi from '../../packing/scaleApi';

export interface Printer {
  name: string;
  port?: string;
}

export interface CanonicalTemplate {
  filename: string;
  customer: 'A11' | 'UI';
  type: string;
  name: string;
  desc: string;
}

export const CANONICAL_TEMPLATES: CanonicalTemplate[] = [
  { 
    filename: 'a11_02.btw', 
    customer: 'A11', 
    type: 'a11_tem2', 
    name: 'A11 Tem 2 (Pallet SSCC & ASIN)', 
    desc: 'Hàng G012C1B, G112C1B — In Pallet SSCC-18, ASIN, factory PN' 
  },
  { 
    filename: 'a11.btw', 
    customer: 'A11', 
    type: 'a11', 
    name: 'A11 Tem 1 (Thùng Carton SN + Rev)', 
    desc: 'Hàng 840-00083, 840-00091, 840-00092 — In Carton S/N năm, Rev, MFR P/N' 
  },
  { 
    filename: 'carton_base.btw', 
    customer: 'UI', 
    type: 'standard', 
    name: 'UI Tem Thùng Tiêu Chuẩn', 
    desc: 'Cáp Patch RJ45 tiêu chuẩn 0.3M - 8M, UACC Outdoor 5M-W / 8M-W' 
  },
  { 
    filename: 'Carton_45.btw', 
    customer: 'UI', 
    type: 'standard', 
    name: 'UI Tem Thùng Cáp Dài 4.5M/5M/8M Đen', 
    desc: 'UACC Outdoor 5M-BK, 8M-BK, UACC-G4-INS Cable USB 4.5M' 
  },
  { 
    filename: 'carton_detail_1M_W.btw', 
    customer: 'UI', 
    type: 'detailed', 
    name: 'UI Tem Chi Tiết Cáp 1M', 
    desc: 'UACC Outdoor 1M Trắng & Đen — Lưới 40 mã sê-ri con' 
  },
  { 
    filename: 'carton_detail_2_3M_W.btw', 
    customer: 'UI', 
    type: 'detailed', 
    name: 'UI Tem Chi Tiết Cáp 2M & 3M', 
    desc: 'UACC Outdoor 2M, 3M Trắng & Đen — Lưới 40 mã sê-ri con' 
  },
  { 
    filename: 'carton_detail_UISP_Connector_SHD.btw', 
    customer: 'UI', 
    type: 'detailed', 
    name: 'UI Tem Chi Tiết UISP Connector', 
    desc: 'Đầu nối UISP-Connector-SHD — Lưới mã sê-ri con' 
  },
];

export interface TemplateCheckItem {
  checking: boolean;
  exists?: boolean;
  resolvedPath?: string;
  error?: string;
}

export function useSettingsModal(
  props: { show: boolean } | Ref<{ show: boolean }>,
  emit: (e: 'close') => void
) {
  const store = useSettingsStore();
  const system = useSystemStore();

  const activeTab = ref<'print' | 'scale' | 'system'>('print');
  const bartenderStatus = ref<'ready' | 'offline'>('offline');
  const isRestartingEngine = ref<boolean>(false);
  const dirError = ref<string>('');

  const templateCheckResults = ref<Record<string, TemplateCheckItem>>({});
  const isCheckingTemplates = ref<boolean>(false);

  const formData = ref({
    printMode: store.printMode,
    language: store.language,
    agentUrl: store.agentUrl,
    localTemplateDir: store.localTemplateDir || 'D:\\PAT\\Templates',
    printerName: store.printerName,
    templatePath: store.templatePath,
    audioDeviceId: store.audioDeviceId,
    scalePort: '',
  });

  const checkAllTemplates = async () => {
    isCheckingTemplates.value = true;
    const targetFolder = formData.value.localTemplateDir || 'D:\\PAT\\Templates';
    const mode = formData.value.printMode;
    
    try {
      for (const tpl of CANONICAL_TEMPLATES) {
        templateCheckResults.value[tpl.filename] = { checking: true };
      }

      if (mode === 'local') {
        const agentUrl = formData.value.agentUrl || 'http://127.0.0.1:8080';
        await Promise.all(CANONICAL_TEMPLATES.map(async (tpl) => {
          try {
            const url = `${agentUrl}/check-file?folder=${encodeURIComponent(targetFolder)}&filename=${encodeURIComponent(tpl.filename)}`;
            const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
            if (res.ok) {
              const data = await res.json();
              templateCheckResults.value[tpl.filename] = {
                checking: false,
                exists: !!data.exists,
                resolvedPath: data.path,
              };
            } else {
              templateCheckResults.value[tpl.filename] = {
                checking: false,
                exists: false,
                error: `HTTP ${res.status}`,
              };
            }
          } catch (err: any) {
            templateCheckResults.value[tpl.filename] = {
              checking: false,
              exists: false,
              error: 'Không kết nối được Print Agent máy trạm',
            };
          }
        }));
      } else {
        // Centralized mode: check on server
        try {
          const res = await printApi.getCanonicalTemplates(targetFolder);
          if (res.data && res.data.templates) {
            for (const item of res.data.templates) {
              templateCheckResults.value[item.filename] = {
                checking: false,
                exists: item.exists,
                resolvedPath: item.resolved_path || undefined,
              };
            }
          }
        } catch (err: any) {
          // Fallback to validating individually
          await Promise.all(CANONICAL_TEMPLATES.map(async (tpl) => {
            try {
              const res = await printApi.validateTemplate(tpl.filename, targetFolder);
              templateCheckResults.value[tpl.filename] = {
                checking: false,
                exists: res.data.valid,
                resolvedPath: res.data.resolved_path || undefined,
                error: res.data.valid ? undefined : res.data.message,
              };
            } catch (e: any) {
              templateCheckResults.value[tpl.filename] = {
                checking: false,
                exists: false,
                error: e.message || 'Lỗi kiểm tra server',
              };
            }
          }));
        }
      }

      const total = CANONICAL_TEMPLATES.length;
      const found = Object.values(templateCheckResults.value).filter(r => r.exists).length;
      if (found === total) {
        system.showNotification(`Tìm thấy đầy đủ ${found}/${total} mẫu tem trong thư mục!`, 'success');
      } else {
        system.showNotification(`Tìm thấy ${found}/${total} mẫu tem. Có ${total - found} mẫu tem chưa có trong thư mục!`, 'warning');
      }
    } finally {
      isCheckingTemplates.value = false;
    }
  };

  const audioDevices = ref<{ id: string; label: string }[]>([]);
  const availablePrinters = ref<(string | Printer)[]>([]);
  const loadingPrinters = ref<boolean>(false);
  const detectingAgent = ref<boolean>(false);

  const availableScalePorts = ref<{ device: string; description: string }[]>([]);
  const loadingScale = ref<boolean>(false);

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
        let res = await fetch(`${url}/status`, { signal: AbortSignal.timeout(1000) });
        if (!res.ok) {
          res = await fetch(`${url}/health`, { signal: AbortSignal.timeout(1000) });
        }
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
          const list = (Array.isArray(data) ? data : (data.printers || [])) as (string | Printer)[];
          availablePrinters.value = list.filter(p => p && (typeof p === 'string' || (typeof p === 'object' && (p as any).name)));
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

  watch(() => formData.value.printMode, async (newVal) => {
    availablePrinters.value = [];
    formData.value.printerName = ''; 
    if (newVal === 'local') {
      await discoverAgent();
    } else {
      await loadPrinters();
    }
  });

  watch(() => ('value' in props ? props.value.show : props.show), async (val) => { 
    if (val) { 
      formData.value = {
        printMode: store.printMode,
        language: store.language,
        agentUrl: store.agentUrl,
        localTemplateDir: store.localTemplateDir || 'D:\\PAT\\Templates',
        printerName: store.printerName,
        templatePath: store.templatePath,
        audioDeviceId: store.audioDeviceId,
        scalePort: formData.value.scalePort || '',
      };
      
      loadAudioDevices(); 
      loadScaleStatus();
      checkEngineStatus();
      checkAllTemplates();
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

  return {
    activeTab,
    bartenderStatus,
    isRestartingEngine,
    dirError,
    formData,
    audioDevices,
    availablePrinters,
    loadingPrinters,
    detectingAgent,
    availableScalePorts,
    loadingScale,
    CANONICAL_TEMPLATES,
    templateCheckResults,
    isCheckingTemplates,
    checkAllTemplates,
    checkEngineStatus,
    handleRestartEngine,
    loadScaleStatus,
    loadAudioDevices,
    discoverAgent,
    loadPrinters,
    handleSave,
  };
}
