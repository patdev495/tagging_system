<template>
  <div class="h-screen flex items-center justify-center bg-linear-to-br from-slate-950 to-indigo-950 text-white">
    <div class="w-full max-w-[400px] p-10 bg-white/5 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-2xl animate-in">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-linear-to-tr from-blue-500 to-violet-500 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl shadow-[0_0_20px_rgba(59,130,246,0.5)]">
          <i class="fas fa-user-shield"></i>
        </div>
        <h2 class="m-0 text-[1.5rem] font-bold tracking-tight">{{ t('admin.login_title') }}</h2>
        <p class="text-slate-400 text-[0.9rem] mt-2">{{ t('admin.login_subtitle') }}</p>
      </div>

      <form @submit.prevent="handleLogin" class="flex flex-col gap-6">
        <div class="flex flex-col gap-2">
          <label for="password" class="text-[0.75rem] font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.password') }}</label>
          <div class="relative flex items-center">
            <i class="fas fa-lock absolute left-4 text-slate-500"></i>
            <input 
              id="password"
              v-model="password" 
              type="password" 
              placeholder="••••••••" 
              required
              ref="passInput"
              class="w-full pl-12 pr-4 py-3 bg-slate-900/60 border border-white/10 rounded-xl text-white text-[1rem] outline-none transition-all focus:border-blue-500 focus:bg-slate-900/80 focus:ring-4 focus:ring-blue-500/10"
            />
          </div>
          <p v-if="error" class="text-rose-500 text-[0.8rem] font-medium mt-1">{{ error }}</p>
        </div>

        <button type="submit" :disabled="loading" class="p-3.5 bg-blue-500 text-white border-none rounded-xl font-bold text-[1rem] cursor-pointer transition-all flex items-center justify-center hover:bg-blue-600 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-10px_rgba(37,99,235,0.5)] active:translate-y-0 disabled:opacity-70 disabled:cursor-not-allowed">
          <span v-if="!loading">{{ t('admin.unlock') }}</span>
          <i v-else class="fas fa-spinner fa-spin"></i>
        </button>
        
        <router-link to="/" class="text-center text-slate-400 no-underline text-[0.85rem] font-medium flex items-center justify-center gap-2 mt-2 transition-colors hover:text-white">
          <i class="fas fa-arrow-left"></i> {{ t('admin.return_packing') }}
        </router-link>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const password = ref<string>('');
const error = ref<string>('');
const loading = ref<boolean>(false);
const passInput = ref<HTMLInputElement | null>(null);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  // Simulated delay for premium feel
  await new Promise(resolve => setTimeout(resolve, 500));
  
  if (password.value === 'admin123') {
    sessionStorage.setItem('admin_session', 'true');
    const redirectPath = (route.query.redirect as string) || '/admin';
    router.push(redirectPath);
  } else {
    error.value = t('admin.incorrect_password');
    password.value = '';
  }
  loading.value = false;
};

onMounted(() => {
  if (passInput.value) passInput.value.focus();
});
</script>
