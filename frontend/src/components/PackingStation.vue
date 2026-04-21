<template>
  <div class="packing-container">
    <div class="glass-card main-card" :class="{ 'wide-layout': currentProduct }">
      <header class="header">
        <h1><i class="fas fa-box-open"></i> NY Packing Station</h1>
        <div class="header-actions">
          <div class="status-badge agent" :class="{ connected: isAgentConnected }" @click="checkAgent" title="Click to refresh Agent status">
            <i class="fas fa-print"></i> {{ isAgentConnected ? 'Agent Online' : 'Agent Offline' }}
          </div>
          <div class="status-badge" :class="{ online: isOnline }">
            {{ isOnline ? 'System Online' : 'Connecting...' }}
          </div>
          <button @click="toggleAudio" class="btn-icon status-audio" :class="{ active: isAudioActive }" :title="isAudioActive ? 'Audio Alert: Active (Click to Test)' : 'Audio Alert: Click to Activate/Test'">
            <i class="fas" :class="isAudioActive ? 'fa-volume-up' : 'fa-volume-mute'"></i>
          </button>
          <button @click="showEmergencyModal = true" class="btn-icon warning" title="Emergency Reprint">
            <i class="fas fa-exclamation-triangle"></i>
          </button>
          <button @click="showSettings = true" class="btn-icon" title="Settings">
            <i class="fas fa-cog"></i>
          </button>
        </div>
      </header>

      <!-- Agent Offline Critical Alert Banner -->
      <div v-if="!isAgentConnected" class="agent-offline-alert-banner fade-in">
        <div class="alert-content">
          <i class="fas fa-exclamation-triangle pulse-icon"></i>
          <span><strong>PRINT AGENT OFFLINE:</strong> Local printing is disabled. Please start <code>print_agent.exe</code> on this computer.</span>
        </div>
        <button @click="checkAgent" class="btn-retry-agent">
          <i class="fas fa-sync-alt"></i> Re-check
        </button>
      </div>


      <section class="selection-panel" v-if="!currentProduct">
        <div class="selection-header-row">
          <div class="control-group customer-select">
            <label>Customer</label>
            <select v-model="selectedCustomerId" @change="loadProducts" class="modern-select">
              <option value="" disabled>Choose a customer...</option>
              <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
            </select>
          </div>

          <div class="control-group product-search" v-if="selectedCustomerId">
            <label>Search Product</label>
            <div class="search-input-wrapper">
              <i class="fas fa-search search-icon"></i>
              <input 
                v-model="productSearch" 
                placeholder="Filter items..." 
                class="modern-input-small"
                ref="productSearchInput"
              />
            </div>
          </div>
        </div>

        <div class="control-group" v-if="selectedCustomerId">
          <div class="product-grid">
            <div 
              v-for="p in filteredProducts" 
              :key="p.id" 
              class="product-card"
              @click="selectProduct(p)"
            >
              <h3>{{ p.item_name }}</h3>
              <p>UPC: {{ p.upc }}</p>
              <div class="qty-tag">Target: {{ p.packed_qty }}</div>
            </div>
            <div v-if="filteredProducts.length === 0" class="no-results-hint">
               No products match your search.
            </div>
          </div>
        </div>
      </section>

      <section class="scanning-panel" v-else>
        <div class="packing-workspace">
          <!-- Main Area: Controls & Info -->
          <div class="main-workspace">
            <div class="session-info">
              <div class="session-header-row">
                <button @click="resetSession" class="btn-back-icon" title="Change Product">
                  <i class="fas fa-arrow-left"></i>
                </button>
                <div class="active-product">
                  <h2>{{ currentProduct.item_name }}</h2>
                  <div class="meta">
                    <span class="badge-outline">UPC: {{ currentProduct.upc }}</span>
                    <span class="badge-outline">Target: {{ currentProduct.packed_qty }}</span>
                  </div>
                </div>
                <div class="header-inputs">
                  <div class="job-order-input">
                    <label>Job Order</label>
                    <input 
                      v-model="jobOrder" 
                      placeholder="Enter Job Order..." 
                      class="modern-input-small"
                      ref="jobOrderInput"
                      @keyup.enter="scanInput.focus()"
                    />
                  </div>
                  <div class="job-order-input">
                    <label>Origin</label>
                    <select 
                      v-model="cartonOrigin" 
                      class="modern-input-small origin-select"
                      @change="scanInput.focus()"
                    >
                      <option value="VN">VN</option>
                      <option value="CN">CN</option>
                    </select>
                  </div>
                  <div class="job-order-input">
                    <label>Start S/N</label>
                    <input 
                      v-model="customSN" 
                      type="number"
                      placeholder="Auto" 
                      class="modern-input-small"
                      :class="{ 'input-err': customSN && parseInt(customSN) < suggestedSNValue }"
                      @keyup.enter="scanInput.focus()"
                    />
                    <span v-if="customSN && parseInt(customSN) < suggestedSNValue" class="input-error-hint">
                       Must be ≥ {{ suggestedSNValue }}
                    </span>
                  </div>
                  <div class="job-order-input">
                    <label>SN Pattern</label>
                    <input 
                      v-model="snPattern" 
                      placeholder="e.g. AS" 
                      class="modern-input-small sn-pattern-input"
                      @keyup.enter="scanInput.focus()"
                    />
                  </div>
                </div>
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
              <div class="success-banner" :class="{ 'error-banner': lastCarton.status === 'FAILED', 'printing-banner': lastCarton.status === 'PRINTING' }">
                <i class="fas" :class="{
                  'fa-check-circle': lastCarton.status === 'SUCCESS', 
                  'fa-exclamation-triangle': lastCarton.status === 'FAILED',
                  'fa-spinner fa-spin': lastCarton.status === 'PRINTING'
                }"></i>
                <span>
                  <template v-if="lastCarton.status === 'PRINTING'">
                    Printing Carton: <strong>{{ lastCarton.carton_sn }}</strong>...
                  </template>
                  <template v-else-if="lastCarton.status === 'SUCCESS'">
                    Last Carton: <strong>{{ lastCarton.carton_sn }}</strong>
                  </template>
                  <template v-else>
                    Previous Attempt Failed: <strong class="text-strike">{{ lastCarton.carton_sn }}</strong>
                    <span v-if="agentErrorMessage" class="error-detail"> - {{ agentErrorMessage }}</span>
                  </template>
                </span>
                <div class="banner-actions" v-if="lastCarton.status !== 'PRINTING'">
                  <a v-if="lastCarton.status === 'SUCCESS'" :href="`http://${host}:8000/cartons/${lastCarton.id}/btxml`" class="btn-reprint" download>
                    <i class="fas fa-file-download"></i> Manual Download
                  </a>
                  <button @click="finalizeCarton(true)" class="btn-reprint" :class="lastCarton.status === 'SUCCESS' ? 'secondary' : 'primary-err'">
                    <i class="fas fa-redo"></i> {{ lastCarton.status === 'SUCCESS' ? 'Re-Print' : 'Try Again' }}
                  </button>
                </div>
              </div>
            </div>

              <div class="input-area">
                <div class="input-row">
                  <input 
                    type="text" 
                    v-model="scanBuffer" 
                    @keyup.enter="handleScan"
                    :placeholder="!jobOrder ? '⚠️ PLEASE ENTER JOB ORDER FIRST...' : (awaitingNext ? '⚠️ BOX FULL! CLICK NEXT CARTON...' : 'Scan Item S/N...')"
                    ref="scanInput"
                    class="scan-input"
                    :class="{ 'input-locked': !jobOrder || awaitingNext }"
                  />
                  <button 
                    v-if="awaitingNext" 
                    @click="startNextCarton" 
                    class="btn-next-carton pulse-animation"
                    title="Start New Carton"
                  >
                    <i class="fas fa-plus-circle"></i> Next Carton
                  </button>
                </div>
                <p class="hint" v-if="jobOrder && !awaitingNext">Waiting for scanner input (Enter to submit)</p>
                <p class="hint success" v-else-if="awaitingNext">Box Complete! Please move to next box and click button above</p>
                <p class="hint warning" v-else>Please fill in the Job Order field at the top first</p>

                <!-- Invalid Scans Area -->
                <div v-if="invalidScans.length > 0" class="invalid-scans-area fade-in">
                  <div class="invalid-header">
                    <span><i class="fas fa-exclamation-circle"></i> Invalid Scans</span>
                    <button @click="invalidScans = []" class="btn-clear-small">Clear</button>
                  </div>
                  <div class="invalid-list">
                    <div v-for="(err, idx) in [...invalidScans].reverse()" :key="idx" class="invalid-item" :class="`type-${err.type || 'generic'}`">
                      <div class="bad-info">
                        <span class="bad-sn">{{ err.sn }}</span>
                        <span class="bad-reason">{{ err.reason }}</span>
                      </div>
                      <span class="bad-time">{{ err.time }}</span>
                    </div>
                  </div>
                </div>
              </div>
          </div>

          <!-- Sidebar: Scanned Items -->
          <div class="scanned-sidebar glass-sidebar">
            <div class="sidebar-header">
              <h3>Scanned ({{ scannedItems.length }})</h3>
              <button @click="scannedItems = []" class="btn-clear" v-if="scannedItems.length > 0">Clear</button>
            </div>
            <div class="scanned-list-container" ref="scannedListContainer">
              <div v-if="scannedItems.length === 0" class="empty-list-hint">
                No items scanned
              </div>
              <ul class="scanned-list" v-else>
                <li v-for="(item, idx) in scannedItems" :key="idx" class="fade-in item-card">
                  <div class="item-info">
                    <span class="sn">{{ item }}</span>
                  </div>
                  <div class="index">#{{ idx + 1 }}</div>
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
        <i class="fas" :class="notification.type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'"></i>
        {{ notification.text }}
      </div>
    </Transition>

    <!-- Emergency Reprint Modal -->
    <div v-if="showEmergencyModal" class="modal-overlay" @click.self="showEmergencyModal = false">
      <div class="modal-card emergency-modal">
        <div class="modal-header-modern">
          <div class="header-title">
            <i class="fas fa-search"></i>
            <h2>Find & Reprint</h2>
          </div>
          <button @click="showEmergencyModal = false" class="btn-close-modern"><i class="fas fa-times"></i></button>
        </div>
        
        <div class="modal-body-modern">
          <p class="emergency-hint">Enter an exact Carton S/N to retrieve and reprint its label.</p>
          
          <div class="search-box-modern">
            <div class="search-input-wrapper">
              <i class="fas fa-barcode search-icon"></i>
              <input 
                v-model="emergencySearchSN" 
                placeholder="e.g. CN26040000001" 
                @keyup.enter="handleEmergencySearch"
                class="modern-search-input"
              />
            </div>
            <button @click="handleEmergencySearch" :disabled="emergencySearchLoading" class="btn-search-modern">
              <i class="fas fa-spinner fa-spin" v-if="emergencySearchLoading"></i>
              <span v-else>Search</span>
            </button>
          </div>

          <div v-if="emergencyResult" class="emergency-result-card fade-in">
            <div class="result-header">
              <div class="status-indicator success"></div>
              <h3>{{ emergencyResult.carton_sn }}</h3>
            </div>
            
            <div class="result-details">
              <div class="detail-group">
                <span class="label">Product</span>
                <span class="value">{{ emergencyResult.product.item_name }}</span>
              </div>
              <div class="detail-row">
                <div class="detail-group">
                  <span class="label">Job Order</span>
                  <span class="value">{{ emergencyResult.job_order || 'N/A' }}</span>
                </div>
                <div class="detail-group">
                  <span class="label">Items</span>
                  <span class="value">{{ emergencyResult.items ? emergencyResult.items.length : '?' }} pcs</span>
                </div>
                <div class="detail-group">
                  <span class="label">Date</span>
                  <span class="value">{{ new Date(emergencyResult.created_at).toLocaleDateString() }}</span>
                </div>
              </div>
            </div>
            
            <div class="result-actions">
              <button @click="handleEmergencyReprint" :disabled="emergencySearchLoading" class="btn-print-action">
                <i class="fas fa-spinner fa-spin" v-if="emergencySearchLoading"></i>
                <i class="fas fa-print" v-else></i>
                <span>Print Label</span>
              </button>
            </div>
          </div>
          
          <div v-else-if="emergencySearchSN && !emergencySearchLoading && !emergencyResult" class="no-result-card">
            <div class="no-result-icon"><i class="fas fa-box-open"></i></div>
            <p>No successful carton found with this S/N.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="glass-card modal-content settings-modal">
        <div class="modal-header-modern">
          <div class="header-title">
            <i class="fas fa-cog"></i>
            <h2>Station Settings</h2>
          </div>
          <button @click="showSettings = false" class="btn-close-modern"><i class="fas fa-times"></i></button>
        </div>
        
        <div class="modal-body-scrollable">
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
            <label>Print Job Folder</label>
            <div class="input-with-hint">
              <input v-model="settings.printFolder" placeholder="D:\print_test" class="modern-input" />
              <small class="hint-text">
                Folder where XML files will be saved for BarTender to watch.
              </small>
            </div>
          </div>

          <div class="form-group checkbox-group">
            <label class="modern-checkbox">
              <input type="checkbox" v-model="settings.serverPrint" />
              <span>Process Print on Server</span>
            </label>
            <small class="hint-text">If OFF, the local Agent or Browser Download will be used.</small>
          </div>

          <div class="form-group">
            <label>Printer Name (Windows)</label>
            <div class="input-with-hint">
              <input v-model="settings.printerName" placeholder="Leave blank for BarTender Default" class="modern-input" />
              <small>Hint: If blank, BarTender will use the printer saved in the .btw file.</small>
            </div>
          </div>

          <div class="form-group">
            <label>Alert Speaker (Audio Output)</label>
            <div class="input-with-hint">
              <select v-model="settings.audioDeviceId" class="modern-input">
                <option value="">Default System Output</option>
                <option v-for="d in audioDevices" :key="d.id" :value="d.id">{{ d.label }}</option>
              </select>
              <button @click="requestAudioPermission" class="btn-text-small" style="margin-top: 8px;" v-if="audioDevices.length > 0 && audioDevices[0].label.startsWith('Speaker (')">
                <i class="fas fa-lock"></i> Click to see Speaker Names (Requires Permission)
              </button>
              <small class="hint-text">Choose which speaker should play the "Invalid Scan" alert sound.</small>
            </div>
          </div>
        </div>

        <div class="modal-actions-sticky">
          <button @click="showSettings = false" class="btn-text">Cancel</button>
          <button @click="saveSettings" class="btn-primary">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
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
const scannedListContainer = ref(null); // Ref for sidebar scroll
const productSearchInput = ref(null); // Ref for product search filter
const showSettings = ref(false);
const lastCarton = ref(null);
const jobOrder = ref(''); // New Job Order state
const cartonOrigin = ref('VN'); // New Origin state
const customSN = ref(''); // Custom starting SN
const snPattern = ref(''); // SN Pattern prefix validation
const invalidScans = ref([]); // Store scans that failed pattern check
const awaitingNext = ref(false); // New state: waiting for manual "Next" click
const suggestedSNValue = ref(0); // Store DB suggested next sequence
const isAgentConnected = ref(false);
const showEmergencyModal = ref(false);
const emergencySearchSN = ref('');
const emergencyResult = ref(null);
const emergencySearchLoading = ref(false);
const productSearch = ref(''); // New Product Search state
const agentErrorMessage = ref(''); // Store the specific BarTender error
const backupScannedItems = ref([]); // Store items in case of failure
const isAudioActive = ref(false); // Audio status indicator
const audioDevices = ref([]); // List of available speakers
let statusTimer = null;

const settings = ref({
  stationId: '',
  templatePath: '',
  printerName: '',
  printFolder: '',
  audioDeviceId: '', // Selected speaker ID
  serverPrint: false
});

const loadSettings = () => {
  const saved = localStorage.getItem('ny_packing_settings');
  if (saved) {
    const parsed = JSON.parse(saved);
    // Merge with defaults to ensure new fields like printFolder exist
    settings.value = { ...settings.value, ...parsed };
  }
};

const saveSettings = async () => {
  localStorage.setItem('ny_packing_settings', JSON.stringify(settings.value));
  showSettings.value = false;
  showNotification('Settings saved locally', 'success');

  // Notify agent if connected
  if (isAgentConnected.value) {
    try {
      await fetch('http://127.0.0.1:1234/print', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'config',
          path: settings.value.printFolder
        })
      });
    } catch (e) {
      console.warn('Failed to notify agent of config change');
    }
  }
};

const progressPercent = computed(() => {
  if (!currentProduct.value) return 0;
  return Math.round((scannedItems.value.length / currentProduct.value.packed_qty) * 100);
});

const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value;
  const q = productSearch.value.toLowerCase();
  return products.value.filter(p => 
    p.item_name.toLowerCase().includes(q) || 
    p.upc.toLowerCase().includes(q)
  );
});


const loadCustomers = async () => {
  try {
    const res = await api.getCustomers();
    customers.value = res.data;
    isOnline.value = true;

    // Auto-select first customer if none selected
    if (customers.value.length > 0 && !selectedCustomerId.value) {
      selectedCustomerId.value = customers.value[0].id;
      loadProducts();
      // Focus search after customer is selected and input renders
      nextTick(() => {
        if (productSearchInput.value) productSearchInput.value.focus();
      });
    }
  } catch (err) {
    showNotification('Cannot connect to API', 'error');
  }
};

const loadProducts = async () => {
  if (!selectedCustomerId.value) return;
  try {
    const res = await api.getCustomerProducts(selectedCustomerId.value);
    products.value = res.data;
    // Clearing previous search for fresh start
    productSearch.value = '';
    // Focus the search input for new customer's products
    nextTick(() => {
      if (productSearchInput.value) productSearchInput.value.focus();
    });
  } catch (err) {
    showNotification('Error loading products', 'error');
  }
};

const selectProduct = async (p) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = p;
  scannedItems.value = [];
  lastCarton.value = null;
  agentErrorMessage.value = '';
  customSN.value = ''; // Reset first
  
  // Fetch next SN info to use as default value
  try {
    const snRes = await api.getNextSN(p.id);
    if (snRes.data && snRes.data.next_seq) {
      customSN.value = snRes.data.next_seq.toString();
      suggestedSNValue.value = snRes.data.next_seq;
    }
  } catch (err) {
    console.warn('Error fetching next SN preview:', err);
  }
  
  // Fetch the last carton for this product immediately
  try {
    const res = await api.getLastCarton(p.id);
    if (res.data) {
      lastCarton.value = res.data;
      if (res.data.status === 'FAILED' && res.data.items) {
        // Pre-load items so that "Try Again" can work without rescanning all over again
        backupScannedItems.value = res.data.items.map(i => i.item_sn);
        if (!jobOrder.value) {
            jobOrder.value = res.data.job_order || '';
        }
      }
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

  // AGENT CONNECTION CHECK: Block all scans if Agent is offline
  if (!isAgentConnected.value) {
    showNotification('CRITICAL: Print Agent is OFFLINE! Cannot scan.', 'error', 0);
    playScanAlert();
    scanBuffer.value = '';
    return;
  }

  // LOCKDOWN LOGIC: If there are ANY invalid scans, block all subsequent scans
  if (invalidScans.value.length > 0) {
    invalidScans.value.push({
      sn: sn,
      time: new Date().toLocaleTimeString(),
      reason: 'invalid', // Explicit generic reason as requested
      type: 'lockdown'
    });
    showNotification('STATION LOCKED! Clear invalid scans first.', 'error');
    playScanAlert();
    scanBuffer.value = '';
    return;
  }

  // Handle scans when box is already full
  if (awaitingNext.value) {
    invalidScans.value.push({
      sn: sn,
      time: new Date().toLocaleTimeString(),
      reason: 'Excess Scan (Box Full)',
      type: 'excess'
    });
    showNotification('BOX FULL! This scan will NOT be added to current box.', 'warning');
    playScanAlert(); // Trigger audio alert
    scanBuffer.value = '';
    return;
  }

  // Pattern Validation
  if (snPattern.value && !sn.startsWith(snPattern.value)) {
    invalidScans.value.push({
      sn: sn,
      time: new Date().toLocaleTimeString(),
      reason: 'Prefix mismatch',
      type: 'pattern'
    });
    showNotification(`Invalid Pattern! SN must start with "${snPattern.value}"`, 'error');
    playScanAlert(); // Trigger audio alert
    scanBuffer.value = '';
    return;
  }

  if (scannedItems.value.includes(sn)) {
    invalidScans.value.push({
      sn: sn,
      time: new Date().toLocaleTimeString(),
      reason: 'Duplicate S/N',
      type: 'duplicate'
    });
    showNotification(`Duplicate S/N: ${sn}`, 'warning');
    playScanAlert(); // Trigger audio alert
    scanBuffer.value = '';
    return;
  }

  scannedItems.value.push(sn);
  scanBuffer.value = '';

  if (scannedItems.value.length >= currentProduct.value.packed_qty) {
    // Set status to full IMMEDIATELY so scanner can catch excess items 
    // while the server/printer is still thinking
    awaitingNext.value = true;
    finalizeCarton();
  }
};

const finalizeCarton = async (isRetry = false) => {
  isProcessing.value = true;
  agentErrorMessage.value = '';
  
  try {
    let cartonId, cartonSn, btxmlContent;

    if (isRetry && lastCarton.value) {
      // Re-print or Try-again flow: exactly reprint previous carton, do not create new snippet
      cartonId = lastCarton.value.id;
      cartonSn = lastCarton.value.carton_sn;
      btxmlContent = lastCarton.value.btxml; // Ensure this is available from previous response
      lastCarton.value.status = 'PRINTING';
    } else {
      // New carton flow
      if (customSN.value && !isNaN(parseInt(customSN.value))) {
        const inputVal = parseInt(customSN.value);
        if (inputVal < suggestedSNValue.value) {
          showNotification(`ERROR: Start S/N cannot be lower than ${suggestedSNValue.value}`, 'error');
          // Scroll to top to see notification
          window.scrollTo({ top: 0, behavior: 'smooth' });
          isProcessing.value = false;
          return;
        }
      }
      
      const itemsToPack = [...scannedItems.value];
      if (itemsToPack.length === 0) {
        showNotification('No items to pack!', 'error');
        isProcessing.value = false;
        return;
      }

      const res = await api.createCarton({
        product_id: currentProduct.value.id,
        items: itemsToPack,
        template_path: settings.value.templatePath || null,
        printer_name: settings.value.printerName || null,
        print_folder: settings.value.printFolder || null,
        job_order: jobOrder.value,
        custom_sn: customSN.value ? parseInt(customSN.value) : null,
        carton_origin: cartonOrigin.value
      });
      
      cartonId = res.data.id;
      cartonSn = res.data.carton_sn;
      btxmlContent = res.data.btxml;
      
      // Set status to PRINTING initially to avoid UI flash of red FAILED
      const cartonData = { ...res.data, status: 'PRINTING' };
      lastCarton.value = cartonData;
      backupScannedItems.value = itemsToPack; // Save for potential future use
    }

    // Client-Side Printing Logic
    console.log('Attempting print via Local Agent...');
    const printStatus = await handleClientPrint(btxmlContent, cartonSn, cartonId);
    
      if (printStatus === 'Success') {
        await api.updateCartonStatus(cartonId, 'SUCCESS');
        lastCarton.value.status = 'SUCCESS';
        showNotification(`Carton ${cartonSn} Printed Successfully!`, 'success');
        
        // Auto-increment custom S/N immediately
        if (!isRetry) {
          if (customSN.value && !isNaN(parseInt(customSN.value))) {
            customSN.value = (parseInt(customSN.value) + 1).toString();
          }
          // Set state to awaiting manual reset
          awaitingNext.value = true;
          // Re-focus immediately so they can keep scanning excess items
          nextTick(() => {
            if (scanInput.value) scanInput.value.focus();
          });
        }
      } else {
      // Print failed: notify and leave items in buffer for retry
      lastCarton.value.status = 'FAILED';
      agentErrorMessage.value = printStatus; // Show reason
      showNotification(`Print failed: ${printStatus}`, 'error');
    }
  } catch (err) {
    console.error('Error finalizing carton:', err);
    if (lastCarton.value && !isRetry) lastCarton.value.status = 'FAILED';
    showNotification('Failed to generate carton on server.', 'error');
  } finally {
    isProcessing.value = false;
  }
};

const handleClientPrint = async (content, cartonSn, cartonId) => {
  try {
    const agentRes = await fetch('http://127.0.0.1:1234/print', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        xml: content,
        filename: `print_job_${cartonSn}.xml`,
        path: settings.value.printFolder || null
      })
    });

    isAgentConnected.value = true;
    const resultText = await agentRes.text();
    return resultText; // This will return "Success" or "Print Failed: ..."
  } catch (err) {
    console.warn('Local Agent connection failed', err);
    isAgentConnected.value = false;
    return 'Error: Could not connect to local Print Agent. Please ensure it is running.';
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

const checkAgent = async () => {
  try {
    const res = await fetch('http://127.0.0.1:1234/', { 
      method: 'GET',
      signal: AbortController.timeout ? AbortController.timeout(1000) : null // Short timeout
    });
    const wasConnected = isAgentConnected.value;
    isAgentConnected.value = res.ok;

    if (isAgentConnected.value && !wasConnected) {
      // Clear offline notification if it exists
      if (notification.value && notification.value.text.includes('Agent is OFFLINE')) {
        notification.value = null;
      }
      showNotification('Print Agent Connected!', 'success');
    }
  } catch (e) {
    isAgentConnected.value = false;
  }

  if (!isAgentConnected.value) {
    // Continuously show error as requested by user
    showNotification('CRITICAL: Print Agent is OFFLINE! Please run the agent.', 'error', 0);
  }
};

const checkSystem = async () => {
  try {
    const res = await api.checkHealth();
    isOnline.value = res.data && res.data.status === 'ok';
  } catch (e) {
    isOnline.value = false;
  }
};

const startNextCarton = () => {
  scannedItems.value = [];
  invalidScans.value = [];
  awaitingNext.value = false;
  // lastCarton stays visible so user knows what they just finished
  nextTick(() => {
    if (scanInput.value) scanInput.value.focus();
  });
};

onMounted(() => {
  loadAudioDevices();
  // Listen for device changes
  if (navigator.mediaDevices) {
    navigator.mediaDevices.addEventListener('devicechange', loadAudioDevices);
  }
});

onUnmounted(() => {
    if (navigator.mediaDevices) {
        navigator.mediaDevices.removeEventListener('devicechange', loadAudioDevices);
    }
});

watch(showSettings, (val) => {
  if (val) loadAudioDevices();
});

const resetSession = () => {
  currentProduct.value = null;
  scannedItems.value = [];
  invalidScans.value = [];
  awaitingNext.value = false;
  scanBuffer.value = '';
  // Focus search input after returning to selection screen
  nextTick(() => {
    if (productSearchInput.value) productSearchInput.value.focus();
  });
};

const showNotification = (text, type = 'info', duration = 3000) => {
  notification.value = { text, type };
  if (duration > 0) {
    setTimeout(() => {
      notification.value = null;
    }, duration);
  }
};

const playScanAlert = async () => {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    // Set output device if selected
    if (settings.value.audioDeviceId && audioCtx.setSinkId) {
      try {
        await audioCtx.setSinkId(settings.value.audioDeviceId);
      } catch (sinkErr) {
        console.warn('Could not set custom speaker, using default:', sinkErr);
      }
    }

    const playBeep = (freq, startTime, duration) => {
      const oscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);

      oscillator.type = 'square'; 
      oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime + startTime);
      
      gainNode.gain.setValueAtTime(0, audioCtx.currentTime + startTime);
      gainNode.gain.linearRampToValueAtTime(0.1, audioCtx.currentTime + startTime + 0.05);
      gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + startTime + duration);

      oscillator.start(audioCtx.currentTime + startTime);
      oscillator.stop(audioCtx.currentTime + startTime + duration);
    };

    // Play a sequence of 3 long, low-frequency beeps (approx 1.5s total)
    playBeep(150, 0, 0.4);
    playBeep(150, 0.5, 0.4);
    playBeep(150, 1.0, 0.4);

  } catch (e) {
    console.warn('Audio alert failed:', e);
  }
};

const toggleAudio = () => {
  isAudioActive.value = true;
  playScanAlert();
  showNotification('Audio Alert: ACTIVE (Test Successful)', 'success');
};

const loadAudioDevices = async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
    console.warn('Audio device enumeration not supported');
    return;
  }
  
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    audioDevices.value = devices
      .filter(d => d.kind === 'audiooutput')
      .map(d => ({
        id: d.deviceId,
        label: d.label || `Speaker (${d.deviceId.slice(0, 5)}...)`
      }));
    
    // If we have devices but labels are empty, it means we need permission
    if (audioDevices.value.length > 0 && !audioDevices.value[0].label.includes('Speaker')) {
       // Labels are available
    }
  } catch (e) {
    console.warn('Error loading audio devices:', e);
  }
};

const requestAudioPermission = async () => {
  try {
    // Requesting micro permission is the standard way to unlock all device labels
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    // Stop the stream immediately
    stream.getTracks().forEach(track => track.stop());
    // Re-load devices to get labels
    await loadAudioDevices();
    showNotification('Audio devices refreshed', 'success');
  } catch (err) {
    showNotification('Could not access audio labels. Check browser permissions.', 'error');
  }
};

const formatTime = () => {
  return new Date().toLocaleTimeString();
};

const handleEmergencySearch = async () => {
  if (!emergencySearchSN.value) return;
  emergencySearchLoading.value = true;
  emergencyResult.value = null;
  try {
    const res = await api.searchCarton(emergencySearchSN.value.trim());
    if (res.data) {
      emergencyResult.value = res.data;
    } else {
      showNotification('Carton not found or not successfully printed.', 'warning');
    }
  } catch (err) {
    showNotification('Search failed: ' + (err.response?.data?.detail || err.message), 'error');
  } finally {
    emergencySearchLoading.value = false;
  }
};

const handleEmergencyReprint = async () => {
  if (!emergencyResult.value) return;
  
  emergencySearchLoading.value = true;
  try {
    // Call the reprint/logging endpoint (this creates a new Carton record and returns new BTXML)
    const res = await api.reprintCarton(
      emergencyResult.value.id, 
      settings.value.templatePath,
      settings.value.printerName
    );
    
    // The response is the new Carton object (with the generated btxml attached)
    const newCarton = res.data;
    
    if (!newCarton || !newCarton.btxml) {
      showNotification('Could not generate reprint data.', 'error');
      return;
    }

    const result = await handleClientPrint(
      newCarton.btxml, 
      newCarton.carton_sn, 
      newCarton.id
    );
    
    if (result === 'Success') {
      showNotification(`Reprint successful: ${emergencyResult.value.carton_sn}`, 'success');
      showEmergencyModal.value = false;
    } else {
      showNotification('Reprint failed: ' + result, 'error');
    }
  } catch (err) {
    showNotification('Reprint error: ' + (err.response?.data?.detail || err.message), 'error');
  } finally {
    emergencySearchLoading.value = false;
  }
};

// Auto-save state
watch([jobOrder, cartonOrigin, currentProduct, scannedItems, customSN, snPattern, awaitingNext, suggestedSNValue, backupScannedItems, lastCarton, invalidScans], () => {
  sessionStorage.setItem('packingState', JSON.stringify({
    jobOrder: jobOrder.value,
    cartonOrigin: cartonOrigin.value,
    currentProduct: currentProduct.value,
    scannedItems: scannedItems.value,
    customSN: customSN.value,
    snPattern: snPattern.value,
    awaitingNext: awaitingNext.value,
    suggestedSNValue: suggestedSNValue.value,
    backupScannedItems: backupScannedItems.value,
    lastCarton: lastCarton.value,
    invalidScans: invalidScans.value
  }));
}, { deep: true });

// Auto-scroll Scanned Items to bottom
watch(scannedItems, () => {
  nextTick(() => {
    if (scannedListContainer.value) {
      scannedListContainer.value.scrollTo({
        top: scannedListContainer.value.scrollHeight,
        behavior: 'smooth'
      });
    }
  });
}, { deep: true });

onMounted(() => {
  // Restore state
  const savedState = sessionStorage.getItem('packingState');
  if (savedState) {
    try {
      const state = JSON.parse(savedState);
      if (state.jobOrder) jobOrder.value = state.jobOrder;
      if (state.cartonOrigin) cartonOrigin.value = state.cartonOrigin;
      if (state.currentProduct) currentProduct.value = state.currentProduct;
      if (state.scannedItems) scannedItems.value = state.scannedItems;
      if (state.customSN) customSN.value = state.customSN;
      if (state.snPattern) snPattern.value = state.snPattern;
      if (state.awaitingNext !== undefined) awaitingNext.value = state.awaitingNext;
      if (state.suggestedSNValue !== undefined) suggestedSNValue.value = state.suggestedSNValue;
      if (state.backupScannedItems) backupScannedItems.value = state.backupScannedItems;
      if (state.lastCarton) lastCarton.value = state.lastCarton;
      if (state.invalidScans) invalidScans.value = state.invalidScans;
    } catch (e) {
      console.error('Failed to restore packing state', e);
    }
  }

  loadCustomers();
  loadSettings();
  
  // Initial checks
  checkAgent();
  checkSystem();

  // Focus search if on selection page
  nextTick(() => {
    if (!currentProduct.value && productSearchInput.value) {
      productSearchInput.value.focus();
    }
  });
  
  // Setup polling every 5 seconds
  statusTimer = setInterval(() => {
    checkAgent();
    checkSystem();
  }, 5000);

  // Keep focus on scan input, but don't steal from other inputs
  window.addEventListener('click', (e) => {
    // Don't steal focus if clicking on settings or other inputs
    if (showSettings.value) return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    
    if (scanInput.value) scanInput.value.focus();
  });
});

onUnmounted(() => {
  if (statusTimer) clearInterval(statusTimer);
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
  padding: 12px 18px;
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
  margin-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 8px;
}

.header h1 {
  color: #0f172a;
  font-weight: 700;
  margin: 0;
  font-size: 1.35rem;
}

.status-badge {
  padding: 6px 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.agent {
  background: #f1f5f9;
  color: #64748b;
  margin-right: 8px;
}

.status-badge.agent.connected {
  background: #e0f2fe;
  color: #0369a1;
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
  /* width: 100%; removed to support flex layout with Next button */
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
.checkbox-group {
  margin-top: 15px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
}

.modern-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-weight: 600;
  color: #1e293b;
}

.modern-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

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
.success-banner.error-banner {
  background: #fee2e2;
  color: #991b1b;
}
.text-strike { text-decoration: line-through; opacity: 0.7; }
.error-detail { font-size: 0.85rem; font-weight: normal; margin-left: 5px; }

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

.btn-reprint.primary-err {
  background: #ef4444;
}
.btn-reprint.primary-err:hover {
  background: #dc2626;
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
  background: #f8fafc;
  color: #2563eb;
  border-color: #3b82f6;
  transform: scale(1.05);
}

.btn-icon.status-audio {
  color: #94a3b8;
  border-color: #e2e8f0;
  background: white;
  transform: none;
}

.btn-icon.status-audio.active {
  color: #2563eb;
  border-color: #3b82f6;
  background: #eff6ff;
  transform: scale(1.05);
}

.btn-icon.status-audio:hover {
  background: #f1f5f9;
  transform: scale(1.1);
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

.btn-icon.warning:hover {
  background: #fdf4ff;
  transform: scale(1.1) rotate(5deg);
}

.agent-offline-alert-banner {
  background: #ef4444;
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  animation: slideDown 0.3s ease-out;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 1rem;
}

.pulse-icon {
  font-size: 1.5rem;
  animation: pulse 1.5s infinite;
}

.btn-retry-agent {
  background: white;
  color: #ef4444;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-retry-agent:hover {
  background: #fee2e2;
  transform: scale(1.05);
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-card.emergency-modal {
  width: 95%;
  max-width: 600px;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
}

.modal-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px 16px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1e293b;
}

.header-title i {
  font-size: 1.5rem;
  color: #2563eb;
}

.header-title h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.btn-close-modern {
  background: #f1f5f9;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-close-modern:hover {
  background: #e2e8f0;
  color: #0f172a;
  transform: rotate(90deg);
}

.modal-body-modern {
  padding: 0 32px 32px;
}

.emergency-hint {
  color: #64748b;
  font-size: 0.95rem;
  margin-bottom: 24px;
}

.search-box-modern {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 6px;
  display: flex;
  gap: 8px;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 32px;
}

.search-box-modern:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  padding-left: 12px;
}

.search-icon {
  color: #94a3b8;
  font-size: 1.1rem;
}

.modern-search-input {
  width: 100%;
  border: none;
  padding: 12px 14px;
  font-size: 1rem;
  color: #1e293b;
  outline: none;
  background: transparent;
}

.btn-search-modern {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-search-modern:hover {
  background: #1d4ed8;
}

.btn-search-modern:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.emergency-result-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
}

.result-header {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.input-err {
  border-color: #ef4444 !important;
  background-color: #fef2f2 !important;
}

.input-error-hint {
  display: block;
  color: #ef4444;
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 4px;
}

.status-indicator.success {
  background: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.result-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #0f172a;
  font-family: monospace;
  letter-spacing: 0.5px;
}

.result-details {
  padding: 20px;
}

.detail-row {
  display: flex;
  gap: 24px;
  margin-top: 16px;
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-group .label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  font-weight: 600;
}

.detail-group .value {
  color: #1e293b;
  font-weight: 500;
  font-size: 0.95rem;
}

.result-actions {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}

.btn-print-action {
  background: #1e293b;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
}

.btn-print-action:hover:not(:disabled) {
  background: #0f172a;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px -3px rgba(15, 23, 42, 0.2);
}

.btn-print-action:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.no-result-card {
  text-align: center;
  padding: 40px 20px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px dashed #cbd5e1;
}

.no-result-icon {
  font-size: 3rem;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.no-result-card p {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.modal-content {
  background: white;
  padding: 0; /* Reset padding for new layout */
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  color: #1e293b;
  overflow: hidden; /* Important for sticky header/footer */
}

/* Modals that need scrolling */
.settings-modal {
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-body-scrollable {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-header-modern {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.modal-header-modern .header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #0f172a;
}

.modal-header-modern h2 {
  margin: 0;
  font-size: 1.25rem;
}

.btn-close-modern {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 1.25rem;
  cursor: pointer;
  transition: color 0.2s;
}
.btn-close-modern:hover { color: #ef4444; }

.modal-actions-sticky {
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: auto;
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

.input-with-hint small.hint-text {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.4;
  background: #f1f5f9;
  padding: 8px;
  border-radius: 6px;
}

.input-with-hint small.hint-text strong {
  color: #2563eb;
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

.btn-text-small {
  background: transparent;
  border: 1px solid #cbd5e1;
  color: #64748b;
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-text-small:hover {
  background: #f1f5f9;
  color: #2563eb;
  border-color: #3b82f6;
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

.session-header-row {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  width: 100%;
}

.btn-back-icon {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #64748b;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-top: 4px;
}

.btn-back-icon:hover {
  background: #e2e8f0;
  color: #1e293b;
  transform: translateX(-2px);
}

.active-product {
  flex: 1;
}

.active-product h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #1e3a8a;
  line-height: 1.2;
}

.badge-outline {
  display: inline-block;
  padding: 2px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #64748b;
  margin-right: 8px;
  background: white;
}

.header-inputs {
  display: flex;
  gap: 12px;
}

.job-order-input {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.job-order-input label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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

.modern-input-small.input-err {
  border-color: #ef4444 !important;
  background: #fff1f2 !important;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input-error-hint {
  color: #e11d48;
  font-size: 0.65rem;
  font-weight: 600;
  margin-top: 2px;
  display: block;
}

.modern-input-small:focus {
  background: white;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from { transform: translateY(20px); opacity: 0; }
.slide-up-leave-to { transform: translateY(20px); opacity: 0; }

/* Invalid Scans Stying */
.invalid-scans-area {
  margin-top: 20px;
  background: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.invalid-header {
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #feb2b2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c53030;
  font-size: 0.85rem;
  font-weight: 700;
}

.invalid-header i {
  margin-right: 6px;
}

.btn-clear-small {
  background: transparent;
  border: 1px solid #feb2b2;
  color: #c53030;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear-small:hover {
  background: #fff5f5;
  border-color: #c53030;
}

.invalid-list {
  max-height: 150px;
  overflow-y: auto;
  padding: 8px;
}

.invalid-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: white;
  border-radius: 6px;
  margin-bottom: 4px;
  border: 1px solid #fed7d7;
}

.bad-sn {
  font-family: monospace;
  font-weight: 600;
  color: #e53e3e;
}

.bad-reason {
  font-size: 0.7rem;
  background: #fecaca;
  color: #b91c1c;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Specific Error Colors */
.type-pattern .bad-reason {
  background: #ffedd5;
  color: #9a3412;
}

.type-duplicate .bad-reason {
  background: #f3e8ff;
  color: #6b21a8;
}

.type-pattern { border-left: 4px solid #f97316; }
.type-duplicate { border-left: 4px solid #a855f7; }
.type-excess { border-left: 4px solid #ef4444; }
.type-generic { border-left: 4px solid #ef4444; }

.bad-info {
  display: flex;
  align-items: center;
}

.bad-time {
  font-size: 0.75rem;
  color: #a0aec0;
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.btn-next-carton {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0 24px;
  height: 58px; /* Match scan input height roughly */
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  transition: all 0.2s;
}

.btn-next-carton:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.pulse-animation {
  animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.hint.success {
  color: #059669;
  font-weight: 700;
}

.scan-input.input-locked {
  /* Keep it looking active but distinct */
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #64748b;
  cursor: not-allowed;
  flex: 1; /* Ensure it takes available space but doesn't push others out */
  min-width: 0;
}

.scan-input {
  flex: 1; /* Added to support the Next button in the same row */
  min-width: 0;
}

.sn-pattern-input {
  width: 100px;
  border-color: #93c5fd;
  color: #1e40af;
}

.sn-pattern-input:focus {
  border-color: #2563eb;
  background: #eff6ff;
}

.selection-header-row {
  display: flex;
  gap: 16px;
  align-items: center; /* Better alignment */
  margin-bottom: 24px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.customer-select {
  width: 250px;
  margin-bottom: 0; /* Override default */
}

.product-search {
  flex: 1;
  margin-bottom: 0;
}

.customer-select label, .product-search label {
  margin-bottom: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-wrapper .search-icon {
  position: absolute;
  left: 18px;
  color: #3b82f6;
  font-size: 0.95rem;
}

.search-input-wrapper input.modern-input-small {
  padding-left: 48px;
  width: 100%;
  height: 42px; /* Fixed height for alignment */
}

/* Ensure select matches input height */
.customer-select .modern-select {
  height: 42px;
  padding: 0 12px;
  font-size: 0.95rem;
}

.no-results-hint {
  grid-column: 1 / -1;
  padding: 40px;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px dashed #e2e8f0;
}
</style>
