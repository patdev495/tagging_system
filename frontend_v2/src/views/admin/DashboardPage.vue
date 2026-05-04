<template>
  <div class="admin-dashboard p-8">
    <div class="header mb-8">
      <h1 class="text-3xl font-bold text-slate-900">Admin Dashboard</h1>
      <p class="text-slate-500">Welcome to the data management system.</p>
    </div>

    <div class="grid md:grid-cols-3 gap-6">
      <div v-for="stat in stats" :key="stat.label" class="stat-card bg-white p-6 rounded-xl shadow-md border border-slate-200">
        <div class="flex items-center gap-4">
          <div :class="`icon-box p-3 rounded-lg bg-${stat.color}-50 text-${stat.color}-500`">
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
      <p class="text-slate-400 italic">Statistical charts will be updated in future phases.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Package, Users, BarChart3 } from 'lucide-vue-next';

const stats = ref([
  { label: 'Total Customers', value: '12', icon: Users, color: 'indigo' },
  { label: 'Active Products', value: '148', icon: Package, color: 'indigo' },
  { label: 'Cartons Today', value: '45', icon: BarChart3, color: 'indigo' },
]);
</script>

<style scoped>
.admin-dashboard {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
