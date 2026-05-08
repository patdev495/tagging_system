<template>
  <div class="min-h-screen p-3 md:p-4 text-slate-800 flex justify-center bg-radial-at-tr from-slate-50 to-slate-200">
    <div class="w-full max-w-[1100px] transition-all duration-500 ease-out flex flex-col bg-white/95 backdrop-blur-2xl border border-white/80 rounded-[20px] p-4 shadow-2xl shadow-slate-900/5" :class="{ 'max-w-[1550px]': currentProduct }">
      <AppHeader
        :isAudioActive="isAudioActive"
        @toggle-audio="toggleAudio"
        @show-emergency="showEmergencyModal = true"
        @show-settings="showSettings = true"
        @home="resetSession"
      />

      <CatalogSelection
        v-if="!currentProduct"
        ref="catalogRef"
        @select-product="selectProduct"
      />

      <section class="mt-2.5" v-else>
        <div class="flex flex-col xl:flex-row gap-6 items-stretch xl:items-start">
          <div class="flex-[1.4] min-w-0">
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

            <div v-if="isRescanMode" class="bg-orange-50 border border-orange-100 rounded-xl p-2.5 md:p-4 mb-4 flex justify-between items-center text-orange-900 animate-in">
              <div class="flex items-center gap-3">
                <i class="fas fa-redo-alt fa-spin text-orange-500"></i>
                <span><strong>{{ t('packing.rescan_mode', { sn: rescanCartonSN }) }}</strong></span>
              </div>
              <button @click="isRescanMode = false; rescanCartonSN = '';" class="bg-orange-100 border-none px-3 py-1.5 rounded-lg text-orange-900 font-semibold cursor-pointer transition-colors hover:bg-orange-200 flex items-center gap-1.5 text-[0.85rem]">
                <i class="fas fa-times"></i> {{ t('packing.cancel') }}
              </button>
            </div>

            <div class="mb-4 bg-white p-3 md:p-4 rounded-2xl shadow-inner-sm border border-slate-100">
              <!-- Cảnh báo Agent Offline (Chỉ hiện khi ở chế độ Local) -->
              <div v-if="settings.printMode === 'local' && !agentConnected" class="bg-linear-to-br from-rose-50 to-rose-100 border-2 border-rose-500 rounded-xl p-3 md:p-4 mb-4 shadow-md shadow-rose-500/10 animate-in">
                <div class="flex items-center gap-3 text-rose-800">
                  <i class="fas fa-exclamation-triangle fa-beat text-[1.5rem] text-rose-500"></i>
                  <span class="text-[0.95rem]"><strong>{{ t('packing.agent_offline') }}</strong></span>
                </div>
              </div>

              <!-- Cảnh báo Thiếu File Tem -->
              <div v-if="settings.printMode === 'local' && agentConnected && templateMissing" class="bg-linear-to-br from-orange-50 to-orange-100 border-2 border-orange-500 rounded-xl p-3 md:p-4 mb-4 shadow-md shadow-orange-500/10 animate-in">
                <div class="flex items-center gap-3 text-orange-800">
                  <i class="fas fa-file-circle-exclamation fa-beat text-[1.5rem] text-orange-500"></i>
                  <span class="text-[0.95rem]"><strong>{{ t('packing.template_missing', { file: templateFilename }) }}</strong></span>
                </div>
              </div>

              <div class="flex justify-between items-end mb-2">
                <span class="text-[1.25rem] font-extrabold text-slate-900">{{ scannedItems.length }} / {{ currentProduct?.packed_qty || 0 }}</span>
                <span class="text-[0.9rem] text-blue-600 font-bold bg-blue-50 px-2.5 py-1 rounded-lg">{{ progressPercent }}%</span>
              </div>
              <div class="h-3.5 bg-slate-100 rounded-full overflow-hidden relative">
                <div class="h-full bg-linear-to-r from-blue-500 to-emerald-500 transition-all duration-600 ease-out shadow-[0_0_10px_rgba(59,130,246,0.3)]" :style="{ width: progressPercent + '%' }"></div>
              </div>
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
              :placeholder="(settings.printMode === 'local' && !agentConnected) ? t('packing.scan_placeholder_offline') : (templateMissing ? t('packing.scan_placeholder_missing') : t('packing.scan_placeholder'))"
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

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSettingsStore } from '../core/stores/settings';
import { useSystemStore } from '../core/stores/system';
import packingApi from '../features/packing/api';
import printApi from '../features/print/api';
import catalogApi from '../features/catalog/api';
import type { Product, Carton } from '../types/api';

import AppHeader from '../core/components/AppHeader.vue';
import CatalogSelection from '../features/catalog/components/CatalogSelection.vue';
import SessionHeader from '../features/packing/components/SessionHeader.vue';
import ScanBuffer from '../features/packing/components/ScanBuffer.vue';
import ScannedList from '../features/packing/components/ScannedList.vue';
import PrintStatusBanner from '../features/print/components/PrintStatusBanner.vue';
import SettingsModal from '../features/settings/components/SettingsModal.vue';
import EmergencyReprintModal from '../features/print/components/EmergencyReprintModal.vue';

const { t } = useI18n();
const system = useSystemStore();
const settings = useSettingsStore();

const agentConnected = ref<boolean>(true);
const templateMissing = ref<boolean>(false);
const templateFilename = ref<string>('');
let agentCheckInterval: ReturnType<typeof setInterval> | null = null;

const checkTemplateExists = async () => {
  if (settings.printMode !== 'local' || !agentConnected.value || !currentProduct.value) {
    templateMissing.value = false;
    return;
  }
  
  const fullPath = currentProduct.value.template_path || 'carton.ui.btw';
  const filename = fullPath.split(/[\\/]/).pop() || 'carton.ui.btw';
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
    // @ts-ignore
    const resp = await fetch(`${settings.agentUrl}/status`, { signal: AbortSignal.timeout ? AbortSignal.timeout(6000) : undefined });
    agentConnected.value = resp.ok;
    if (agentConnected.value) {
      await checkTemplateExists();
    }
  } catch (err) {
    agentConnected.value = false;
  }
};
const agentErrorMessage = ref<string>('');

const currentProduct = ref<Product | null>(null);
const scannedItems = ref<string[]>([]);
const scanBuffer = ref<string>('');

interface InvalidScan {
  sn: string;
  time: string;
  reason: string;
  type: 'pattern' | 'duplicate' | 'lockdown';
}

interface OverflowScan {
  sn: string;
  time: string;
}

const invalidScans = ref<InvalidScan[]>([]);
const lastCarton = ref<(Carton & { status?: string, items?: { item_sn: string }[] }) | null>(null);
const jobOrder = ref<string>('');
const cartonOrigin = ref<string>('VN');
const customSN = ref<string>('');
const snPattern = ref<string>('');
const customYYMM = ref<string>('');
const awaitingNext = ref<boolean>(false);
const suggestedSNValue = ref<number>(1);
const backupScannedItems = ref<string[]>([]);
const isProcessing = ref<boolean>(false);
const overflowScans = ref<OverflowScan[]>([]);
const isAudioActive = ref<boolean>(false);
const showSettings = ref<boolean>(false);
const showEmergencyModal = ref<boolean>(false);
const isRescanMode = ref<boolean>(false);
const rescanCartonSN = ref<string>('');
const isSNManual = ref<boolean>(false);
const snExists = ref<boolean>(false);
let snCheckTimer: ReturnType<typeof setTimeout> | null = null;
let statusTimer: ReturnType<typeof setInterval> | null = null;
let audioCtx: AudioContext | null = null;
let isAudioInitialized = false;

const initAudio = async () => {
  if (isAudioInitialized) return;
  try {
    audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    if (settings.audioDeviceId && (audioCtx as any).setSinkId) {
      try { await (audioCtx as any).setSinkId(settings.audioDeviceId); } catch {}
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

const catalogRef = ref<InstanceType<typeof CatalogSelection> | null>(null);
const sessionRef = ref<InstanceType<typeof SessionHeader> | null>(null);
const scanRef = ref<InstanceType<typeof ScanBuffer> | null>(null);

const progressPercent = computed(() => {
  if (!currentProduct.value) return 0;
  return Math.round((scannedItems.value.length / currentProduct.value.packed_qty) * 100);
});

const focusScan = () => { nextTick(() => { if (scanRef.value) scanRef.value.focusScan(); }); initAudio(); };

const checkSystem = async () => {
  try {
    await catalogApi.getCustomers();
    system.isOnline = true;
  } catch (e) { system.isOnline = false; }
};

const selectProduct = async (p: Product) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = p;
  scannedItems.value = [];
  lastCarton.value = null;
  agentErrorMessage.value = '';
  customSN.value = '';
  isSNManual.value = false;
  suggestedSNValue.value = 1;
  isRescanMode.value = false;
  rescanCartonSN.value = '';
  await refreshNextSN();
  try {
    const res = await packingApi.getLastCarton(p.id);
    if (res.data) {
      lastCarton.value = res.data;
      if (res.data.status === 'FAILED' && res.data.items) {
        backupScannedItems.value = res.data.items.map((i: any) => i.item_sn);
        if (!jobOrder.value) jobOrder.value = (res.data as any).job_order || '';
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
    const snRes = await packingApi.getNextSN(currentProduct.value.id, customYYMM.value);
    const data = snRes.data as any;
    const newSeq = data.next_seq || (data.next_sn ? parseInt(data.next_sn.match(/\d{5}$/)?.[0] || '0') : 1);
    
    if (newSeq) {
      suggestedSNValue.value = newSeq;
      if (!isSNManual.value) {
        customSN.value = newSeq.toString();
      }
    }
  } catch (err) { console.warn('Sync SN failed:', err); }
};

const processSingleScan = (sn: string) => {
  if (!sn || !currentProduct.value) return;

  if (isProcessing.value || awaitingNext.value) {
    if (scannedItems.value.length >= currentProduct.value.packed_qty) {
      playScanAlert();
      overflowScans.value.push({ sn, time: new Date().toLocaleTimeString() });
      system.showNotification(t('packing.box_full', { sn }), 'warning');
      return;
    }
    if (isProcessing.value) return;
  }

  if (!jobOrder.value) { system.showNotification(t('packing.enter_job_order'), 'error'); return; }

  const hasRealInvalid = invalidScans.value.some(s => ['pattern', 'duplicate', 'lockdown'].includes(s.type));
  if (hasRealInvalid) { 
    playScanAlert(); 
    invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Station locked — clear errors first', type: 'lockdown' }); 
    system.showNotification(t('packing.station_locked'), 'error'); 
    return; 
  }

  if (snPattern.value && !sn.startsWith(snPattern.value)) { 
    playScanAlert(); 
    invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Prefix mismatch', type: 'pattern' }); 
    system.showNotification(t('packing.prefix_mismatch', { sn }), 'error'); 
    return; 
  }
  
  if (scannedItems.value.includes(sn)) { 
    playScanAlert(); 
    invalidScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Duplicate S/N', type: 'duplicate' }); 
    system.showNotification(t('packing.duplicate_sn'), 'warning'); 
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

  const sns = rawInput.split(/[\n\r\t,]+/).map(s => s.trim()).filter(s => s.length > 0);
  
  if (sns.length === 0) return;

  sns.forEach(sn => processSingleScan(sn));
  
  scanBuffer.value = '';
};

const finalizeCarton = async (isRetry = false) => {
  if (!currentProduct.value) return;
  if (isProcessing.value && !isRetry) return;
  isProcessing.value = true;
  agentErrorMessage.value = '';
  try {
    let cartonId: number, cartonSn: string;
    if (isRetry && lastCarton.value?.id) {
      const res = await printApi.reprintCarton(
        lastCarton.value.id, 
        settings.templatePath || '', 
        settings.printerName
      );
      cartonId = res.data.id;
      cartonSn = res.data.carton_sn;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
    } else if (isRescanMode.value && rescanCartonSN.value) {
      const items = [...scannedItems.value];
      const res = await packingApi.rescanCarton({
        carton_sn: rescanCartonSN.value,
        items: items
      });
      cartonId = res.data.id;
      cartonSn = res.data.carton_sn;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
    } else {
      if (snExists.value) {
        system.showNotification(t('packing.sn_exists'), 'error');
        isProcessing.value = false;
        return;
      }
      const items = [...scannedItems.value];
      if (items.length === 0) { system.showNotification(t('packing.no_items'), 'error'); isProcessing.value = false; return; }
      
      lastCarton.value = { status: 'PRINTING', carton_sn: snPreview.value } as any;

      const res = await packingApi.createCarton({ 
        product_id: currentProduct.value.id, 
        items: items,
        job_order: jobOrder.value || undefined,
        custom_sn: isSNManual.value ? parseInt(customSN.value) : undefined,
        carton_origin: cartonOrigin.value,
        custom_yymm: customYYMM.value || undefined
      });
      cartonId = res.data.id; cartonSn = res.data.carton_sn;
      lastCarton.value = { ...res.data, status: 'PRINTING' };
      backupScannedItems.value = items;
    }

    if (!cartonId) throw new Error('Invalid Carton ID received from server');

    const printResult = await handlePrintExecution(cartonId, cartonSn);
    if (printResult === 'Success') {
      if (lastCarton.value) lastCarton.value.status = 'SUCCESS';
      system.showNotification(t('packing.carton_printed', { sn: cartonSn }), 'success');
      if (cartonSn) {
        const lastSeqMatch = cartonSn.match(/\d{5}$/);
        if (lastSeqMatch) {
            const lastSeq = parseInt(lastSeqMatch[0]);
            suggestedSNValue.value = lastSeq + 1;
            if (!isSNManual.value) {
              customSN.value = (lastSeq + 1).toString();
            }
         }
      }

      if (!isRetry) { 
        if (!isRescanMode.value) {
          if (isSNManual.value && customSN.value && !isNaN(parseInt(customSN.value))) {
            customSN.value = (parseInt(customSN.value) + 1).toString(); 
          } else if (!isSNManual.value) {
            customSN.value = '';
          }
        }
        awaitingNext.value = true; 
        focusScan(); 
      }
    } else { 
      if (lastCarton.value) lastCarton.value.status = 'FAILED'; 
      agentErrorMessage.value = printResult; 
      system.showNotification(t('packing.print_failed', { error: printResult }), 'error'); 
    }
  } catch (err: any) {
    console.error(err);
    if (lastCarton.value && !isRetry) lastCarton.value.status = 'FAILED';
    let msg = err.response?.data?.detail || err.message || t('packing.server_error');
    if (msg === 'AGENT_CONNECTION_FAILED') msg = t('packing.agent_offline');
    system.showNotification(msg, 'error');
  } finally { isProcessing.value = false; }
};

const handlePrintExecution = async (cartonId: number, _cartonSn: string): Promise<string> => {
  try {
    if (settings.printMode === 'local') {
      const resXml = await printApi.download_carton_btxml(cartonId, currentProduct.value?.template_path || '');
      const xmlContent = resXml.data.xml;
      
      const result = await printApi.agentPrint(
        settings.agentUrl, 
        xmlContent, 
        settings.printerName,
        settings.localTemplateDir
      );
      
      if (result.success) {
        await printApi.updateCartonStatus(cartonId, 'SUCCESS');
        return 'Success';
      } else {
        return result.message || 'Agent failed to print';
      }
    } else {
      const res = await printApi.serverPrint(
        cartonId,
        settings.printerName || undefined,
        settings.templatePath || undefined
      );
      if (res.data?.success) {
        if ((res.data as any).type === 'pdf' && (res.data as any).data) {
          const link = document.createElement('a');
          link.href = `data:application/pdf;base64,${(res.data as any).data}`;
          link.download = `Label_${_cartonSn}.pdf`;
          link.click();
        }
        return 'Success';
      } else {
        return (res.data as any)?.message || 'Server print failed';
      }
    }
  } catch (err: any) {
    console.error('Print Execution Error:', err);
    return err.response?.data?.detail || err.message || 'Print connection error.';
  }
};

const handleEmergencyReprint = async (carton: Carton) => {
  if (!carton.id) {
    system.showNotification('Invalid Carton ID', 'error');
    return;
  }
  try {
    const res = await printApi.reprintCarton(carton.id, settings.templatePath || '', settings.printerName);
    const newCarton = res.data;
    if (!newCarton?.id) throw new Error('Failed to create reprint record');
    
    const printResult = await handlePrintExecution(newCarton.id, newCarton.carton_sn);
    if (printResult === 'Success') { 
      system.showNotification(`Reprint successful: ${carton.carton_sn}`, 'success'); 
      showEmergencyModal.value = false; 
    }
    else system.showNotification('Reprint failed: ' + printResult, 'error');
  } catch (err: any) { system.showNotification('Reprint error: ' + (err.response?.data?.detail || err.message), 'error'); }
};

const handleRescan = (carton: Carton) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  currentProduct.value = carton.product || null;
  scannedItems.value = [];
  invalidScans.value = [];
  overflowScans.value = [];
  awaitingNext.value = false;
  lastCarton.value = carton;
  agentErrorMessage.value = '';
  customSN.value = '';
  snPattern.value = '';
  
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
    if (!audioCtx) return;
    if (audioCtx.state === 'suspended') audioCtx.resume();
    
    const beep = (freq: number, start: number, dur: number) => {
      if (!audioCtx) return;
      const o = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      o.connect(g);
      g.connect(audioCtx.destination);
      o.type = 'square';
      o.frequency.setValueAtTime(freq, audioCtx.currentTime + start);
      
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
      const res = await printApi.searchCarton(newVal);
      snExists.value = !!res.data;
    } catch (e) {
      snExists.value = false;
    }
  }, 500);
});

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
  window.addEventListener('click', (e) => { 
    if (showSettings.value || showEmergencyModal.value) return; 
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'SELECT') return; 
    focusScan(); 
  });
});

onUnmounted(() => { 
  if (statusTimer) clearInterval(statusTimer); 
  if (agentCheckInterval) clearInterval(agentCheckInterval);
});
</script>
