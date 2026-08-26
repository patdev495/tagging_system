<template>
  <div class="rounded-xl border-2 border-indigo-300/70 bg-gradient-to-br from-indigo-950 to-slate-900 shadow-lg shadow-indigo-950/40 flex items-center justify-between px-4 py-2.5 gap-3 relative overflow-hidden shrink-0">
    <!-- Subtle glow -->
    <div class="absolute -right-8 -top-8 w-32 h-32 rounded-full bg-indigo-500/20 blur-2xl pointer-events-none"></div>

    <!-- Label + SN Preview -->
    <div class="flex flex-col min-w-0 z-10">
      <div class="flex items-center gap-2 mb-0.5">
        <div class="w-5 h-5 rounded bg-indigo-500/30 border border-indigo-400/40 flex items-center justify-center text-indigo-300 text-[10px] font-black shrink-0">#</div>
        <span class="text-[10px] font-extrabold uppercase tracking-widest text-indigo-300">Sê-ri Thùng Tiếp Theo</span>
        <span :class="['px-1.5 py-px rounded text-[9px] font-black uppercase shrink-0', isAutoSN ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30']">
          {{ isAutoSN ? 'Tự Động' : 'Thủ Công' }}
        </span>
        <span v-if="snCheckError" class="text-amber-400 text-[10px] font-bold flex items-center gap-0.5" :title="snCheckError">
          <i class="fas fa-exclamation-triangle text-[9px]"></i> Trùng SN
        </span>
      </div>
      <!-- Big SN Text -->
      <span class="font-mono font-black text-xl md:text-2xl text-white tracking-tight leading-none select-all truncate" :title="currentSNPreview">
        {{ currentSNPreview }}
      </span>
    </div>

    <!-- Controls: Manual input + toggle -->
    <div class="flex items-center gap-2 shrink-0 z-10">
      <input
        v-if="!isAutoSN"
        :value="manualSequence"
        @input="onInput"
        type="number"
        min="1"
        placeholder="85"
        class="w-20 px-2.5 py-1.5 rounded-lg border border-indigo-400/50 bg-slate-800 font-mono font-black text-sm text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none text-center"
      />
      <button
        @click="$emit('toggle-mode')"
        type="button"
        :class="[
          'px-3 py-1.5 rounded-lg font-bold text-xs flex items-center gap-1.5 transition-all cursor-pointer shadow-sm',
          isAutoSN 
            ? 'bg-slate-700 hover:bg-slate-600 text-slate-200 border border-slate-600' 
            : 'bg-indigo-500/30 hover:bg-indigo-500/50 text-indigo-200 border border-indigo-400/50'
        ]"
      >
        <i :class="isAutoSN ? 'fas fa-pen text-[10px]' : 'fas fa-rotate-right text-[10px]'"></i>
        <span>{{ isAutoSN ? 'Sửa Thủ Công' : 'Về Auto' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentSNPreview: string;
  isAutoSN: boolean;
  manualSequence: number | null;
  snCheckError?: string;
}>();

const emit = defineEmits<{
  (e: 'toggle-mode'): void;
  (e: 'update:manual-sequence', val: number | null): void;
  (e: 'check-manual-sn'): void;
}>();

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const val = target.value ? Number(target.value) : null;
  emit('update:manual-sequence', val);
  emit('check-manual-sn');
};
</script>
