<template>
  <div class="w-full h-[400px] md:h-[450px] relative mt-4 md:mt-5 bg-white rounded-[24px] border border-slate-100 flex flex-col shadow-[0_4px_20px_rgba(0,0,0,0.03)] lg:w-[320px] xl:w-[380px] lg:h-[calc(100vh-100px)] lg:sticky lg:top-4 lg:mt-0">
    <div class="px-6 py-5 border-b border-slate-50 flex justify-between items-center bg-linear-to-b from-slate-50 to-white rounded-t-[24px]">
      <h3 class="m-0 text-[1.1rem] font-extrabold text-slate-900">{{ t('packing.scanned') }} ({{ items.length }})</h3>
      <button @click="$emit('clear')" class="px-3 py-1.5 text-[0.8rem] font-bold text-rose-500 bg-rose-50 border-none rounded-lg cursor-pointer transition-all hover:bg-rose-100 hover:-translate-y-0.5" v-if="items.length > 0">{{ t('packing.clear') }}</button>
    </div>
    <div class="overflow-y-auto p-4 flex-1 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent" ref="listContainer">
      <div v-if="items.length === 0" class="flex flex-col justify-center items-center h-full text-slate-400 text-[0.9rem]">{{ t('packing.no_items_scanned') }}</div>
      <ul class="list-none p-0 m-0" v-else>
        <li v-for="(item, idx) in items" :key="idx" class="flex justify-between items-center px-4 py-3 bg-white rounded-xl mb-2 border border-slate-100 shadow-xs transition-all hover:border-blue-500 hover:translate-x-1 hover:shadow-[0_4px_12px_rgba(59,130,246,0.05)]">
          <span class="font-bold text-slate-800 text-[1.05rem] font-mono">{{ item }}</span>
          <span class="text-[0.75rem] font-extrabold text-slate-400 bg-slate-50 px-2 py-0.5 rounded-md">#{{ idx + 1 }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const props = defineProps<{
  items: string[]
}>();
defineEmits<{
  (e: 'clear'): void
}>();
const listContainer = ref<HTMLElement | null>(null);
watch(() => props.items, () => {
  nextTick(() => { if (listContainer.value) listContainer.value.scrollTo({ top: listContainer.value.scrollHeight, behavior: 'smooth' }); });
}, { deep: true });
</script>
