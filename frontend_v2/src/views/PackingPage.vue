<template>
  <div class="packing-container">
    <div class="glass-card main-card" :class="{ 'wide-layout': currentProduct }">
      <AppHeader
        :isAudioActive="isAudioActive"
        @check-agent="checkAgent"
        @toggle-audio="toggleAudio"
        @show-emergency="showEmergencyModal = true"
        @show-settings="showSettings = true"
      />

      <CatalogSelection
        v-if="!currentProduct"
        ref="catalogRef"
        @select-product="selectProduct"
      />

      <section class="scanning-panel" v-else>
        <div class="packing-workspace">
          <div class="main-workspace">
            <SessionHeader
              ref="sessionRef"
              :product="currentProduct"
              v-model:jobOrder="jobOrder"
              v-model:cartonOrigin="cartonOrigin"
              v-model:customSN="customSN"
              v-model:isSNManual="isSNManual"
              v-model:snPattern="snPattern"
              :suggestedSNValue="suggestedSNValue"
              :snPreview="snPreview"
              @back="resetSession"
              @focus-scan="focusScan"
            />

            <div v-if="isRescanMode" class="rescan-banner fade-in">
              <div class="rescan-info">
                <i class="fas fa-redo-alt fa-spin"></i>
                <span><strong>RESCAN MODE:</strong> Updating Carton <strong>{{ rescanCartonSN }}</strong></span>
              </div>
              <button @click="isRescanMode = false; rescanCartonSN = '';" class="btn-cancel-rescan">
                <i class="fas fa-times"></i> Cancel
              </button>
            </div>

            <div class="progress-container">
              <div class="progress-header">
                <span class="count">{{ scannedItems.length }} / {{ currentProduct.packed_qty }}</span>
                <span class="percent">{{ progressPercent }}%</span>
              </div>
              <div class="progress-bar"><div class="fill" :style="{ width: progressPercent + '%' }"></div></div>
            </div>

            <PrintStatusBanner
              :lastCarton="lastCarton"
              :agentErrorMessage="agentErrorMessage"
              @retry="finalizeCarton(true)"
            />

            <ScanBuffer
              ref="scanRef"
              v-model:scanBuffer="scanBuffer"
              :jobOrder="jobOrder"
              :awaitingNext="awaitingNext"
              :invalidScans="invalidScans"
              :overflowScans="overflowScans"
              :allowPartial="currentProduct && currentProduct.allow_partial === 1"
              :scannedCount="scannedItems.length"
              @scan="handleScan"
              @next-carton="startNextCarton"
              @pack-now="finalizeCarton()"
              @clear-invalid="invalidScans = []"
              @clear-overflow="overflowScans = []"
            />
          </div>

          <ScannedList
            :items="scannedItems"
            @clear="scannedItems = []"
          />
        </div>
      </section>
    </div>

    <Notification />
    <SettingsModal :show="showSettings" @close="showSettings = false" />
    <EmergencyReprintModal 
      :show="showEmergencyModal" 
      @close="showEmergencyModal = false" 
      @reprint="handleEmergencyReprint" 
      @rescan="handleRescan"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useSettingsStore } from '../core/stores/settings';
import { useSystemStore } from '../core/stores/system';
import { usePrintAgent } from '../features/print/composables/usePrintAgent';
import packingApi from '../features/packing/api';
import printApi from '../features/print/api';
import catalogApi from '../features/catalog/api';

import AppHeader from '../core/components/AppHeader.vue';
import Notification from '../core/components/Notification.vue';
import CatalogSelection from '../features/catalog/components/CatalogSelection.vue';
import SessionHeader from '../features/packing/components/SessionHeader.vue';
import ScanBuffer from '../features/packing/components/ScanBuffer.vue';
import ScannedList from '../features/packing/components/ScannedList.vue';
import PrintStatusBanner from '../features/print/components/PrintStatusBanner.vue';
import SettingsModal from '../features/settings/components/SettingsModal.vue';
import EmergencyReprintModal from '../features/print/components/EmergencyReprintModal.vue';

const settings = useSettingsStore();
const system = useSystemStore();
const { isAgentConnected, agentErrorMessage, checkAgentHealth, sendPrintJob } = usePrintAgent();

const currentProduct = ref(null);
const scannedItems = ref([]);
const scanBuffer = ref('');
const invalidScans = ref([]);
const lastCarton = ref(null);
const jobOrder = ref('');
const cartonOrigin = ref('VN');
const customSN = ref('');
const snPattern = ref('');
const awaitingNext = ref(false);
const suggestedSNValue = ref(0);
const backupScannedItems = ref([]);
const isProcessing = ref(false);
const overflowScans = ref([]);
const isAudioActive = ref(false);
const showSettings = ref(false);
const showEmergencyModal = ref(false);
const isRescanMode = ref(false);
const rescanCartonSN = ref('');
const isSNManual = ref(false);
let statusTimer = null;
let audioCtx = null;
let isAudioInitialized = false;

const initAudio = async () => {
  if (isAudioInitialized) return;
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (settings.audioDeviceId && audioCtx.setSinkId) {
      try { await audioCtx.setSinkId(settings.audioDeviceId); } catch {}
    }
    isAudioInitialized = true;
  } catch(e) {}
};

const snPreview = computed(() => {
  if (!currentProduct.value) return '';
  const now = new Date();
  const yy = String(now.getFullYear()).slice(-2);
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const seq = customSN.value || suggestedSNValue.value || '1';
  const prefix = `${currentProduct.value.start_part || ''}${yy}${mm}${currentProduct.value.middle_part || ''}`;
  return `${prefix}${String(seq).padStart(5, '0')}`;
});

const catalogRef = ref(null);
const sessionRef = ref(null);
const scanRef = ref(null);

const progressPercent = computed(() => {
  if (!currentProduct.value) return 0;
  return Math.round((scannedItems.value.length / currentProduct.value.packed_qty) * 100);
});

const focusScan = () => { nextTick(() => { if (scanRef.value) scanRef.value.focusScan(); }); initAudio(); };

const checkAgent = async () => {
  await checkAgentHealth();
  system.isAgentConnected = isAgentConnected.value;
  if (isAgentConnected.value) {
    if (system.notification?.text?.includes('OFFLINE')) system.clearNotification();
  } else {
    system.showNotification('CRITICAL: Print Agent is OFFLINE!', 'error', 0);
  }
};

const checkSystem = async () => {
  try {
    const res = await catalogApi.getCustomers();
    system.isOnline = true;
  } catch (e) { system.isOnline = false; }
};

const selectProduct = async (p) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = p;
  scannedItems.value = [];
  lastCarton.value = null;
  agentErrorMessage.value = '';
  customSN.value = '';
  isSNManual.value = false;
  suggestedSNValue.value = 0; // Reset to 0 to ensure the next fetch is accepted
  await refreshNextSN();
  try {
    const res = await packingApi.getLastCarton(p.id);
    if (res.data) {
      lastCarton.value = res.data;
      if (res.data.status === 'FAILED' && res.data.items) {
        backupScannedItems.value = res.data.items.map(i => i.item_sn);
        if (!jobOrder.value) jobOrder.value = res.data.job_order || '';
      }
    }
  } catch (err) { console.warn('Error fetching last carton:', err); }
  nextTick(() => {
    if (!jobOrder.value && sessionRef.value) sessionRef.value.focusJobOrder();
    else focusScan();
  });
};

const refreshNextSN = async () => {
  if (!currentProduct.value || isProcessing.value) return;
  try {
    const snRes = await packingApi.getNextSN(currentProduct.value.id);
    if (snRes.data?.next_seq) {
      const newSeq = snRes.data.next_seq;
      // Only update if the server has a newer (higher) number
      if (newSeq > suggestedSNValue.value) {
        // If user is following the suggestion, update their current S/N too
        if (!customSN.value || customSN.value === suggestedSNValue.value.toString()) {
          customSN.value = newSeq.toString();
        }
        suggestedSNValue.value = newSeq;
      }
    }
  } catch (err) { console.warn('Sync SN failed:', err); }
};

const handleScan = () => {
  const sn = scanBuffer.value.trim();
  if (!sn) return;

  // When box is already full (processing or awaiting next), capture overflow — DON'T block
  if (isProcessing.value || awaitingNext.value) {
    if (scannedItems.value.length >= currentProduct.value.packed_qty) {
      playScanAlert();
      overflowScans.value.push({ sn, time: new Date().toLocaleTimeString() });
      system.showNotification(`⚠️ BOX FULL — S/N captured: ${sn}`, 'warning');
      scanBuffer.value = '';
      return;
    }
    // Still processing but box not full yet (shouldn't happen, but guard)
    if (isProcessing.value) return;
  }

  if (!jobOrder.value) { system.showNotification('Please enter Job Order!', 'error'); return; }
  
  if (scannedItems.value.length >= currentProduct.value.packed_qty && !awaitingNext.value) {
    finalizeCarton();
    return;
  }

  // Strict check for Start S/N
  if (customSN.value && !isNaN(parseInt(customSN.value)) && parseInt(customSN.value) < suggestedSNValue.value) {
    system.showNotification(`INVALID START S/N: Must be at least ${suggestedSNValue.value}`, 'error');
    playScanAlert();
    return;
  }

  if (!isAgentConnected.value) { playScanAlert(); system.showNotification('CRITICAL: Agent OFFLINE!', 'error', 0); scanBuffer.value = ''; return; }

  // Lockdown only for real invalid scans (pattern, duplicate, lockdown) — NOT overflow/excess
  const hasRealInvalid = invalidScans.value.some(s => ['pattern', 'duplicate', 'lockdown'].includes(s.type));
  if (hasRealInvalid) { playScanAlert(); invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Station locked — clear errors first', type: 'lockdown' }); system.showNotification('STATION LOCKED! Clear errors first.', 'error'); scanBuffer.value = ''; return; }

  if (snPattern.value && !sn.startsWith(snPattern.value)) { playScanAlert(); invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Prefix mismatch', type: 'pattern' }); system.showNotification(`Invalid Pattern! Must start with "${snPattern.value}"`, 'error'); scanBuffer.value = ''; return; }
  if (scannedItems.value.includes(sn)) { playScanAlert(); invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Duplicate S/N', type: 'duplicate' }); system.showNotification(`Duplicate: ${sn}`, 'warning'); scanBuffer.value = ''; return; }
  scannedItems.value.push(sn);
  scanBuffer.value = '';
  if (scannedItems.value.length >= currentProduct.value.packed_qty) { finalizeCarton(); }
};

const finalizeCarton = async (isRetry = false) => {
  // Guard: prevent concurrent finalization (double-click / rapid Enter)
  if (isProcessing.value && !isRetry) return;
  isProcessing.value = true;
  agentErrorMessage.value = '';
  try {
    let cartonId, cartonSn, btxmlContent;
    if (isRetry && lastCarton.value) {
      cartonId = lastCarton.value.id; cartonSn = lastCarton.value.carton_sn; btxmlContent = lastCarton.value.btxml;
      lastCarton.value.status = 'PRINTING';
    } else if (isRescanMode.value) {
      const items = [...scannedItems.value];
      const res = await packingApi.rescanCarton({
        carton_sn: rescanCartonSN.value,
        items,
        template_path: settings.templatePath || null,
        printer_name: settings.printerName || null
      });
      cartonId = res.data.id;
      cartonSn = res.data.carton_sn;
      btxmlContent = res.data.btxml;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
    } else {
      if (customSN.value && !isNaN(parseInt(customSN.value)) && parseInt(customSN.value) < suggestedSNValue.value) {
        system.showNotification(`ERROR: Start S/N cannot be lower than ${suggestedSNValue.value}`, 'error'); isProcessing.value = false; return;
      }
      const items = [...scannedItems.value];
      if (items.length === 0) { system.showNotification('No items!', 'error'); isProcessing.value = false; return; }
      
      // Clear previous banner/status to avoid confusion with old SNs
      lastCarton.value = { status: 'PRINTING', carton_sn: snPreview.value };

      // Use null for custom_sn if in Auto mode to let backend assign atomically
      const finalCustomSN = isSNManual.value ? (customSN.value ? parseInt(customSN.value) : null) : null;

      const res = await packingApi.createCarton({ product_id: currentProduct.value.id, items, template_path: settings.templatePath || null, printer_name: settings.printerName || null, print_folder: settings.printFolder || null, job_order: jobOrder.value, custom_sn: finalCustomSN, carton_origin: cartonOrigin.value });
      cartonId = res.data.id; cartonSn = res.data.carton_sn; btxmlContent = res.data.btxml;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
      backupScannedItems.value = items;
    }
    const printResult = await handleClientPrint(btxmlContent, cartonSn, cartonId);
    if (printResult === 'Success') {
      await printApi.updateCartonStatus(cartonId, 'SUCCESS');
      lastCarton.value.status = 'SUCCESS';
      system.showNotification(`Carton ${cartonSn} Printed!`, 'success');
      
      // Update the suggestion base immediately from what was just assigned
      if (cartonSn) {
        const lastSeq = parseInt(cartonSn.slice(-5));
        if (!isNaN(lastSeq)) suggestedSNValue.value = lastSeq + 1;
      }

      if (!isRetry) { 
        if (!isRescanMode.value) {
          if (isSNManual.value && customSN.value && !isNaN(parseInt(customSN.value))) {
            customSN.value = (parseInt(customSN.value) + 1).toString(); 
          } else if (!isSNManual.value) {
            customSN.value = ''; // Keep empty to stay in AUTO mode
          }
        }
        awaitingNext.value = true; 
        focusScan(); 
      }
    } else { lastCarton.value.status = 'FAILED'; agentErrorMessage.value = printResult; system.showNotification(`Print failed: ${printResult}`, 'error'); }
  } catch (err) {
    console.error(err);
    if (lastCarton.value && !isRetry) lastCarton.value.status = 'FAILED';
    const msg = err.response?.data?.detail || 'Server error.';
    system.showNotification(msg, 'error');
    
    // If SN is already in use, refresh the suggestion
    if (err.response?.status === 400 && msg.includes('already in use')) {
      try {
        const snRes = await packingApi.getNextSN(currentProduct.value.id);
        if (snRes.data?.next_seq) {
          suggestedSNValue.value = snRes.data.next_seq;
          customSN.value = snRes.data.next_seq.toString();
          system.showNotification(`Suggested S/N updated to ${snRes.data.next_seq}`, 'warning');
        }
      } catch (e) {}
    }
  } finally { isProcessing.value = false; }
};

const handleClientPrint = async (content, cartonSn, cartonId) => {
  try {
    const agentRes = await fetch('http://127.0.0.1:1234/print', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify({ 
        xml: content, 
        filename: `print_job_${cartonSn}.xml`, 
        path: settings.printFolder || null,
        printer_name: settings.printerName || null
      }) 
    });
    isAgentConnected.value = true; system.isAgentConnected = true;
    return await agentRes.text();
  } catch (err) { isAgentConnected.value = false; system.isAgentConnected = false; return 'Error: Could not connect to Print Agent.'; }
};

const handleEmergencyReprint = async (result) => {
  try {
    const res = await printApi.reprintCarton(result.id, settings.templatePath, settings.printerName);
    const newCarton = res.data;
    if (!newCarton?.btxml) { system.showNotification('Could not generate reprint data.', 'error'); return; }
    const printResult = await handleClientPrint(newCarton.btxml, newCarton.carton_sn, newCarton.id);
    if (printResult === 'Success') { system.showNotification(`Reprint successful: ${result.carton_sn}`, 'success'); showEmergencyModal.value = false; }
    else system.showNotification('Reprint failed: ' + printResult, 'error');
  } catch (err) { system.showNotification('Reprint error: ' + (err.response?.data?.detail || err.message), 'error'); }
};

const handleRescan = (carton) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = carton.product;
  scannedItems.value = [];
  jobOrder.value = carton.job_order || '';
  cartonOrigin.value = carton.carton_origin || 'VN';
  isRescanMode.value = true;
  rescanCartonSN.value = carton.carton_sn;
  showEmergencyModal.value = false;
  system.showNotification(`RESCAN MODE ACTIVE for ${carton.carton_sn}`, 'warning');
  focusScan();
};

const startNextCarton = () => { 
  scannedItems.value = []; 
  invalidScans.value = []; 
  overflowScans.value = [];
  awaitingNext.value = false; 
  isRescanMode.value = false;
  rescanCartonSN.value = '';
  focusScan(); 
};
const resetSession = () => { currentProduct.value = null; scannedItems.value = []; invalidScans.value = []; overflowScans.value = []; awaitingNext.value = false; scanBuffer.value = ''; nextTick(() => { if (catalogRef.value) catalogRef.value.focusSearch(); }); };

const playScanAlert = () => {
  try {
    if (!audioCtx) return; // Silent fallback if not initialized
    if (audioCtx.state === 'suspended') audioCtx.resume(); // Don't await, let it play as soon as it resumes
    
    const beep = (freq, start, dur) => {
      const o = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      o.connect(g);
      g.connect(audioCtx.destination);
      o.type = 'square';
      o.frequency.setValueAtTime(freq, audioCtx.currentTime + start);
      
      // Sharp attack (0.005s) for instant sound, instead of slow 0.05s fade-in
      g.gain.setValueAtTime(0, audioCtx.currentTime + start);
      g.gain.linearRampToValueAtTime(1.0, audioCtx.currentTime + start + 0.005);
      g.gain.linearRampToValueAtTime(0, audioCtx.currentTime + start + dur);
      
      o.start(audioCtx.currentTime + start);
      o.stop(audioCtx.currentTime + start + dur);
    };
    beep(800, 0, 0.4); beep(800, 0.5, 0.4); beep(800, 1.0, 0.4);
  } catch (e) { console.warn('Audio alert failed:', e); }
};
const toggleAudio = () => { isAudioActive.value = true; initAudio().then(playScanAlert); system.showNotification('Audio Alert: ACTIVE', 'success'); };

// Detect manual SN entry
watch(customSN, (val) => {
  if (val && val !== suggestedSNValue.value.toString()) {
    isSNManual.value = true;
  }
});

// Session persistence
watch([jobOrder, cartonOrigin, currentProduct, scannedItems, customSN, snPattern, awaitingNext, suggestedSNValue, backupScannedItems, lastCarton, invalidScans, isSNManual, overflowScans], () => {
  sessionStorage.setItem('packingState', JSON.stringify({ jobOrder: jobOrder.value, cartonOrigin: cartonOrigin.value, currentProduct: currentProduct.value, scannedItems: scannedItems.value, customSN: customSN.value, snPattern: snPattern.value, awaitingNext: awaitingNext.value, suggestedSNValue: suggestedSNValue.value, backupScannedItems: backupScannedItems.value, lastCarton: lastCarton.value, invalidScans: invalidScans.value, isSNManual: isSNManual.value, overflowScans: overflowScans.value }));
}, { deep: true });

onMounted(() => {
  const saved = sessionStorage.getItem('packingState');
  if (saved) { try { const s = JSON.parse(saved); if (s.jobOrder) jobOrder.value = s.jobOrder; if (s.cartonOrigin) cartonOrigin.value = s.cartonOrigin; if (s.currentProduct) currentProduct.value = s.currentProduct; if (s.scannedItems) scannedItems.value = s.scannedItems; if (s.customSN) customSN.value = s.customSN; if (s.snPattern) snPattern.value = s.snPattern; if (s.awaitingNext !== undefined) awaitingNext.value = s.awaitingNext; if (s.suggestedSNValue !== undefined) suggestedSNValue.value = s.suggestedSNValue; if (s.backupScannedItems) backupScannedItems.value = s.backupScannedItems; if (s.lastCarton) lastCarton.value = s.lastCarton; if (s.invalidScans) invalidScans.value = s.invalidScans; if (s.overflowScans) overflowScans.value = s.overflowScans; } catch (e) { console.error('Restore failed', e); } }
  settings.loadSettings();
  checkAgent(); checkSystem();
  nextTick(() => { if (!currentProduct.value && catalogRef.value) catalogRef.value.focusSearch(); });
  statusTimer = setInterval(() => { checkAgent(); checkSystem(); refreshNextSN(); }, 3000);
  window.addEventListener('click', (e) => { if (showSettings.value || showEmergencyModal.value) return; if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return; focusScan(); });
});
onUnmounted(() => { if (statusTimer) clearInterval(statusTimer); });
</script>

<style scoped>
.packing-container { min-height: 100vh; background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); padding: 40px 20px; color: #1e293b; display: flex; justify-content: center; }
.glass-card { background: rgba(255,255,255,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.5); border-radius: 16px; padding: 12px 18px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.main-card { width: 95%; max-width: 1000px; background: white; transition: max-width 0.4s cubic-bezier(0.4,0,0.2,1); }
.main-card.wide-layout { max-width: 1500px; }
.packing-workspace { display: flex; gap: 32px; align-items: flex-start; }
.main-workspace { flex: 1; min-width: 0; }
.progress-container { margin-bottom: 20px; background: #f1f5f9; padding: 12px 20px; border-radius: 12px; }
.progress-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 600; }
.progress-bar { height: 12px; background: #e2e8f0; border-radius: 6px; overflow: hidden; }
.progress-bar .fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #10b981); transition: width 0.4s cubic-bezier(0.4,0,0.2,1); }
@media (max-width: 1100px) { .packing-workspace { flex-direction: column; align-items: stretch; } }
@media (max-width: 600px) { .packing-container { padding: 10px; } .main-card { padding: 12px; } }

.rescan-banner {
  background: #fff7ed;
  border: 1px solid #ffedd5;
  border-radius: 12px;
  padding: 12px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #9a3412;
}
.rescan-info { display: flex; align-items: center; gap: 12px; }
.rescan-info i { color: #f97316; }
.btn-cancel-rescan {
  background: #ffedd5;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  color: #9a3412;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
}
.btn-cancel-rescan:hover { background: #fed7aa; }
</style>
