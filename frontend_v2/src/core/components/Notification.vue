<template>
  <Transition name="slide-up">
    <div v-if="system.notification" class="notification" :class="system.notification.type">
      <i class="fas" :class="system.notification.type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'"></i>
      {{ system.notification.text }}
    </div>
  </Transition>
</template>

<script setup>
import { useSystemStore } from '../stores/system';
const system = useSystemStore();
</script>

<style scoped>
.notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 16px 24px;
  border-radius: 12px;
  background: #1e293b;
  color: white;
  z-index: 3000;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}
.notification.success { background: #10b981; }
.notification.error { background: #ef4444; }
.notification.warning { background: #f59e0b; }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from { transform: translateY(20px); opacity: 0; }
.slide-up-leave-to { transform: translateY(20px); opacity: 0; }
</style>
