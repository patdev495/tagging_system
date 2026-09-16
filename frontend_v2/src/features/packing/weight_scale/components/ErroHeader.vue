<template>
  <header class="flex items-center justify-between pb-2 border-b border-slate-200 shrink-0">
    <div class="flex items-center gap-2.5">
      <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 shadow-inner shrink-0">
        <i class="fas fa-weight-scale text-lg"></i>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-black text-base md:text-lg text-slate-900 leading-tight">Trạm Cân Đóng Gói (Erro)</h1>
          <span class="px-2 py-0.5 text-[10px] font-black rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200 tracking-wide uppercase">
            Khách Hàng Erro
          </span>
        </div>
        <p class="text-[11px] text-slate-500 leading-none">Kiểm soát trọng lượng dung sai và in nhãn BarTender Erro</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <!-- Agent Status -->
      <div 
        :class="['px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 text-xs font-bold transition-all shrink-0 cursor-help', isAgentOnline ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs' : 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse']"
        :title="isAgentOnline ? `Print Agent đang chạy (${agentUrl})` : 'Chưa bật phần mềm NY Print Agent trên máy tính'"
      >
        <span class="relative flex h-2 w-2">
          <span v-if="isAgentOnline" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span :class="['relative inline-flex rounded-full h-2 w-2', isAgentOnline ? 'bg-emerald-500' : 'bg-rose-500']"></span>
        </span>
        <i class="fas fa-print text-xs"></i>
        <span>{{ isAgentOnline ? 'Agent Online' : 'Agent Offline' }}</span>
      </div>

      <!-- Scale Status -->
      <div 
        :class="['px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 text-xs font-bold transition-all shrink-0', (isAgentOnline && scaleStatus.connected) ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs' : 'bg-rose-50 text-rose-700 border-rose-200']"
        :title="(isAgentOnline && scaleStatus.connected) ? `Cân đang kết nối cổng ${scaleStatus.port}` : 'Cân chưa kết nối hoặc mất tín hiệu COM'"
      >
        <span class="relative flex h-2 w-2">
          <span v-if="isAgentOnline && scaleStatus.connected" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span :class="['relative inline-flex rounded-full h-2 w-2', (isAgentOnline && scaleStatus.connected) ? 'bg-emerald-500' : 'bg-rose-500']"></span>
        </span>
        <i class="fas fa-weight-scale text-xs"></i>
        <span>{{ (isAgentOnline && scaleStatus.connected) ? `Cân Online (${scaleStatus.port || 'COM'})` : 'Cân Mất Kết Nối' }}</span>
      </div>

      <!-- Actions -->
      <button @click="$emit('showSettings')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer">
        <i class="fas fa-cog text-slate-500"></i><span>Cài Đặt</span>
      </button>
      <button @click="$emit('switchCustomer')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs">
        <i class="fas fa-exchange-alt"></i><span>Đổi Khách</span>
      </button>
      <router-link to="/admin" class="px-2.5 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs" title="Trang quản trị hệ thống (Admin)">
        <i class="fas fa-user-shield text-indigo-600"></i><span>Admin</span>
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  isAgentOnline: boolean;
  agentUrl: string;
  scaleStatus: {
    connected: boolean;
    port?: string;
  };
}>();

defineEmits<{
  (e: 'showSettings'): void;
  (e: 'switchCustomer'): void;
}>();
</script>
