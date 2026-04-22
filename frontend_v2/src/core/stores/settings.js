import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export const useSettingsStore = defineStore('settings', () => {
  const stationId = ref('');
  const templatePath = ref('');
  const printerName = ref('');
  const printFolder = ref('');
  const audioDeviceId = ref('');
  const serverPrint = ref(false);

  function loadSettings() {
    const saved = localStorage.getItem('ny_packing_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.stationId !== undefined) stationId.value = parsed.stationId;
        if (parsed.templatePath !== undefined) templatePath.value = parsed.templatePath;
        if (parsed.printerName !== undefined) printerName.value = parsed.printerName;
        if (parsed.printFolder !== undefined) printFolder.value = parsed.printFolder;
        if (parsed.audioDeviceId !== undefined) audioDeviceId.value = parsed.audioDeviceId;
        if (parsed.serverPrint !== undefined) serverPrint.value = parsed.serverPrint;
      } catch (e) {
        console.error('Failed to parse settings', e);
      }
    }
  }

  function saveSettings() {
    const data = {
      stationId: stationId.value,
      templatePath: templatePath.value,
      printerName: printerName.value,
      printFolder: printFolder.value,
      audioDeviceId: audioDeviceId.value,
      serverPrint: serverPrint.value
    };
    localStorage.setItem('ny_packing_settings', JSON.stringify(data));
  }

  return {
    stationId,
    templatePath,
    printerName,
    printFolder,
    audioDeviceId,
    serverPrint,
    loadSettings,
    saveSettings
  };
});
