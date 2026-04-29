<template>
  <header class="header">
    <h1><i class="fas fa-box-open"></i> NY Packing Station</h1>
    <div class="header-actions">
      <div class="status-badge" :class="{ online: system.isOnline }">
        {{ system.isOnline ? 'System Online' : 'Connecting...' }}
      </div>
      <button @click="$emit('toggle-audio')" class="btn-icon status-audio" :class="{ active: isAudioActive }" :title="isAudioActive ? 'Audio Alert: Active (Click to Test)' : 'Audio Alert: Click to Activate/Test'">
        <i class="fas" :class="isAudioActive ? 'fa-volume-up' : 'fa-volume-mute'"></i>
      </button>
      <button @click="$emit('show-emergency')" class="btn-icon warning" title="Emergency Reprint">
        <i class="fas fa-exclamation-triangle"></i>
      </button>
      <button @click="$emit('show-settings')" class="btn-icon" title="Settings">
        <i class="fas fa-cog"></i>
      </button>
      <router-link to="/admin" class="btn-icon admin-btn" title="Admin Dashboard">
        <i class="fas fa-user-shield"></i>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { useSystemStore } from '../stores/system';

defineProps({
  isAudioActive: { type: Boolean, default: false }
});

defineEmits(['toggle-audio', 'show-emergency', 'show-settings']);

const system = useSystemStore();
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 8px;
}
.header h1 {
  color: #0f172a;
  font-weight: 700;
  margin: 0;
  font-size: 1.35rem;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
.status-badge {
  padding: 6px 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}
.status-badge.online {
  background: #dcfce7;
  color: #166534;
}
.btn-icon {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #2563eb;
  border-color: #3b82f6;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  transform: scale(1.05);
}
.btn-icon i { font-size: 1.2rem; }
.btn-icon.status-audio {
  color: #94a3b8;
  border-color: #e2e8f0;
  background: white;
  transform: none;
}
.btn-icon.status-audio.active {
  color: #2563eb;
  border-color: #3b82f6;
  background: #eff6ff;
  transform: scale(1.05);
}
.btn-icon.status-audio:hover {
  background: #f1f5f9;
  transform: scale(1.1);
}
.btn-icon.warning:hover {
  background: #fdf4ff;
  transform: scale(1.1) rotate(5deg);
}
.btn-icon.admin-btn {
  background: #1e293b;
  color: white;
  border-color: #0f172a;
}
.btn-icon.admin-btn:hover {
  background: #334155;
  transform: scale(1.1);
}
</style>
