<template>
  <div class="packing-container">
    <div class="glass-card main-card" :class="{ 'wide-layout': currentProduct }">
      <AppHeader
        :isAudioActive="isAudioActive"

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
              v-model:customYYMM="customYYMM"
              :suggestedSNValue="suggestedSNValue"
              :snPreview="snPreview"
              :snExists="snExists"
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
              <!-- Cảnh báo Agent Offline (Chỉ hiện khi ở chế độ Local) -->
              <div v-if="settings.printMode === 'local' && !agentConnected" class="agent-offline-banner fade-in">
                <div class="banner-content">
                  <i class="fas fa-exclamation-triangle fa-beat"></i>
                  <span><strong>AGENT OFFLINE:</strong> Vui lòng bật <code>agent.py</code> để bắt đầu quét hàng.</span>
                </div>
              </div>

              <!-- Cảnh báo Thiếu File Tem -->
              <div v-if="settings.printMode === 'local' && agentConnected && templateMissing" class="agent-offline-banner template-missing-banner fade-in">
                <div class="banner-content">
                  <i class="fas fa-file-circle-exclamation fa-beat"></i>
                  <span><strong>THIẾU FILE TEM:</strong> Không tìm thấy <code>{{ templateFilename }}</code> trong thư mục cục bộ.</span>
                </div>
              </div>

              <div class="progress-header">
                <span class="count">{{ scannedItems.length }} / {{ currentProduct?.packed_qty || 0 }}</span>
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
              :disabled="isProcessing || (settings.printMode === 'local' && (!agentConnected || templateMissing))"
              :placeholder="(settings.printMode === 'local' && !agentConnected) ? 'AGENT OFFLINE' : (templateMissing ? 'THIẾU FILE TEM' : 'Scan S/N here...')"
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
import packingApi from '../features/packing/api';
import printApi from '../features/print/api';
import catalogApi from '../features/catalog/api';

import AppHeader from '../core/components/AppHeader.vue';
import CatalogSelection from '../features/catalog/components/CatalogSelection.vue';
import SessionHeader from '../features/packing/components/SessionHeader.vue';
import ScanBuffer from '../features/packing/components/ScanBuffer.vue';
import ScannedList from '../features/packing/components/ScannedList.vue';
import PrintStatusBanner from '../features/print/components/PrintStatusBanner.vue';
import SettingsModal from '../features/settings/components/SettingsModal.vue';
import EmergencyReprintModal from '../features/print/components/EmergencyReprintModal.vue';

const system = useSystemStore();
const settings = useSettingsStore();

const agentConnected = ref(true); // Mặc định coi là connected để không bị nháy đỏ lúc đầu
const templateMissing = ref(false);
const templateFilename = ref('');
let agentCheckInterval = null;

const checkTemplateExists = async () => {
  if (settings.printMode !== 'local' || !agentConnected.value || !currentProduct.value) {
    templateMissing.value = false;
    return;
  }
  
  // Lấy tên file từ đường dẫn (Server có thể gửi đường dẫn đầy đủ, ta chỉ lấy tên file)
  const fullPath = currentProduct.value.template_path || 'carton.ui.btw';
  const filename = fullPath.split(/[\\/]/).pop();
  templateFilename.value = filename;

  try {
    const url = `${settings.agentUrl}/check-file?folder=${encodeURIComponent(settings.localTemplateDir)}&filename=${encodeURIComponent(filename)}`;
    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      templateMissing.value = !data.exists;
    }
  } catch (err) {
    templateMissing.value = false;
  }
};

const checkAgentHealth = async () => {
  if (settings.printMode !== 'local') {
    agentConnected.value = true;
    templateMissing.value = false;
    return;
  }
  try {
    // Tăng timeout lên 6000ms để không bị báo lỗi "ảo" khi Agent đang bận xử lý in (COM block event loop)
    const resp = await fetch(`${settings.agentUrl}/status`, { signal: AbortSignal.timeout(6000) });
    agentConnected.value = resp.ok;
    if (agentConnected.value) {
      await checkTemplateExists();
    }
  } catch (err) {
    agentConnected.value = false;
  }
};
const agentErrorMessage = ref('');

const currentProduct = ref(null);
const scannedItems = ref([]);
const scanBuffer = ref('');
const invalidScans = ref([]);
const lastCarton = ref(null);
const jobOrder = ref('');
const cartonOrigin = ref('VN');
const customSN = ref('');
const snPattern = ref('');
const customYYMM = ref('');
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
const snExists = ref(false);
let snCheckTimer = null;
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
  
  let yymm = '';
  if (customYYMM.value && customYYMM.value.length === 4) {
    yymm = customYYMM.value;
  } else {
    const now = new Date();
    const yy = String(now.getFullYear()).slice(-2);
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    yymm = `${yy}${mm}`;
  }

  const seq = customSN.value || suggestedSNValue.value || '1';
  const prefix = `${currentProduct.value.start_part || ''}${yymm}${currentProduct.value.middle_part || ''}`;
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

// Agent now integrated into backend

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
  isRescanMode.value = false;
  rescanCartonSN.value = '';
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
  await checkTemplateExists();
};

const refreshNextSN = async () => {
  if (!currentProduct.value || isProcessing.value) return;
  try {
    const snRes = await packingApi.getNextSN(currentProduct.value.id);
    if (snRes.data?.next_seq) {
      const newSeq = snRes.data.next_seq;
      // Update the reference suggested value regardless of mode
      if (newSeq > suggestedSNValue.value) {
        suggestedSNValue.value = newSeq;
        
        // ONLY auto-update the input field if we are in AUTO mode
        if (!isSNManual.value) {
          customSN.value = newSeq.toString();
        }
      }
    }
  } catch (err) { console.warn('Sync SN failed:', err); }
};

const processSingleScan = (sn) => {
  if (!sn) return;

  // When box is already full (processing or awaiting next), capture overflow
  if (isProcessing.value || awaitingNext.value) {
    if (scannedItems.value.length >= currentProduct.value.packed_qty) {
      playScanAlert();
      overflowScans.value.push({ sn, time: new Date().toLocaleTimeString() });
      system.showNotification(`⚠️ BOX FULL — S/N captured: ${sn}`, 'warning');
      return;
    }
    if (isProcessing.value) return;
  }

  if (!jobOrder.value) { system.showNotification('Please enter Job Order!', 'error'); return; }

  const hasRealInvalid = invalidScans.value.some(s => ['pattern', 'duplicate', 'lockdown'].includes(s.type));
  if (hasRealInvalid) { 
    playScanAlert(); 
    invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Station locked — clear errors first', type: 'lockdown' }); 
    system.showNotification('STATION LOCKED!', 'error'); 
    return; 
  }

  if (snPattern.value && !sn.startsWith(snPattern.value)) { 
    playScanAlert(); 
    invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Prefix mismatch', type: 'pattern' }); 
    system.showNotification(`Invalid Pattern: ${sn}`, 'error'); 
    return; 
  }
  
  if (scannedItems.value.includes(sn)) { 
    playScanAlert(); 
    invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Duplicate S/N', type: 'duplicate' }); 
    system.showNotification(`Duplicate: ${sn}`, 'warning'); 
    return; 
  }

  scannedItems.value.push(sn);
  if (scannedItems.value.length >= currentProduct.value.packed_qty) { 
    finalizeCarton(); 
  }
};

const handleScan = () => {
  const rawInput = scanBuffer.value.trim();
  if (!rawInput) return;

  // Split by newlines, tabs, or commas. Spaces WITHIN S/Ns are preserved.
  const sns = rawInput.split(/[\n\r\t,]+/).map(s => s.trim()).filter(s => s.length > 0);
  
  if (sns.length === 0) return;

  // Process each S/N in the batch
  sns.forEach(sn => processSingleScan(sn));
  
  scanBuffer.value = '';
};

const finalizeCarton = async (isRetry = false) => {
  // Guard: prevent concurrent finalization (double-click / rapid Enter)
  if (isProcessing.value && !isRetry) return;
  isProcessing.value = true;
  agentErrorMessage.value = '';
  try {
    let cartonId, cartonSn, btxmlContent;
    if (isRetry && lastCarton.value) {
      const res = await printApi.reprintCarton(
        lastCarton.value.id, 
        settings.templatePath || null, 
        settings.printerName
      );
      cartonId = res.data.id;
      cartonSn = res.data.carton_sn;
      btxmlContent = res.data.btxml;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
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
      if (snExists.value) {
        system.showNotification('S/N already exists! Please use a different number.', 'error');
        isProcessing.value = false;
        return;
      }
      const items = [...scannedItems.value];
      if (items.length === 0) { system.showNotification('No items!', 'error'); isProcessing.value = false; return; }
      
      // Clear previous banner/status to avoid confusion with old SNs
      lastCarton.value = { status: 'PRINTING', carton_sn: snPreview.value };

      // Use null for custom_sn if in Auto mode to let backend assign atomically
      const finalCustomSN = isSNManual.value ? (customSN.value ? parseInt(customSN.value) : null) : null;

      const res = await packingApi.createCarton({ 
        product_id: currentProduct.value.id, 
        items, 
        template_path: settings.templatePath || null, 
        printer_name: settings.printerName || null, 
        print_folder: settings.printFolder || null, 
        job_order: jobOrder.value, 
        custom_sn: finalCustomSN, 
        custom_yymm: customYYMM.value || null,
        carton_origin: cartonOrigin.value,
        station_id: system.stationId 
      });
      cartonId = res.data.id; cartonSn = res.data.carton_sn; btxmlContent = res.data.btxml;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
      backupScannedItems.value = items;
    }
    // In tập trung hoặc Local Agent dựa trên cấu hình
    const printResult = await handlePrintExecution(cartonId, cartonSn);
    if (printResult === 'Success') {
      lastCarton.value.status = 'SUCCESS';
      system.showNotification(`Carton ${cartonSn} Printed!`, 'success');
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

/** Gửi lệnh in (Tự động chọn giữa Server-side hoặc Local Agent) */
const handlePrintExecution = async (cartonId, cartonSn) => {
  try {
    if (settings.printMode === 'local') {
      // 1. Lấy BTXML từ server trước
      const resXml = await printApi.download_carton_btxml(cartonId);
      const xmlContent = resXml.data;
      
      // 2. Gửi sang Agent cục bộ
      const result = await printApi.agentPrint(
        settings.agentUrl, 
        xmlContent, 
        settings.printerName,
        settings.localTemplateDir
      );
      
      if (result.success) {
        // Cập nhật trạng thái thành công trên server
        await printApi.updateCartonStatus(cartonId, 'SUCCESS');
        return 'Success';
      } else {
        return result.message || 'Agent failed to print';
      }
    } else {
      // Chế độ in tập trung (Centralized)
      const res = await printApi.serverPrint(
        cartonId,
        settings.printerName || null,
        settings.templatePath || null
      );
      if (res.data?.success) {
        if (res.data.type === 'pdf' && res.data.data) {
          // Nhận PDF thật từ Server
          const byteChars = atob(res.data.data);
          const byteNums = new Array(byteChars.length);
          for (let i = 0; i < byteChars.length; i++) byteNums[i] = byteChars.charCodeAt(i);
          const blob = new Blob([new Uint8Array(byteNums)], { type: 'application/pdf' });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `label_${cartonSn}.pdf`;
          link.click();
          window.URL.revokeObjectURL(url);
          system.showNotification('PDF label downloaded!', 'success');
        }
        return 'Success';
      } else {
        return res.data?.message || 'Server print failed';
      }
    }
  } catch (err) {
    console.error('Print Execution Error:', err);
    return err.response?.data?.detail || err.message || 'Print connection error.';
  }
};



const handleEmergencyReprint = async (result) => {
  try {
    const res = await printApi.reprintCarton(result.id, settings.templatePath || null, settings.printerName);
    const newCarton = res.data;
    if (!newCarton?.btxml) { system.showNotification('Could not generate reprint data.', 'error'); return; }
    
    const printResult = await handlePrintExecution(newCarton.id, newCarton.carton_sn);
    if (printResult === 'Success') { 
      system.showNotification(`Reprint successful: ${result.carton_sn}`, 'success'); 
      showEmergencyModal.value = false; 
    }
    else system.showNotification('Reprint failed: ' + printResult, 'error');
  } catch (err) { system.showNotification('Reprint error: ' + (err.response?.data?.detail || err.message), 'error'); }
};

const handleRescan = (carton) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = carton.product;
  scannedItems.value = [];
  invalidScans.value = [];
  overflowScans.value = [];
  awaitingNext.value = false;
  lastCarton.value = null;
  agentErrorMessage.value = '';
  customSN.value = '';
  snPattern.value = ''; // Reset pattern as it's product-specific
  
  jobOrder.value = carton.job_order || '';
  cartonOrigin.value = carton.carton_origin || 'VN';
  isRescanMode.value = true;
  rescanCartonSN.value = carton.carton_sn;
  showEmergencyModal.value = false;
  system.showNotification(`RESCAN MODE ACTIVE for ${carton.carton_sn}`, 'warning');
  checkAgentHealth();
  agentCheckInterval = setInterval(checkAgentHealth, 5000);
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
const resetSession = () => { 
  currentProduct.value = null; 
  scannedItems.value = []; 
  invalidScans.value = []; 
  overflowScans.value = []; 
  awaitingNext.value = false; 
  isRescanMode.value = false;
  rescanCartonSN.value = '';
  scanBuffer.value = ''; 
  nextTick(() => { if (catalogRef.value) catalogRef.value.focusSearch(); }); 
};

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

watch(snPreview, (newVal) => {
  if (!newVal || !isSNManual.value || isRescanMode.value) {
    snExists.value = false;
    return;
  }
  if (snCheckTimer) clearTimeout(snCheckTimer);
  snCheckTimer = setTimeout(async () => {
    try {
      // Use existing searchCarton API to check if this SN is already taken
      const res = await printApi.searchCarton(newVal);
      snExists.value = !!res.data;
    } catch (e) {
      snExists.value = false;
    }
  }, 500);
});

// Session persistence
watch([jobOrder, cartonOrigin, currentProduct, scannedItems, customSN, snPattern, awaitingNext, suggestedSNValue, backupScannedItems, lastCarton, invalidScans, isSNManual, overflowScans, isRescanMode, rescanCartonSN], () => {
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
    invalidScans: invalidScans.value, 
    isSNManual: isSNManual.value, 
    overflowScans: overflowScans.value,
    isRescanMode: isRescanMode.value,
    rescanCartonSN: rescanCartonSN.value
  }));
}, { deep: true });

onMounted(() => {
  const saved = sessionStorage.getItem('packingState');
  if (saved) { 
    try { 
      const s = JSON.parse(saved); 
      if (s.jobOrder) jobOrder.value = s.jobOrder; 
      if (s.cartonOrigin) cartonOrigin.value = s.cartonOrigin; 
      if (s.currentProduct) currentProduct.value = s.currentProduct; 
      if (s.scannedItems) scannedItems.value = s.scannedItems; 
      if (s.customSN) customSN.value = s.customSN; 
      if (s.snPattern) snPattern.value = s.snPattern; 
      if (s.awaitingNext !== undefined) awaitingNext.value = s.awaitingNext; 
      if (s.suggestedSNValue !== undefined) suggestedSNValue.value = s.suggestedSNValue; 
      if (s.backupScannedItems) backupScannedItems.value = s.backupScannedItems; 
      if (s.lastCarton) lastCarton.value = s.lastCarton; 
      if (s.invalidScans) invalidScans.value = s.invalidScans; 
      if (s.overflowScans) overflowScans.value = s.overflowScans; 
      if (s.isRescanMode !== undefined) isRescanMode.value = s.isRescanMode;
      if (s.rescanCartonSN) rescanCartonSN.value = s.rescanCartonSN;
    } catch (e) { console.error('Restore failed', e); } 
  }
  settings.loadSettings();
  checkSystem();
  checkAgentHealth();
  nextTick(() => { if (!currentProduct.value && catalogRef.value) catalogRef.value.focusSearch(); });
  statusTimer = setInterval(() => { checkSystem(); refreshNextSN(); }, 3000);
  agentCheckInterval = setInterval(checkAgentHealth, 5000);
  window.addEventListener('click', (e) => { if (showSettings.value || showEmergencyModal.value) return; if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return; focusScan(); });
});
onUnmounted(() => { 
  if (statusTimer) clearInterval(statusTimer); 
  if (agentCheckInterval) clearInterval(agentCheckInterval);
});
</script>

<style scoped>
.packing-container { 
  min-height: 100vh; 
  padding: 24px; 
  color: #1e293b; 
  display: flex; 
  justify-content: center; 
  background: radial-gradient(circle at top right, #f8fafc, #f1f5f9); 
}
.glass-card { 
  background: rgba(255, 255, 255, 0.95); 
  backdrop-filter: blur(16px); 
  border: 1px solid rgba(255, 255, 255, 0.8); 
  border-radius: 24px; 
  padding: 24px; 
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02); 
}
.main-card { 
  width: 100%; 
  max-width: 1100px; 
  transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1); 
  display: flex;
  flex-direction: column;
}
.main-card.wide-layout { max-width: 1550px; }
.packing-workspace { 
  display: flex; 
  gap: 40px; 
  align-items: flex-start; 
  margin-top: 10px;
}
.main-workspace { flex: 1.4; min-width: 0; }
.progress-container { 
  margin-bottom: 24px; 
  background: #ffffff; 
  padding: 16px 24px; 
  border-radius: 20px; 
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
  border: 1px solid #f1f5f9;
}
.progress-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-end;
  margin-bottom: 12px; 
}
.progress-header .count {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}
.progress-header .percent {
  font-size: 0.9rem;
  color: #3b82f6;
  font-weight: 700;
  background: #eff6ff;
  padding: 4px 10px;
  border-radius: 8px;
}
.progress-bar { 
  height: 14px; 
  background: #f1f5f9; 
  border-radius: 10px; 
  overflow: hidden; 
  position: relative;
}
.progress-bar .fill { 
  height: 100%; 
  background: linear-gradient(90deg, #3b82f6, #10b981); 
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); 
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}
@media (max-width: 1280px) {
  .packing-workspace { gap: 24px; }
}
@media (max-width: 1000px) { 
  .packing-workspace { flex-direction: column; align-items: stretch; } 
  .main-card { padding: 16px; border-radius: 16px; }
}
@media (max-width: 600px) { 
  .packing-container { padding: 8px; } 
  .main-card { border-radius: 12px; } 
}

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

/* Agent Offline Banner */
.agent-offline-banner {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border: 2px solid #ef4444;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);
  animation: fadeIn 0.4s ease-out;
}
.banner-content {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #b91c1c;
}
.banner-content i {
  font-size: 1.5rem;
  color: #ef4444;
}
.banner-content span {
  font-size: 0.95rem;
}
.banner-content code {
  background: #fca5a5;
  padding: 2px 6px;
  border-radius: 4px;
  color: #7f1d1d;
  font-weight: bold;
}
@keyframes fadeIn { 
  from { opacity: 0; transform: translateY(-10px); } 
  to { opacity: 1; transform: translateY(0); } 
}
.template-missing-banner {
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  border: 2px solid #f97316;
}
.template-missing-banner .banner-content {
  color: #c2410c;
}
.template-missing-banner .banner-content i {
  color: #f97316;
}
</style>
