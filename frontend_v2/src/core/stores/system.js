import { defineStore } from 'pinia';
import { ref } from 'vue';
import printApi from '../../features/print/api';

export const useSystemStore = defineStore('system', () => {
  const isOnline = ref(false);
  const isAgentConnected = ref(true); // BarTender tích hợp trong Backend
  const isSidebarCollapsed = ref(false);
  const stationId = ref('Detecting...');
  const notification = ref(null);
  let notificationTimer = null;

  function showNotification(text, type = 'info', duration = 3000) {
    if (notificationTimer) clearTimeout(notificationTimer);
    notification.value = { text, type };
    if (duration > 0) {
      notificationTimer = setTimeout(() => {
        notification.value = null;
      }, duration);
    }
  }

  function clearNotification() {
    if (notificationTimer) clearTimeout(notificationTimer);
    notification.value = null;
  }

  async function initStationId() {
    try {
      const res = await printApi.whoami();
      if (res.data?.ip) {
        stationId.value = res.data.ip;
      }
    } catch (e) {
      console.warn('Failed to detect client IP:', e);
      stationId.value = 'Unknown IP';
    }
  }

  // Initialize on load
  initStationId();

  return {
    isOnline,
    isAgentConnected,
    isSidebarCollapsed,
    stationId,
    notification,
    showNotification,
    clearNotification,
    initStationId
  };
});
