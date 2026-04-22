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
              v-model:snPattern="snPattern"
              :suggestedSNValue="suggestedSNValue"
              :snPreview="snPreview"
              @back="resetSession"
              @focus-scan="focusScan"
            />

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
              @scan="handleScan"
              @next-carton="startNextCarton"
              @clear-invalid="invalidScans = []"
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
    <EmergencyReprintModal :show="showEmergencyModal" @close="showEmergencyModal = false" @reprint="handleEmergencyReprint" />
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
const isAudioActive = ref(false);
const showSettings = ref(false);
const showEmergencyModal = ref(false);
let statusTimer = null;

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

const focusScan = () => { nextTick(() => { if (scanRef.value) scanRef.value.focusScan(); }); };

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
  try {
    const snRes = await packingApi.getNextSN(p.id);
    if (snRes.data?.next_seq) { customSN.value = snRes.data.next_seq.toString(); suggestedSNValue.value = snRes.data.next_seq; }
  } catch (err) { console.warn('Error fetching next SN:', err); }
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

const handleScan = () => {
  if (!jobOrder.value) { system.showNotification('Please enter Job Order!', 'error'); return; }
  
  // Strict check for Start S/N
  if (customSN.value && !isNaN(parseInt(customSN.value)) && parseInt(customSN.value) < suggestedSNValue.value) {
    system.showNotification(`INVALID START S/N: Must be at least ${suggestedSNValue.value}`, 'error');
    playScanAlert();
    return;
  }

  const sn = scanBuffer.value.trim();
  if (!sn) return;
  if (!isAgentConnected.value) { system.showNotification('CRITICAL: Agent OFFLINE!', 'error', 0); playScanAlert(); scanBuffer.value = ''; return; }
  if (invalidScans.value.length > 0) { invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'invalid', type: 'lockdown' }); system.showNotification('STATION LOCKED!', 'error'); playScanAlert(); scanBuffer.value = ''; return; }
  if (awaitingNext.value) { invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Excess Scan (Box Full)', type: 'excess' }); system.showNotification('BOX FULL!', 'warning'); playScanAlert(); scanBuffer.value = ''; return; }
  if (snPattern.value && !sn.startsWith(snPattern.value)) { invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Prefix mismatch', type: 'pattern' }); system.showNotification(`Invalid Pattern! Must start with "${snPattern.value}"`, 'error'); playScanAlert(); scanBuffer.value = ''; return; }
  if (scannedItems.value.includes(sn)) { invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Duplicate S/N', type: 'duplicate' }); system.showNotification(`Duplicate: ${sn}`, 'warning'); playScanAlert(); scanBuffer.value = ''; return; }
  scannedItems.value.push(sn);
  scanBuffer.value = '';
  if (scannedItems.value.length >= currentProduct.value.packed_qty) { awaitingNext.value = true; finalizeCarton(); }
};

const finalizeCarton = async (isRetry = false) => {
  isProcessing.value = true;
  agentErrorMessage.value = '';
  try {
    let cartonId, cartonSn, btxmlContent;
    if (isRetry && lastCarton.value) {
      cartonId = lastCarton.value.id; cartonSn = lastCarton.value.carton_sn; btxmlContent = lastCarton.value.btxml;
      lastCarton.value.status = 'PRINTING';
    } else {
      if (customSN.value && !isNaN(parseInt(customSN.value)) && parseInt(customSN.value) < suggestedSNValue.value) {
        system.showNotification(`ERROR: Start S/N cannot be lower than ${suggestedSNValue.value}`, 'error'); isProcessing.value = false; return;
      }
      const items = [...scannedItems.value];
      if (items.length === 0) { system.showNotification('No items!', 'error'); isProcessing.value = false; return; }
      const res = await packingApi.createCarton({ product_id: currentProduct.value.id, items, template_path: settings.templatePath || null, printer_name: settings.printerName || null, print_folder: settings.printFolder || null, job_order: jobOrder.value, custom_sn: customSN.value ? parseInt(customSN.value) : null, carton_origin: cartonOrigin.value });
      cartonId = res.data.id; cartonSn = res.data.carton_sn; btxmlContent = res.data.btxml;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
      backupScannedItems.value = items;
    }
    const printResult = await handleClientPrint(btxmlContent, cartonSn, cartonId);
    if (printResult === 'Success') {
      await printApi.updateCartonStatus(cartonId, 'SUCCESS');
      lastCarton.value.status = 'SUCCESS';
      system.showNotification(`Carton ${cartonSn} Printed!`, 'success');
      if (!isRetry) { if (customSN.value && !isNaN(parseInt(customSN.value))) customSN.value = (parseInt(customSN.value) + 1).toString(); awaitingNext.value = true; focusScan(); }
    } else { lastCarton.value.status = 'FAILED'; agentErrorMessage.value = printResult; system.showNotification(`Print failed: ${printResult}`, 'error'); }
  } catch (err) { console.error(err); if (lastCarton.value && !isRetry) lastCarton.value.status = 'FAILED'; system.showNotification('Server error.', 'error'); }
  finally { isProcessing.value = false; }
};

const handleClientPrint = async (content, cartonSn, cartonId) => {
  try {
    const agentRes = await fetch('http://127.0.0.1:1234/print', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ xml: content, filename: `print_job_${cartonSn}.xml`, path: settings.printFolder || null }) });
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

const startNextCarton = () => { scannedItems.value = []; invalidScans.value = []; awaitingNext.value = false; focusScan(); };
const resetSession = () => { currentProduct.value = null; scannedItems.value = []; invalidScans.value = []; awaitingNext.value = false; scanBuffer.value = ''; nextTick(() => { if (catalogRef.value) catalogRef.value.focusSearch(); }); };

const playScanAlert = async () => {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (settings.audioDeviceId && ctx.setSinkId) { try { await ctx.setSinkId(settings.audioDeviceId); } catch {} }
    const beep = (freq, start, dur) => { const o = ctx.createOscillator(); const g = ctx.createGain(); o.connect(g); g.connect(ctx.destination); o.type = 'square'; o.frequency.setValueAtTime(freq, ctx.currentTime + start); g.gain.setValueAtTime(0, ctx.currentTime + start); g.gain.linearRampToValueAtTime(0.1, ctx.currentTime + start + 0.05); g.gain.linearRampToValueAtTime(0, ctx.currentTime + start + dur); o.start(ctx.currentTime + start); o.stop(ctx.currentTime + start + dur); };
    beep(150, 0, 0.4); beep(150, 0.5, 0.4); beep(150, 1.0, 0.4);
  } catch (e) { console.warn('Audio alert failed:', e); }
};
const toggleAudio = () => { isAudioActive.value = true; playScanAlert(); system.showNotification('Audio Alert: ACTIVE', 'success'); };

// Session persistence
watch([jobOrder, cartonOrigin, currentProduct, scannedItems, customSN, snPattern, awaitingNext, suggestedSNValue, backupScannedItems, lastCarton, invalidScans], () => {
  sessionStorage.setItem('packingState', JSON.stringify({ jobOrder: jobOrder.value, cartonOrigin: cartonOrigin.value, currentProduct: currentProduct.value, scannedItems: scannedItems.value, customSN: customSN.value, snPattern: snPattern.value, awaitingNext: awaitingNext.value, suggestedSNValue: suggestedSNValue.value, backupScannedItems: backupScannedItems.value, lastCarton: lastCarton.value, invalidScans: invalidScans.value }));
}, { deep: true });

onMounted(() => {
  const saved = sessionStorage.getItem('packingState');
  if (saved) { try { const s = JSON.parse(saved); if (s.jobOrder) jobOrder.value = s.jobOrder; if (s.cartonOrigin) cartonOrigin.value = s.cartonOrigin; if (s.currentProduct) currentProduct.value = s.currentProduct; if (s.scannedItems) scannedItems.value = s.scannedItems; if (s.customSN) customSN.value = s.customSN; if (s.snPattern) snPattern.value = s.snPattern; if (s.awaitingNext !== undefined) awaitingNext.value = s.awaitingNext; if (s.suggestedSNValue !== undefined) suggestedSNValue.value = s.suggestedSNValue; if (s.backupScannedItems) backupScannedItems.value = s.backupScannedItems; if (s.lastCarton) lastCarton.value = s.lastCarton; if (s.invalidScans) invalidScans.value = s.invalidScans; } catch (e) { console.error('Restore failed', e); } }
  settings.loadSettings();
  checkAgent(); checkSystem();
  nextTick(() => { if (!currentProduct.value && catalogRef.value) catalogRef.value.focusSearch(); });
  statusTimer = setInterval(() => { checkAgent(); checkSystem(); }, 5000);
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
</style>
