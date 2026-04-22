import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSystemStore = defineStore('system', () => {
  const isOnline = ref(false);
  const isAgentConnected = ref(false);
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

  return {
    isOnline,
    isAgentConnected,
    notification,
    showNotification,
    clearNotification
  };
});
