<template>
  <aside 
    :class="[
      'fixed left-0 top-0 h-screen transition-all duration-300 z-50 flex flex-col shadow-[4px_0_20px_rgba(0,0,0,0.1)] bg-linear-to-b from-[#1e1b4b] to-[#0f172a] text-white',
      isCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <!-- Header/Logo -->
    <router-link to="/" class="p-6 flex items-center gap-3 border-b border-indigo-800 hover:bg-white/5 transition-colors cursor-pointer no-underline text-white">
      <div class="bg-white p-2 rounded-lg flex-shrink-0 shadow-sm">
        <Package class="text-indigo-900 w-6 h-6" />
      </div>
      <div v-if="!isCollapsed" class="overflow-hidden whitespace-nowrap">
        <h1 class="font-black tracking-tight text-xl">NY TAGGING</h1>
      </div>
    </router-link>

    <!-- Navigation -->
    <nav class="flex-1 py-6 px-3 space-y-2 overflow-y-auto">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path" 
        :to="item.path"
        class="flex items-center gap-3 p-3 rounded-lg transition-all hover:bg-white/10 group text-white"
        active-class="bg-indigo-600 shadow-[0_4px_12px_rgba(79,70,229,0.3)]"
        exact-active-class="bg-indigo-600 shadow-[0_4px_12px_rgba(79,70,229,0.3)]"
        :title="isCollapsed ? item.label : ''"
      >
        <component :is="item.icon" class="w-6 h-6 flex-shrink-0" />
        <span v-if="!isCollapsed" class="font-medium whitespace-nowrap">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Footer / Toggle -->
    <div class="p-4 border-t border-indigo-800">
      <button 
        @click="isCollapsed = !isCollapsed"
        class="w-full flex items-center justify-center p-2 rounded-lg hover:bg-indigo-800 transition-colors cursor-pointer"
      >
        <ChevronLeft v-if="!isCollapsed" class="w-6 h-6" />
        <ChevronRight v-else class="w-6 h-6" />
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { 
  Package, 
  LayoutDashboard, 
  Users, 
  Box, 
  Settings, 
  BarChart3,
  ChevronLeft,
  ChevronRight,
  ClipboardList
} from 'lucide-vue-next';
import { useSystemStore } from '../stores/system';
import { storeToRefs } from 'pinia';
import type { Component } from 'vue';

const systemStore = useSystemStore();
const { isSidebarCollapsed: isCollapsed } = storeToRefs(systemStore);

interface MenuItem {
  label: string;
  path: string;
  icon: Component;
}

const menuItems: MenuItem[] = [
  { label: 'Packing Station', path: '/', icon: Box },
  { label: 'Dashboard', path: '/admin', icon: LayoutDashboard },
  { label: 'Customers', path: '/admin/customers', icon: Users },
  { label: 'Products', path: '/admin/products', icon: Package },
  { label: 'Carton History', path: '/admin/history', icon: ClipboardList },
  { label: 'S/N Lookup', path: '/admin/stats', icon: BarChart3 },
  { label: 'Settings', path: '/admin/settings', icon: Settings },
];
</script>
