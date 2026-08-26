<template>
  <div class="min-h-screen p-3 md:p-4 text-slate-800 flex justify-center bg-radial-at-tr from-slate-50 to-slate-200">
    <div class="w-full max-w-[1100px] transition-all duration-500 ease-out flex flex-col bg-white/95 backdrop-blur-2xl border border-white/80 rounded-[20px] p-2.5 md:p-4 shadow-2xl shadow-slate-900/5" :class="{ 'max-w-[1550px]': currentStep === 3 }">
      <AppHeader
        :isAudioActive="isAudioActive"
        @toggle-audio="toggleAudio"
        @show-emergency="openEmergencyModal"
        @show-settings="showSettings = true"
        @home="resetSession"
      />

      <!-- Bước 1: Nhập Công Lệnh -->
      <JobOrderInputStep
        v-if="currentStep === 1"
        ref="jobOrderInputStepRef"
        v-model="inputJobOrder"
        :isLoading="isLoadingJobOrder"
        :hasError="hasJobOrderError"
        :errorText="jobOrderErrorText"
        @submit="submitJobOrder"
      />

      <!-- Bước 2: Thông tin đơn hàng (Product Card) -->
      <ProductCardStep
        v-else-if="currentStep === 2"
        :jobOrder="jobOrder"
        :jobOrderDetails="jobOrderDetails"
        @changeJobOrder="changeJobOrder"
        @enterScanning="enterScanning"
      />

      <!-- Bước 3: Giao diện quét mã -->
      <section class="mt-2" v-else-if="currentStep === 3">
        <div class="flex flex-col lg:flex-row gap-4 xl:gap-6 items-stretch lg:items-start">
          <div class="flex-[1.4] min-w-0">
            <SessionHeader
              :product="currentProduct!"
              :jobOrder="jobOrder"
              v-model:cartonOrigin="cartonOrigin"
              v-model:cartonNumberStr="cartonNumberStr"
              :cartonNumberRange="cartonNumberRange"
              :snPreview="snPreview"
              v-model:snPattern="snPattern"
              :customYYMM="customYYMM"
              :hasCartonNumberError="hasCartonNumberError"
              :cartonNumberErrorText="cartonNumberErrorText"
              @back="currentStep = 2"
              @focus-scan="focusScan"
              @submit-carton-number="handleCartonNumberSubmit"
              @clear-carton-error="hasCartonNumberError = false; cartonNumberErrorText = '';"
            />

            <!-- Thanh tóm tắt Công lệnh & Tiến độ thùng -->
            <div class="mb-4 bg-linear-to-r from-slate-50 to-white p-3 px-4 rounded-2xl border border-slate-100 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div class="flex items-center gap-2.5">
                <div class="w-9 h-9 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-600">
                  <i class="fas fa-boxes"></i>
                </div>
                <div>
                  <div class="text-[0.85rem] font-bold text-slate-500 uppercase tracking-wider leading-none mb-1">{{ t('packing.packing_progress', 'Tiến Độ Đóng Thùng') }}</div>
                  <div class="text-[0.95rem] font-extrabold text-slate-800">
                    {{ t('packing.scanned') }}: <span class="text-blue-600 font-black">{{ scannedCartonsCount }}</span> / <span class="font-black">{{ jobOrderDetails?.total_cartons }}</span> {{ t('packing.cartons_unit', 'thùng') }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2 w-full sm:w-auto">
                <button @click="showCartonSlotsModal = true" class="flex-1 sm:flex-none px-4 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200/50 rounded-xl font-bold cursor-pointer transition-all flex items-center justify-center gap-1.5 text-[0.85rem] active:scale-95">
                  <i class="fas fa-list-check"></i> {{ t('packing.view_details', 'Xem chi tiết') }}
                </button>
                <button @click="changeJobOrder" class="flex-1 sm:flex-none px-4 py-2 bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-xl font-bold cursor-pointer transition-all flex items-center justify-center gap-1.5 text-[0.85rem] active:scale-95">
                  <i class="fas fa-exchange-alt"></i> {{ t('packing.change_job_order', 'Đổi công lệnh') }}
                </button>
              </div>
            </div>

            <!-- Rescan Mode Alert -->
            <div v-if="isRescanMode" class="bg-orange-50 border border-orange-100 rounded-xl p-2.5 md:p-4 mb-4 flex justify-between items-center text-orange-900 animate-in">
              <div class="flex items-center gap-3">
                <i class="fas fa-redo-alt fa-spin text-orange-500"></i>
                <span><strong>{{ t('packing.rescan_mode', { sn: rescanCartonSN }) }}</strong></span>
              </div>
              <button @click="cancelRescan" class="bg-orange-100 border-none px-3 py-1.5 rounded-lg text-orange-900 font-semibold cursor-pointer transition-colors hover:bg-orange-200 flex items-center gap-1.5 text-[0.85rem]">
                <i class="fas fa-times"></i> {{ t('packing.cancel') }}
              </button>
            </div>

            <!-- Progress & Agent Status -->
            <div class="mb-4 bg-white p-3 md:p-4 rounded-2xl shadow-inner-sm border border-slate-100">
              <div v-if="settings.printMode === 'local' && !agentConnected" class="bg-linear-to-br from-rose-50 to-rose-100 border-2 border-rose-500 rounded-xl p-3 md:p-4 mb-4 shadow-md shadow-rose-500/10 animate-in">
                <div class="flex items-center gap-3 text-rose-800">
                  <i class="fas fa-exclamation-triangle fa-beat text-[1.5rem] text-rose-500"></i>
                  <span class="text-[0.95rem]"><strong>{{ t('packing.agent_offline') }}</strong></span>
                </div>
              </div>

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
              :disabled="(settings.printMode === 'local' && (!agentConnected || templateMissing)) || (!selectedSlotId && !isRescanMode)"
              :placeholder="(!selectedSlotId && !isRescanMode) ? 'Vui lòng chọn hoặc nhập số thùng cần quét trước...' : ((settings.printMode === 'local' && !agentConnected) ? t('packing.scan_placeholder_offline') : (templateMissing ? t('packing.scan_placeholder_missing') : t('packing.scan_placeholder')))"
              :jobOrder="jobOrder"
              :awaitingNext="awaitingNext"
              :invalidScans="invalidScans"
              :overflowScans="overflowScans"
              :allowPartial="currentProduct?.allow_partial === 1"
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

    <!-- Modals -->
    <CartonSlotsModal
      :show="showCartonSlotsModal"
      :jobOrder="jobOrder"
      :totalCartons="jobOrderDetails?.total_cartons"
      :scannedCount="scannedCartonsCount"
      :slots="jobOrderSlots"
      :selectedSlotId="selectedSlotId"
      @close="showCartonSlotsModal = false"
      @selectSlot="handleSlotClickInModal"
    />

    <CartonVerificationModal
      ref="cartonVerificationModalRef"
      :show="showVerificationModal"
      :carton="cartonToVerify"
      :currentProduct="currentProduct"
      :scannedCount="scannedItems.length"
      @close="showVerificationModal = false"
      @verified="confirmVerification"
      @resetSession="resetSession"
      @scanAlert="playScanAlert"
    />

    <SettingsModal :show="showSettings" @close="showSettings = false" />
    <EmergencyReprintModal 
      :show="showEmergencyModal" 
      @close="closeEmergencyModal" 
      @reprint="onEmergencyReprint" 
      @rescan="handleRescan"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSettingsStore } from '../core/stores/settings';
import { useSystemStore } from '../core/stores/system';
import catalogApi from '../features/catalog/api';
import type { Product, Carton } from '../types/api';

import AppHeader from '../core/components/AppHeader.vue';
import SessionHeader from '../features/packing/components/SessionHeader.vue';
import ScanBuffer from '../features/packing/components/ScanBuffer.vue';
import ScannedList from '../features/packing/components/ScannedList.vue';
import PrintStatusBanner from '../features/print/components/PrintStatusBanner.vue';
import SettingsModal from '../features/settings/components/SettingsModal.vue';
import EmergencyReprintModal from '../features/print/components/EmergencyReprintModal.vue';
import JobOrderInputStep from '../features/packing/components/JobOrderInputStep.vue';
import ProductCardStep from '../features/packing/components/ProductCardStep.vue';
import CartonSlotsModal from '../features/packing/components/CartonSlotsModal.vue';
import CartonVerificationModal from '../features/packing/components/CartonVerificationModal.vue';

import { useAgentHealth } from '../features/packing/composables/useAgentHealth';
import { usePackingAudio } from '../features/packing/composables/usePackingAudio';
import { useCartonPrinting } from '../features/packing/composables/useCartonPrinting';
import { usePackingStatePersistence } from '../features/packing/composables/usePackingStatePersistence';
import { useJobOrderWorkflow } from '../features/packing/composables/useJobOrderWorkflow';

const { t } = useI18n();
const system = useSystemStore();
const settings = useSettingsStore();

const currentProduct = ref<Product | null>(null);
const jobOrderInputStepRef = ref<InstanceType<typeof JobOrderInputStep> | null>(null);
const cartonVerificationModalRef = ref<InstanceType<typeof CartonVerificationModal> | null>(null);
const scanRef = ref<InstanceType<typeof ScanBuffer> | null>(null);

let statusTimer: ReturnType<typeof setInterval> | null = null;

const { agentConnected, templateMissing, templateFilename, checkAgentHealth, checkTemplateExists, startPolling, stopPolling } = useAgentHealth({
  settings,
  currentProduct,
});

const { isAudioActive, initAudio, playSuccessSound, playScanAlert, toggleAudio } = usePackingAudio({
  audioDeviceId: settings.audioDeviceId,
});

const focusScan = () => { nextTick(() => { if (scanRef.value) scanRef.value.focusScan(); }); initAudio(); };

const workflow = useJobOrderWorkflow({
  system,
  currentProduct,
  focusScan,
  checkTemplateExists,
  startPolling,
  stopPolling,
  playScanAlert,
  jobOrderInputRef: jobOrderInputStepRef,
  cartonVerificationModalRef,
});

const {
  currentStep, inputJobOrder, isLoadingJobOrder, jobOrderDetails, jobOrderSlots, cartonNumberStr,
  selectedSlotId, jobOrder, cartonOrigin, customSN, snPattern, customYYMM, awaitingNext,
  suggestedSNValue, suggestedSNPreview, backupScannedItems, scannedItems, scanBuffer, invalidScans,
  overflowScans, lastCarton, hadJobOrder, savedSessionState, isRescanMode, rescanCartonSN,
  isSNManual, snExists, showSettings, showEmergencyModal, showCartonSlotsModal, showVerificationModal,
  cartonToVerify, hasCartonNumberError, cartonNumberErrorText, hasJobOrderError, jobOrderErrorText,
  scannedCartonsCount, progressPercent, snPreview, cartonNumberRange, submitJobOrder, changeJobOrder,
  refreshJobOrderDetails, enterScanning, selectSlot, handleSlotClickInModal, handleCartonNumberSubmit,
  refreshNextSN, handleScan, handleRescan, cancelRescan, startNextCarton, resetSession, setOnFinalizeCarton
} = workflow;

const { agentErrorMessage, finalizeCarton, confirmVerification, handleEmergencyReprint } = useCartonPrinting({
  settings, system, currentProduct, jobOrder, selectedSlotId, cartonOrigin, customSN, customYYMM,
  isSNManual, snPreview, snExists, scannedItems, jobOrderSlots, lastCarton, backupScannedItems,
  isRescanMode, rescanCartonSN, showVerificationModal, cartonToVerify, playSuccessSound,
  stopAgentPolling: stopPolling, resetSession: () => resetSession(), selectSlot, focusScan,
  hadJobOrder, savedSessionState, currentStep, cartonNumberStr, suggestedSNPreview, awaitingNext
});

setOnFinalizeCarton(finalizeCarton);

const persistence = usePackingStatePersistence({
  currentStep, inputJobOrder, jobOrderDetails, jobOrderSlots, cartonNumberStr, selectedSlotId, jobOrder,
  cartonOrigin, currentProduct, scannedItems, customSN, snPattern, awaitingNext, suggestedSNValue,
  suggestedSNPreview, backupScannedItems, lastCarton, invalidScans, isSNManual, overflowScans,
  isRescanMode, rescanCartonSN, showVerificationModal, cartonToVerify
});

const openEmergencyModal = () => {
  hadJobOrder.value = !!jobOrder.value;
  showEmergencyModal.value = true;
};

const closeEmergencyModal = () => {
  showEmergencyModal.value = false;
  if (!hadJobOrder.value) resetSession();
};

const onEmergencyReprint = async (carton: Carton) => {
  const ok = await handleEmergencyReprint(carton);
  if (ok) {
    showEmergencyModal.value = false;
    if (!hadJobOrder.value) resetSession();
  }
};

const checkSystem = async () => {
  try {
    await catalogApi.getCustomers();
    system.isOnline = true;
  } catch { system.isOnline = false; }
};

onMounted(() => {
  persistence.restoreState();
  persistence.initPersistence();
  settings.loadSettings();
  checkSystem();
  checkAgentHealth();
  startPolling(5000);
  nextTick(() => { 
    if (showVerificationModal.value) {
      if (cartonVerificationModalRef.value) cartonVerificationModalRef.value.focusInput();
    } else if (currentStep.value === 1 && jobOrderInputStepRef.value) {
      jobOrderInputStepRef.value.focusInput();
    } else {
      focusScan();
    }
  });
  statusTimer = setInterval(() => { checkSystem(); refreshNextSN(); }, 3000);
  
  window.addEventListener('click', (e) => { 
    if (showSettings.value || showEmergencyModal.value) return; 
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'SELECT') return; 
    if (showVerificationModal.value) {
      if (cartonVerificationModalRef.value) cartonVerificationModalRef.value.focusInput();
    } else if (currentStep.value === 3) {
      focusScan(); 
    }
  });
  if (jobOrder.value) refreshJobOrderDetails();
  window.addEventListener('focus', refreshJobOrderDetails);
});

onUnmounted(() => { 
  if (statusTimer) clearInterval(statusTimer); 
  stopPolling();
  window.removeEventListener('focus', refreshJobOrderDetails);
});
</script>
