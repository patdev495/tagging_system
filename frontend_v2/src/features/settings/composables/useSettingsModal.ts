import { ref, onMounted, watch, type Ref } from 'vue';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import printApi from '../../print/api';
import scaleApi from '../../packing/scaleApi';

export interface Printer {
  name: string;
  port?: string;
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
    checkEngineStatus,
    handleRestartEngine,
    loadScaleStatus,
    loadAudioDevices,
    discoverAgent,
    loadPrinters,
    handleSave,
  };
}
