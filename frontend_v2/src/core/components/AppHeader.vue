<template>
  <header class="header">
    <h1><i class="fas fa-box-open"></i> NY Packing Station</h1>
    <div class="header-actions">
      <div class="status-badge agent" :class="{ connected: system.isAgentConnected }" @click="$emit('check-agent')" title="Click to refresh Agent status">
        <i class="fas fa-print"></i> {{ system.isAgentConnected ? 'Agent Online' : 'Agent Offline' }}
      </div>
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
    </div>
  </header>

  <!-- Agent Offline Critical Alert Banner -->
  <div v-if="!system.isAgentConnected" class="agent-offline-alert-banner fade-in">
    <div class="alert-content">
      <i class="fas fa-exclamation-triangle pulse-icon"></i>
      <span><strong>PRINT AGENT OFFLINE:</strong> Local printing is disabled. Please start <code>print_agent.exe</code> on this computer.</span>
    </div>
    <button @click="$emit('check-agent')" class="btn-retry-agent">
      <i class="fas fa-sync-alt"></i> Re-check
    </button>
  </div>
</template>

<script setup>
import { useSystemStore } from '../stores/system';

defineProps({
  isAudioActive: { type: Boolean, default: false }
});

defineEmits(['check-agent', 'toggle-audio', 'show-emergency', 'show-settings']);

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
.status-badge.agent {
  background: #f1f5f9;
  color: #64748b;
  margin-right: 8px;
  cursor: pointer;
}
.status-badge.agent.connected {
  background: #e0f2fe;
  color: #0369a1;
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
.agent-offline-alert-banner {
  background: #ef4444;
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  animation: slideDown 0.3s ease-out;
}
.alert-content {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 1rem;
}
.pulse-icon {
  font-size: 1.5rem;
  animation: pulse 1.5s infinite;
}
.btn-retry-agent {
  background: white;
  color: #ef4444;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.btn-retry-agent:hover {
  background: #fee2e2;
  transform: scale(1.05);
}
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}
@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
