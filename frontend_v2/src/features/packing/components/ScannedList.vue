<template>
  <div class="scanned-sidebar glass-sidebar">
    <div class="sidebar-header">
      <h3>Scanned ({{ items.length }})</h3>
      <button @click="$emit('clear')" class="btn-clear" v-if="items.length > 0">Clear</button>
    </div>
    <div class="scanned-list-container" ref="listContainer">
      <div v-if="items.length === 0" class="empty-list-hint">No items scanned</div>
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
const props = defineProps({ items: { type: Array, default: () => [] } });
defineEmits(['clear']);
const listContainer = ref(null);
watch(() => props.items, () => {
  nextTick(() => { if (listContainer.value) listContainer.value.scrollTo({ top: listContainer.value.scrollHeight, behavior: 'smooth' }); });
}, { deep: true });
</script>

<style scoped>
.scanned-sidebar { width: 320px; background: #f1f5f9; border-radius: 16px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; height: calc(100vh - 120px); position: sticky; top: 10px; }
.sidebar-header { padding: 16px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.sidebar-header h3 { margin: 0; font-size: 1rem; color: #1e293b; }
.btn-clear { padding: 4px 8px; font-size: 0.75rem; color: #ef4444; background: transparent; border: none; cursor: pointer; }
.scanned-list-container { overflow-y: auto; padding: 10px; flex: 1; }
.scanned-list { list-style: none; padding: 0; margin: 0; }
.empty-list-hint { display: flex; justify-content: center; align-items: center; height: 100%; color: #94a3b8; font-style: italic; }
.item-card { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: white; border-radius: 8px; margin-bottom: 6px; border: 1px solid #f1f5f9; }
.sn { font-weight: 600; color: #0f172a; font-size: 0.95rem; }
.index { font-size: 0.8rem; font-weight: 700; color: #cbd5e1; }
@media (max-width: 1100px) { .scanned-sidebar { width: 100% !important; height: 400px !important; position: relative !important; top: 0 !important; } }
</style>
