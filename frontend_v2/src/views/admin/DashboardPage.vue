<template>
  <div class="p-8 animate-in">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900">{{ t('header.admin_dashboard') }}</h1>
      <p class="text-slate-500">{{ t('admin.welcome') }}</p>
    </div>

    <div class="grid md:grid-cols-3 gap-6">
      <div v-for="stat in stats" :key="stat.label" class="bg-white p-6 rounded-xl shadow-md border border-slate-200">
        <div class="flex items-center gap-4">
          <div :class="['p-3 rounded-lg', stat.color === 'indigo' ? 'bg-indigo-50 text-indigo-500' : '']">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
          <div>
            <p class="text-sm font-medium text-slate-500">{{ stat.label }}</p>
            <p class="text-2xl font-bold text-slate-900">{{ stat.value }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-12 bg-white p-8 rounded-xl shadow-md border border-slate-200 text-center">
      <p class="text-slate-400 italic">{{ t('admin.charts_future') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Package, Users, BarChart3 } from 'lucide-vue-next';
import type { Component } from 'vue';

const { t } = useI18n();

interface Stat {
  label: string;
  value: string;
  icon: Component;
  color: string;
}

const stats = ref<Stat[]>([
  { label: t('admin.total_customers'), value: '12', icon: Users, color: 'indigo' },
  { label: t('admin.active_products'), value: '148', icon: Package, color: 'indigo' },
  { label: t('admin.cartons_today'), value: '45', icon: BarChart3, color: 'indigo' },
]);
</script>
