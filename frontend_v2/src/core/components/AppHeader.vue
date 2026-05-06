<template>
  <header class="header">
    <div @click="$emit('home')" class="title-link cursor-pointer">
      <h1><i class="fas fa-box-open"></i> {{ t('header.title') }}</h1>
    </div>
    <div class="header-actions">
      <div class="status-badge" :class="{ online: system.isOnline }">
        {{ system.isOnline ? t('header.status_online') : t('header.connecting') }}
      </div>
      <button @click="$emit('toggle-audio')" class="btn-icon status-audio" :class="{ active: isAudioActive }" :title="isAudioActive ? t('header.audio_active') : t('header.audio_inactive')">
        <i class="fas" :class="isAudioActive ? 'fa-volume-up' : 'fa-volume-mute'"></i>
      </button>
      <button @click="$emit('show-emergency')" class="btn-icon warning" :title="t('header.emergency_reprint')">
        <i class="fas fa-exclamation-triangle"></i>
      </button>
      <div class="lang-switcher">
        <button 
          @click="toggleLanguage" 
          class="btn-lang" 
          :class="{ active: settings.language === 'en' }"
          :title="settings.language === 'vi' ? 'Switch to English' : 'Chuyển sang Tiếng Việt'"
        >
          <span class="lang-text">{{ settings.language === 'vi' ? 'VI' : 'EN' }}</span>
          <i class="fas fa-language"></i>
        </button>
      </div>
      <button @click="$emit('show-settings')" class="btn-icon" :title="t('header.settings')">
        <i class="fas fa-cog"></i>
      </button>
      <router-link to="/admin" class="btn-icon admin-btn" :title="t('header.admin_dashboard')">
        <i class="fas fa-user-shield"></i>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { useSystemStore } from '../stores/system';
import { useSettingsStore } from '../stores/settings';

defineProps({
  isAudioActive: { type: Boolean, default: false }
});

defineEmits(['toggle-audio', 'show-emergency', 'show-settings', 'home']);

const { t } = useI18n();
const system = useSystemStore();
const settings = useSettingsStore();

const toggleLanguage = () => {
  settings.language = settings.language === 'vi' ? 'en' : 'vi';
  settings.saveSettings();
};
</script>

<style scoped>
.header {
  background: white;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.title-link {
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s;
  cursor: pointer;
}

.title-link:hover {
  opacity: 0.8;
}

h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 10px;
}

h1 i { color: #2563eb; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-badge::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e1;
}

.status-badge.online {
  background: #dcfce7;
  color: #166534;
}

.status-badge.online::before {
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.btn-icon {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #64748b;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
  transform: translateY(-2px);
}

.btn-icon.warning:hover {
  background: #fff1f2;
  border-color: #fecaca;
  color: #e11d48;
}

.status-audio.active {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #2563eb;
}

.admin-btn {
  background: #f8fafc;
  color: #4f46e5;
  border-color: #c7d2fe;
}

.admin-btn:hover {
  background: #eef2ff;
  color: #3730a3;
}

.lang-switcher {
  border-left: 1px solid #e2e8f0;
  padding-left: 12px;
  margin-left: 4px;
}

.btn-lang {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  font-size: 0.7rem;
  transition: all 0.2s;
}

.btn-lang:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}

.btn-lang.active {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}

.lang-text {
  font-family: 'Inter', sans-serif;
}
</style>
