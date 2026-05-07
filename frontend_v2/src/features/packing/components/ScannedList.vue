<template>
  <div class="scanned-sidebar glass-sidebar">
    <div class="sidebar-header">
      <h3>{{ t('packing.scanned') }} ({{ items.length }})</h3>
      <button @click="$emit('clear')" class="btn-clear" v-if="items.length > 0">{{ t('packing.clear') }}</button>
    </div>
    <div class="scanned-list-container" ref="listContainer">
      <div v-if="items.length === 0" class="empty-list-hint">{{ t('packing.no_items_scanned') }}</div>
      <ul class="scanned-list" v-else>
        <li v-for="(item, idx) in items" :key="idx" class="item-card">
          <span class="sn">{{ item }}</span>
          <span class="index">#{{ idx + 1 }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const props = defineProps({ items: { type: Array, default: () => [] } });
defineEmits(['clear']);
const listContainer = ref(null);
watch(() => props.items, () => {
  nextTick(() => { if (listContainer.value) listContainer.value.scrollTo({ top: listContainer.value.scrollHeight, behavior: 'smooth' }); });
}, { deep: true });
</script>

<style scoped>
.scanned-sidebar { 
  width: 380px; 
  background: #ffffff; 
  border-radius: 24px; 
  border: 1px solid #f1f5f9; 
  display: flex; 
  flex-direction: column; 
  height: calc(100vh - 120px); 
  position: sticky; 
  top: 20px; 
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}
.sidebar-header { 
  padding: 20px 24px; 
  border-bottom: 1px solid #f8fafc; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  background: linear-gradient(to bottom, #fcfdfe, #ffffff);
  border-radius: 24px 24px 0 0;
}
.sidebar-header h3 { 
  margin: 0; 
  font-size: 1.1rem; 
  font-weight: 800;
  color: #0f172a; 
}
.btn-clear { 
  padding: 6px 12px; 
  font-size: 0.8rem; 
  font-weight: 700;
  color: #ef4444; 
  background: #fff1f2; 
  border: none; 
  border-radius: 8px;
  cursor: pointer; 
  transition: all 0.2s;
}
.btn-clear:hover {
  background: #fee2e2;
  transform: translateY(-1px);
}
.scanned-list-container { 
  overflow-y: auto; 
  padding: 16px; 
  flex: 1; 
  scrollbar-width: thin;
  scrollbar-color: #e2e8f0 transparent;
}
.scanned-list { 
  list-style: none; 
  padding: 0; 
  margin: 0; 
}
.empty-list-hint { 
  display: flex; 
  flex-direction: column;
  justify-content: center; 
  align-items: center; 
  height: 100%; 
  color: #94a3b8; 
  font-size: 0.9rem;
}
.item-card { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 12px 16px; 
  background: #ffffff; 
  border-radius: 12px; 
  margin-bottom: 8px; 
  border: 1px solid #f1f5f9; 
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  transition: all 0.2s;
}
.item-card:hover {
  border-color: #3b82f6;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.05);
}
.sn { 
  font-weight: 700; 
  color: #1e293b; 
  font-size: 1.05rem; 
  font-family: 'JetBrains Mono', monospace;
}
.index { 
  font-size: 0.75rem; 
  font-weight: 800; 
  color: #94a3b8; 
  background: #f8fafc;
  padding: 2px 8px;
  border-radius: 6px;
}
@media (max-width: 1200px) { 
  .scanned-sidebar { 
    width: 100% !important; 
    height: 450px !important; 
    position: relative !important; 
    top: 0 !important; 
    margin-top: 20px;
  } 
}
</style>
