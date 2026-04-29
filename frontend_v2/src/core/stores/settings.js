import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSettingsStore = defineStore('settings', () => {
  const stationId = ref('');
  const printerName = ref('');
  const audioDeviceId = ref('');

  function loadSettings() {
    const saved = localStorage.getItem('ny_packing_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.stationId !== undefined) stationId.value = parsed.stationId;
        if (parsed.printerName !== undefined) printerName.value = parsed.printerName;
        if (parsed.audioDeviceId !== undefined) audioDeviceId.value = parsed.audioDeviceId;
      } catch (e) {
        console.error('Failed to parse settings', e);
      }
    }
  }

  function saveSettings() {
    const data = {
      stationId: stationId.value,
      printerName: printerName.value,
      audioDeviceId: audioDeviceId.value,
    };
    localStorage.setItem('ny_packing_settings', JSON.stringify(data));
  }

  return {
    stationId,
    printerName,
    audioDeviceId,
    loadSettings,
    saveSettings
  };
});
