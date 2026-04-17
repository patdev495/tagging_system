<template>
  <div class="packing-container">
    <div class="glass-card main-card" :class="{ 'wide-layout': currentProduct }">
      <header class="header">
        <h1><i class="fas fa-box-open"></i> NY Packing Station</h1>
        <div class="header-actions">
          <div class="status-badge" :class="{ online: isOnline }">
            {{ isOnline ? 'System Online' : 'Connecting...' }}
          </div>
          <button @click="showSettings = true" class="btn-icon" title="Settings">
            <i class="fas fa-cog"></i>
          </button>
        </div>
      </header>

      <section class="selection-panel" v-if="!currentProduct">
        <div class="control-group">
          <label>Select Customer</label>
          <select v-model="selectedCustomerId" @change="loadProducts" class="modern-select">
            <option value="" disabled>Choose a customer...</option>
            <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
          </select>
        </div>

        <div class="control-group" v-if="selectedCustomerId">
          <label>Select Product</label>
          <div class="product-grid">
            <div 
              v-for="p in products" 
              :key="p.id" 
              class="product-card"
              @click="selectProduct(p)"
            >
              <h3>{{ p.item_name }}</h3>
              <p>UPC: {{ p.upc }}</p>
              <div class="qty-tag">Target: {{ p.packed_qty }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="scanning-panel" v-else>
        <div class="packing-workspace">
          <!-- Main Area: Controls & Info -->
          <div class="main-workspace">
            <div class="session-info">
              <button @click="resetSession" class="btn-text">&larr; Change Product</button>
              <div class="active-product">
                <h2>{{ currentProduct.item_name }}</h2>
                <div class="meta">
                  <span>UPC: {{ currentProduct.upc }}</span>
                  <span>Target: {{ currentProduct.packed_qty }}</span>
                </div>
              </div>
              <div class="job-order-input">
                <label>Job Order</label>
                <input 
                  v-model="jobOrder" 
                  placeholder="Enter job order number..." 
                  class="modern-input-small"
                  ref="jobOrderInput"
                  @keyup.enter="scanInput.focus()"
                />
              </div>
            </div>

            <div class="progress-container">
              <div class="progress-header">
                <span class="count">{{ scannedItems.length }} / {{ currentProduct.packed_qty }}</span>
                <span class="percent">{{ progressPercent }}%</span>
              </div>
              <div class="progress-bar">
                <div class="fill" :style="{ width: progressPercent + '%' }"></div>
              </div>
            </div>

            <div class="result-actions fade-in" v-if="lastCarton">
              <div class="success-banner">
                <i class="fas fa-check-circle"></i>
                <span>Last Carton: <strong>{{ lastCarton.carton_sn }}</strong></span>
                <div class="banner-actions">
                  <a :href="`http://${host}:8000/cartons/${lastCarton.id}/btxml`" class="btn-reprint" download>
                    <i class="fas fa-file-download"></i> Manual Download
                  </a>
                  <button @click="triggerDownload(null, null, lastCarton.id)" class="btn-reprint secondary" v-if="lastCarton.btxml">
                    <i class="fas fa-print"></i> Retry Print
                  </button>
                </div>
              </div>
            </div>

            <div class="input-area">
              <input 
                type="text" 
                v-model="scanBuffer" 
                @keyup.enter="handleScan"
                :placeholder="!jobOrder ? '⚠️ PLEASE ENTER JOB ORDER FIRST...' : 'Scan Item S/N...'"
                ref="scanInput"
                class="scan-input"
                :class="{ 'input-locked': !jobOrder }"
                :disabled="isProcessing"
              />
              <p class="hint" v-if="jobOrder">Waiting for scanner input (Enter to submit)</p>
              <p class="hint warning" v-else>Please fill in the Job Order field at the top first</p>
            </div>
          </div>

          <!-- Sidebar: Scanned Items -->
          <div class="scanned-sidebar glass-sidebar">
            <div class="sidebar-header">
              <h3>Scanned ({{ scannedItems.length }})</h3>
              <button @click="scannedItems = []" class="btn-clear" v-if="scannedItems.length > 0">Clear</button>
            </div>
            <div class="scanned-list-container">
              <div v-if="scannedItems.length === 0" class="empty-list-hint">
                No items scanned
              </div>
              <ul class="scanned-list" v-else>
                <li v-for="(item, idx) in sortedScannedItems" :key="idx" class="fade-in item-card">
                  <div class="item-info">
                    <span class="sn">{{ item }}</span>
                  </div>
                  <div class="index">#{{ scannedItems.length - idx }}</div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Notification Overlay -->
    <Transition name="slide-up">
      <div v-if="notification" class="notification" :class="notification.type">
        {{ notification.text }}
      </div>
    </Transition>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="glass-card modal-content">
        <h2><i class="fas fa-print"></i> Printer Settings</h2>
        <p class="subtitle">Configure local printer and template paths for this station.</p>
        
        <div class="form-group">
          <label>Station ID</label>
          <input v-model="settings.stationId" placeholder="e.g., PACK-01" class="modern-input" />
        </div>

        <div class="form-group">
          <label>Template Path (.btw)</label>
          <div class="input-with-hint">
            <input v-model="settings.templatePath" placeholder="D:\Labels\carton_ui.btw" class="modern-input" />
            <small>Hint: Shift + Right Click on file -> "Copy as path" then paste here.</small>
          </div>
        </div>

        <div class="form-group">
          <label>Print Job Folder (Watch Folder)</label>
          <div class="input-with-hint">
            <input v-model="settings.printFolder" placeholder="D:\print_jobs" class="modern-input" />
            <small>Hint: The folder where Bartender is watching for files.</small>
          </div>
        </div>

        <div class="form-group">
          <label>Printer Name (Windows)</label>
          <div class="input-with-hint">
            <input v-model="settings.printerName" placeholder="Leave blank for BarTender Default" class="modern-input" />
            <small>Hint: If blank, BarTender will use the printer saved in the .btw file.</small>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="saveSettings" class="btn-primary">Save Settings</button>
          <button @click="showSettings = false" class="btn-text">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import api from '../api';

const customers = ref([]);
const products = ref([]);
const selectedCustomerId = ref('');
const currentProduct = ref(null);
const scannedItems = ref([]);
const scanBuffer = ref('');
const isOnline = ref(false);
const isProcessing = ref(false);
const host = window.location.hostname;
const notification = ref(null);
const scanInput = ref(null);
const jobOrderInput = ref(null); // Ref for Job Order input
const showSettings = ref(false);
const lastCarton = ref(null);
const jobOrder = ref(''); // New Job Order state

const settings = ref({
  stationId: '',
  templatePath: '',
  printerName: '',
  printFolder: ''
});

const loadSettings = () => {
  const saved = localStorage.getItem('ny_packing_settings');
  if (saved) {
    const parsed = JSON.parse(saved);
    // Merge with defaults to ensure new fields like printFolder exist
    settings.value = { ...settings.value, ...parsed };
  }
};

const saveSettings = () => {
  localStorage.setItem('ny_packing_settings', JSON.stringify(settings.value));
  showSettings.value = false;
  showNotification('Settings saved locally', 'success');
};

const progressPercent = computed(() => {
  if (!currentProduct.value) return 0;
  return Math.round((scannedItems.value.length / currentProduct.value.packed_qty) * 100);
});

const sortedScannedItems = computed(() => {
  return [...scannedItems.value].reverse();
});

const loadCustomers = async () => {
  try {
    const res = await api.getCustomers();
    customers.value = res.data;
    isOnline.value = true;
  } catch (err) {
    showNotification('Cannot connect to API', 'error');
  }
};

const loadProducts = async () => {
  if (!selectedCustomerId.value) return;
  try {
    const res = await api.getCustomerProducts(selectedCustomerId.value);
    products.value = res.data;
  } catch (err) {
    showNotification('Error loading products', 'error');
  }
};

const selectProduct = async (p) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = p;
  scannedItems.value = [];
  lastCarton.value = null; // Clear previous state
  
  // Fetch the last carton for this product immediately
  try {
    const res = await api.getLastCarton(p.id);
    if (res.data) {
      lastCarton.value = res.data;
    }
  } catch (err) {
    console.warn('Error fetching last carton:', err);
  }

  nextTick(() => {
    // Focus logic: Job Order first if empty
    if (!jobOrder.value && jobOrderInput.value) {
      jobOrderInput.value.focus({ preventScroll: true });
    } else if (scanInput.value) {
      scanInput.value.focus({ preventScroll: true });
    }
  });
};

const handleScan = () => {
  if (!jobOrder.value) {
    showNotification('Please enter Job Order before starting!', 'error');
    if (jobOrderInput.value) jobOrderInput.value.focus();
    return;
  }
  
  const sn = scanBuffer.value.trim();
  if (!sn) return;

  if (scannedItems.value.includes(sn)) {
    showNotification(`Duplicate S/N: ${sn}`, 'warning');
    scanBuffer.value = '';
    return;
  }

  scannedItems.value.push(sn);
  scanBuffer.value = '';

  if (scannedItems.value.length >= currentProduct.value.packed_qty) {
    finalizeCarton();
  }
};

const finalizeCarton = async () => {
  isProcessing.value = true;
  lastCarton.value = null;
  
  console.log('Finalizing carton with settings:', settings.value);

  try {
    const res = await api.createCarton({
      product_id: currentProduct.value.id,
      items: scannedItems.value,
      template_path: settings.value.templatePath || null,
      printer_name: settings.value.printerName || null,
      print_folder: settings.value.printFolder || null,
      job_order: jobOrder.value // Pass job order to API
    });
    
    console.log('API Response:', res.data);
    lastCarton.value = res.data;
    
    showNotification(`Carton ${res.data.carton_sn} created!`, 'success');

    // Phase 3: Auto-download logic
    if (res.data.btxml) {
      if (settings.value.printFolder) {
        // Mode A: Direct Write (Backend already did the work)
        console.log('File written directly to folder by backend:', settings.value.printFolder);
        showNotification(`Label file saved to ${settings.value.printFolder}`, 'success');
      } else {
        // Mode B: Browser Download (Fallback/USB Printer)
        console.log('Triggering download via server...');
        triggerDownload(res.data.btxml, res.data.carton_sn, res.data.id);
      }
    } else {
      console.warn('No BTXML content returned. Check Template Path in settings.');
      showNotification('Note: No print command generated. Check Settings.', 'warning');
    }
    
    // Auto-reset scan list for next carton of SAME product
    scannedItems.value = [];
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message;
    console.error('Finalize Error:', err);
    showNotification('Error finalizing carton: ' + errorMsg, 'error');
  } finally {
    isProcessing.value = false;
  }
};

const triggerDownload = (content, cartonSn, cartonId) => {
  if (!cartonId && lastCarton.value) cartonId = lastCarton.value.id;
  if (!cartonId) return;

  const downloadUrl = `http://${window.location.hostname}:8000/cartons/${cartonId}/btxml`;
  
  // Method 3: Use a hidden anchor tag (Most reliable for server-side downloads)
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.setAttribute('download', `print_job_${cartonSn || 'label'}.xml`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const resetSession = () => {
  currentProduct.value = null;
  scannedItems.value = [];
  scanBuffer.value = '';
};

const showNotification = (text, type = 'info') => {
  notification.value = { text, type };
  setTimeout(() => {
    notification.value = null;
  }, 3000);
};

const formatTime = () => {
  return new Date().toLocaleTimeString();
};

onMounted(() => {
  loadCustomers();
  loadSettings();
  // Keep focus on scan input, but don't steal from other inputs
  window.addEventListener('click', (e) => {
    // Don't steal focus if clicking on settings or other inputs
    if (showSettings.value) return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    
    if (scanInput.value) scanInput.value.focus();
  });
});
</script>

<style scoped>
.packing-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  padding: 40px 20px;
  color: #1e293b;
  display: flex;
  justify-content: center;
}

.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.main-card {
  width: 95%;
  max-width: 1000px; /* Narrower for selection screen */
  background: white;
  transition: max-width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-card.wide-layout {
  max-width: 1500px; /* Wider for packing station */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 10px;
}

.header h1 {
  color: #0f172a;
  font-weight: 700;
  margin: 0;
}

.status-badge {
  padding: 6px 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.online {
  background: #dcfce7;
  color: #166534;
}

.modern-select {
  width: 100%;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  color: #1e293b;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.modern-select:focus {
  border-color: #3b82f6;
}

.control-group label {
  display: block;
  margin-bottom: 10px;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.product-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover {
  background: white;
  transform: translateY(-4px);
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.product-card h3 {
  margin: 0 0 8px 0;
  color: #0f172a;
}

.product-card p {
  color: #64748b;
  font-size: 0.85rem;
  margin-bottom: 12px;
}

.qty-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #eff6ff;
  color: #2563eb;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.active-product h2 {
  margin: 0;
  color: #1e3a8a;
}

.meta {
  color: #64748b;
  margin-top: 4px;
}

.meta span { margin-right: 16px; }

.session-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
  margin-bottom: 16px;
  padding: 12px 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.active-product h2 {
  font-size: 1.25rem;
  margin: 0;
}

.progress-container {
  margin-bottom: 20px;
  background: #f1f5f9;
  padding: 12px 20px;
  border-radius: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 600;
}

.progress-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar .fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.scan-input {
  width: 100%;
  box-sizing: border-box;
  padding: 16px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.scan-input:focus {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  outline: none;
}

.hint {
  text-align: center;
  color: #94a3b8;
  font-size: 0.85rem;
}

.hint.warning {
  color: #ef4444;
  font-weight: 600;
}

.scan-input.input-locked {
  background: #fff1f2;
  border-color: #fecaca;
  color: #991b1b;
  cursor: not-allowed;
}

.packing-workspace {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

/* Responsive Layout */
@media (max-width: 1100px) {
  .packing-workspace {
    flex-direction: column;
    align-items: stretch;
  }
  
  .scanned-sidebar {
    width: 100% !important;
    height: 400px !important;
    position: relative !important;
    top: 0 !important;
  }
}

@media (max-width: 600px) {
  .packing-container {
    padding: 10px;
  }
  
  .main-card {
    padding: 12px;
  }
  
  .session-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header h1 {
    font-size: 1.25rem;
  }
  
  .banner-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn-reprint {
    width: 100%;
    justify-content: center;
  }
}

.main-workspace {
  flex: 1;
  min-width: 0; /* Allow shrinking */
}

.scanned-sidebar {
  width: 320px;
  background: #f1f5f9;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px); /* Larger height relative to screen */
  position: sticky;
  top: 10px;
}

.empty-list-hint {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #94a3b8;
  font-style: italic;
  font-size: 0.9rem;
}

.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.btn-clear {
  padding: 4px 8px;
  font-size: 0.75rem;
  color: #ef4444;
  background: transparent;
  border: none;
  cursor: pointer;
}

.scanned-list-container {
  overflow-y: auto;
  padding: 10px;
  flex: 1;
}

.item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 6px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-info .sn {
  font-weight: 600;
  color: #0f172a;
  font-size: 0.95rem;
}

.item-info .timestamp {
  font-size: 0.75rem;
  color: #94a3b8;
}

.index {
  font-size: 0.8rem;
  font-weight: 700;
  color: #cbd5e1;
}

.notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 16px 24px;
  border-radius: 12px;
  background: #1e293b;
  color: white;
  z-index: 3000;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.notification.success { background: #10b981; }
.notification.error { background: #ef4444; }
.notification.warning { background: #f59e0b; }

.result-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px dashed #e2e8f0;
}

.success-banner {
  background: #dcfce7;
  color: #166534;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.btn-reprint {
  margin-left: auto;
  background: #166534;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-reprint:hover {
  background: #15803d;
  transform: scale(1.05);
}

.btn-reprint.secondary {
  background: white;
  color: #166534;
  border: 1px solid #166534;
}

.banner-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

@keyframes bounceIn {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); opacity: 1; }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-icon {
  background: white;
  border: 1px solid #e2e8f0;
  color: #1e293b;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.btn-icon:hover {
  background: #f8fafc;
  color: #2563eb;
  border-color: #3b82f6;
  transform: scale(1.05);
}

.btn-icon i {
  font-size: 1.2rem;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  color: #1e293b;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #0f172a;
}

.subtitle {
  color: #64748b;
  margin-bottom: 24px;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
}

.modern-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  background: #f8fafc;
  color: #1e293b;
  outline: none;
  transition: border-color 0.2s;
}

.modern-input:focus {
  border-color: #3b82f6;
  background: white;
}

.input-with-hint small {
  display: block;
  margin-top: 4px;
  font-size: 0.75rem;
  color: #2563eb;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-text {
  background: transparent;
  color: #64748b;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
}

.btn-text:hover { color: #1e293b; }

.job-order-input {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 200px;
}

.job-order-input label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}

.modern-input-small {
  padding: 10px 14px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.modern-input-small:focus {
  background: white;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from { transform: translateY(20px); opacity: 0; }
.slide-up-leave-to { transform: translateY(20px); opacity: 0; }
</style>
