<template>
  <div class="login-container">
    <div class="glass-card login-card fade-in">
      <div class="login-header">
        <div class="logo-circle">
          <i class="fas fa-user-shield"></i>
        </div>
        <h2>{{ t('admin.login_title') }}</h2>
        <p>{{ t('admin.login_subtitle') }}</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="password">{{ t('admin.password') }}</label>
          <div class="input-wrapper">
            <i class="fas fa-lock"></i>
            <input 
              id="password"
              v-model="password" 
              type="password" 
              placeholder="••••••••" 
              required
              ref="passInput"
              class="password-input"
            />
          </div>
          <p v-if="error" class="error-msg">{{ error }}</p>
        </div>

        <button type="submit" :disabled="loading" class="btn-login">
          <span v-if="!loading">{{ t('admin.unlock') }}</span>
          <i v-else class="fas fa-spinner fa-spin"></i>
        </button>
        
        <router-link to="/" class="btn-back">
          <i class="fas fa-arrow-left"></i> {{ t('admin.return_packing') }}
        </router-link>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const password = ref('');
const error = ref('');
const loading = ref(false);
const passInput = ref(null);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  // Simulated delay for premium feel
  await new Promise(resolve => setTimeout(resolve, 500));
  
  if (password.value === 'admin123') {
    sessionStorage.setItem('admin_session', 'true');
    const redirectPath = route.query.redirect || '/admin';
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

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  color: white;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-circle {
  width: 64px;
  height: 64px;
  background: linear-gradient(45deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 24px;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.login-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.login-header p {
  color: #94a3b8;
  font-size: 0.9rem;
  margin-top: 8px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 16px;
  color: #64748b;
}

.password-input {
  width: 100%;
  padding: 12px 16px 12px 48px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s;
}

.password-input:focus {
  border-color: #3b82f6;
  background: rgba(15, 23, 42, 0.8);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.btn-login {
  padding: 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-login:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 10px 20px -10px rgba(37, 99, 235, 0.5);
}

.btn-login:active {
  transform: translateY(0);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-back {
  text-align: center;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  transition: color 0.2s;
}

.btn-back:hover {
  color: white;
}

.error-msg {
  color: #ef4444;
  font-size: 0.8rem;
  font-weight: 500;
  margin-top: 4px;
}

.fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
