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
      <div v-if="currentStep === 1" class="flex-1 flex flex-col justify-center items-center py-16 md:py-24">
        <div class="w-full max-w-[480px] bg-slate-50 border border-slate-200/60 rounded-3xl p-6 md:p-8 shadow-xl">
          <div class="text-center mb-8">
            <div class="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-blue-600">
              <i class="fas fa-file-invoice text-[2rem]"></i>
            </div>
            <h2 class="text-[1.5rem] font-black text-slate-900 mb-2">{{ t('packing.enter_job_order_title') }}</h2>
            <p class="text-slate-500 text-[0.9rem]">{{ t('packing.enter_job_order_desc') }}</p>
          </div>

          <form @submit.prevent="submitJobOrder" class="space-y-4">
            <div class="relative">
              <input
                ref="jobOrderInputRef"
                v-model="inputJobOrder"
                :placeholder="t('packing.job_order_placeholder')"
                class="w-full border rounded-2xl px-5 py-4 text-[1.1rem] outline-none bg-white font-mono transition-all text-center tracking-wider"
                :class="hasJobOrderError
                  ? 'border-rose-500 text-rose-600 focus:border-rose-500 focus:ring-rose-500/10 shadow-[0_0_0_4px_rgba(239,68,68,0.1)] bg-rose-50/10'
                  : 'border-slate-200 focus:border-blue-500 focus:ring-blue-500/10 text-slate-800'"
                autocomplete="off"
                :disabled="isLoadingJobOrder"
              />
            </div>

            <!-- Job Order Error Alert -->
            <div 
              v-if="hasJobOrderError && jobOrderErrorText"
              class="text-[0.85rem] text-rose-600 bg-rose-50 px-4 py-3 rounded-2xl border border-rose-100 font-bold flex items-center gap-2 animate-in"
            >
              <i class="fas fa-exclamation-circle text-rose-500"></i>
              <span>{{ jobOrderErrorText }}</span>
            </div>

            <button
              type="submit"
              :disabled="!inputJobOrder.trim() || isLoadingJobOrder"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 text-white disabled:text-slate-400 font-bold py-4 px-6 rounded-2xl transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-blue-500/10"
            >
              <i v-if="isLoadingJobOrder" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-arrow-right"></i>
              <span>{{ t('packing.confirm') }}</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Bước 2: Thông tin đơn hàng (Product Card) -->
      <div v-else-if="currentStep === 2" class="flex-1 flex flex-col justify-center items-center py-16 md:py-24 animate-in">
        <div class="w-full max-w-[550px] space-y-6">
          <div class="flex justify-between items-center px-2">
            <span class="text-[0.9rem] text-slate-500 font-medium">
              {{ t('packing.job_order') }}: <strong class="font-mono text-slate-800">{{ jobOrder }}</strong>
            </span>
            <button @click="changeJobOrder" class="text-blue-600 hover:text-blue-800 border-none bg-transparent font-bold cursor-pointer text-[0.9rem] flex items-center gap-1.5">
              <i class="fas fa-exchange-alt"></i> {{ t('packing.change_job_order', 'Đổi công lệnh') }}
            </button>
          </div>

          <!-- Product Card -->
          <div 
            @click="enterScanning"
            class="bg-linear-to-br from-slate-900 to-slate-800 text-white rounded-[24px] p-8 shadow-2xl hover:scale-[1.02] cursor-pointer transition-all duration-300 relative overflow-hidden group border border-slate-700/30"
          >
            <div class="absolute -right-10 -bottom-10 opacity-5 text-[10rem] pointer-events-none group-hover:scale-110 transition-transform duration-500">
              <i class="fas fa-box-open"></i>
            </div>
            
            <div class="flex justify-between items-start mb-6">
              <span class="bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-xl px-3 py-1 text-[0.8rem] font-bold uppercase tracking-wider">
                Product Info
              </span>
              <div class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white/80 group-hover:bg-white/20 transition-colors">
                <i class="fas fa-arrow-right"></i>
              </div>
            </div>

            <h3 class="text-[1.8rem] font-black leading-tight mb-2 tracking-wide text-white group-hover:text-blue-200 transition-colors">
              {{ jobOrderDetails?.product.item_name }}
            </h3>
            
            <p class="text-slate-400 font-mono text-[1rem] mb-6">
              UPC: {{ jobOrderDetails?.product.upc || 'N/A' }}
            </p>

            <div class="grid grid-cols-3 gap-2 border-t border-white/10 pt-6">
              <div>
                <span class="text-slate-400 text-[0.8rem] uppercase font-bold block mb-1">Quy cách / Thùng</span>
                <span class="text-[1.3rem] font-black text-white">QTY: {{ jobOrderDetails?.product.packed_qty }}</span>
              </div>
              <div class="border-x border-white/10 px-2 text-center">
                <span class="text-slate-400 text-[0.8rem] uppercase font-bold block mb-1">{{ t('packing.total_qty') }}</span>
                <span class="text-[1.3rem] font-black text-emerald-400">{{ jobOrderDetails?.total_qty }} con</span>
              </div>
              <div class="text-right">
                <span class="text-slate-400 text-[0.8rem] uppercase font-bold block mb-1">{{ t('packing.total_cartons') }}</span>
                <span class="text-[1.3rem] font-black text-blue-400">{{ jobOrderDetails?.total_cartons }} Thùng</span>
              </div>
            </div>
          </div>
          
          <p class="text-center text-slate-400 text-[0.85rem] italic">
            Bấm vào thẻ sản phẩm ở trên để vào giao diện quét mã
          </p>
        </div>
      </div>

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

            <div v-if="isRescanMode" class="bg-orange-50 border border-orange-100 rounded-xl p-2.5 md:p-4 mb-4 flex justify-between items-center text-orange-900 animate-in">
              <div class="flex items-center gap-3">
                <i class="fas fa-redo-alt fa-spin text-orange-500"></i>
                <span><strong>{{ t('packing.rescan_mode', { sn: rescanCartonSN }) }}</strong></span>
              </div>
              <button @click="cancelRescan" class="bg-orange-100 border-none px-3 py-1.5 rounded-lg text-orange-900 font-semibold cursor-pointer transition-colors hover:bg-orange-200 flex items-center gap-1.5 text-[0.85rem]">
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

    <!-- Modal Chi Tiết Vị Trí Thùng (Carton Slots Detail) -->
    <div v-if="showCartonSlotsModal" class="fixed inset-0 bg-black/75 backdrop-blur-md flex justify-center items-center z-[2000] p-4">
      <div class="w-full max-w-[800px] bg-white rounded-[24px] overflow-hidden shadow-2xl flex flex-col border border-slate-100 max-h-[90vh]">
        <!-- Header -->
        <div class="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-slate-50">
          <div class="flex items-center gap-2.5 text-slate-800">
            <i class="fas fa-boxes text-[1.2rem] text-blue-600"></i>
            <h2 class="m-0 text-[1.2rem] font-black text-slate-900">{{ t('packing.carton_slots_title', 'Chi Tiết Vị Trí Thùng') }} ({{ jobOrderDetails?.total_cartons }} {{ t('packing.cartons_unit', 'thùng') }})</h2>
          </div>
          <button @click="showCartonSlotsModal = false" class="w-8 h-8 rounded-full bg-slate-200/50 hover:bg-slate-200 flex items-center justify-center text-slate-500 hover:text-slate-800 border-none cursor-pointer transition-colors">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <!-- Body -->
        <div class="p-6 overflow-y-auto flex-1 bg-slate-50/30">
          <!-- Summary card inside modal -->
          <div class="flex justify-between items-center mb-4 bg-white p-4 rounded-xl border border-slate-100">
            <span class="text-[0.9rem] font-bold text-slate-600">
              {{ t('packing.job_order') }}: <strong class="font-mono text-slate-900">{{ jobOrder }}</strong>
            </span>
            <span class="text-[0.9rem] font-bold text-slate-600">
              {{ t('packing.scanned') }}: <strong class="text-blue-600">{{ scannedCartonsCount }}</strong> / <strong>{{ jobOrderDetails?.total_cartons }}</strong>
            </span>
          </div>

          <!-- Slots Grid -->
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            <div
              v-for="slot in jobOrderSlots"
              :key="slot.id"
              @click="handleSlotClickInModal(slot)"
              class="relative py-3.5 px-2 text-center rounded-xl cursor-pointer font-bold border transition-all flex flex-col justify-center items-center min-h-[68px] shadow-xs active:scale-95"
              :class="[
                slot.status === 'SCANNED'
                  ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed pointer-events-none opacity-60'
                  : 'bg-white border-slate-200 text-slate-700 hover:border-blue-300 hover:bg-blue-50/30',
                selectedSlotId === slot.id ? 'ring-3 ring-blue-500 border-blue-500 bg-blue-500/5 font-extrabold scale-102' : ''
              ]"
            >
              <span class="font-mono text-[0.9rem] sm:text-[0.95rem] font-black tracking-tight" :class="slot.status === 'SCANNED' ? 'text-slate-400/80' : 'text-slate-800'">{{ slot.carton_sn }}</span>
              <span class="text-[0.7rem] sm:text-[0.75rem] leading-none mt-1.5 font-bold" :class="slot.status === 'SCANNED' ? 'text-slate-400/50' : 'text-slate-400'">{{ t('packing.carton', 'Thùng') }} {{ slot.carton_number }}/{{ jobOrderDetails?.total_cartons }}</span>
              <i v-if="slot.status === 'SCANNED'" class="fas fa-check-circle text-emerald-500 text-[0.85rem] absolute top-1.5 right-1.5"></i>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button @click="showCartonSlotsModal = false" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-xl transition-all shadow-lg shadow-blue-500/10 cursor-pointer text-[0.85rem]">
            {{ t('settings.close', 'Đóng') }}
          </button>
        </div>
      </div>
    </div>

    <SettingsModal :show="showSettings" @close="showSettings = false" />
    <EmergencyReprintModal 
      :show="showEmergencyModal" 
      @close="closeEmergencyModal" 
      @reprint="handleEmergencyReprint" 
      @rescan="handleRescan"
    />

    <!-- Carton Verification Modal -->
    <div v-if="showVerificationModal" class="fixed inset-0 bg-black/70 backdrop-blur-md flex justify-center items-center z-[2000]">
      <div class="w-[95%] max-w-[600px] bg-white rounded-[24px] overflow-hidden shadow-2xl flex flex-col animate-in border border-slate-100" :class="{ 'ring-4 ring-rose-500/20 border-rose-300 animate-shake': verificationError }">
        
        <!-- Header -->
        <div class="flex justify-between items-center px-8 pt-6 pb-4 border-b border-slate-100">
          <div class="flex items-center gap-3 text-slate-800">
            <i class="fas fa-barcode text-[1.5rem] text-blue-600 animate-pulse"></i>
            <h2 class="m-0 text-[1.5rem] font-black text-slate-900">{{ t('packing.verification_title') }}</h2>
          </div>
        </div>

        <!-- Body -->
        <div class="px-8 py-6 flex-1">
          <p class="text-slate-500 text-[0.95rem] mb-6">
            {{ t('packing.verification_desc') }}
          </p>

          <!-- Expected SN display -->
          <div class="mb-6">
            <span class="text-[0.75rem] uppercase tracking-wider text-slate-400 font-bold block mb-2">{{ t('packing.expected_sn') }}</span>
            <div class="bg-slate-50 border border-slate-200 rounded-2xl p-5 text-center shadow-inner-sm">
              <span class="font-mono text-[2rem] font-bold text-slate-900 select-all tracking-wider">
                {{ cartonToVerify?.carton_sn }}
              </span>
            </div>
          </div>

          <!-- Product info details -->
          <div class="grid grid-cols-2 gap-4 mb-6 bg-slate-50/50 p-4 rounded-xl border border-slate-100">
            <div>
              <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">{{ t('admin.product') }}</span>
              <span class="text-slate-700 font-medium text-[0.85rem] truncate block">{{ currentProduct?.item_name || 'N/A' }}</span>
            </div>
            <div>
              <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">{{ t('packing.job_order') }}</span>
              <span class="text-slate-700 font-medium text-[0.85rem]">{{ cartonToVerify?.job_order || 'N/A' }}</span>
            </div>
            <div>
              <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">{{ t('print.items') }}</span>
              <span class="text-slate-700 font-medium text-[0.85rem]">{{ cartonToVerify?.items?.length || scannedItems.length }} pcs</span>
            </div>
            <div>
              <span class="text-[0.7rem] uppercase tracking-wider text-slate-400 font-bold block">Status</span>
              <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[0.75rem] font-semibold bg-amber-50 text-amber-700 border border-amber-200/60 mt-0.5">
                <i class="fas fa-print"></i> PRINTED
              </span>
            </div>
          </div>

          <!-- Scan input field -->
          <div class="relative">
            <div class="border rounded-xl p-1 flex gap-2 bg-white transition-all duration-300" 
                 :class="verificationError ? 'border-rose-500 shadow-[0_0_0_4px_rgba(239,68,68,0.1)]' : 'border-slate-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10'">
              <div class="flex-1 flex items-center pl-3">
                <i class="fas fa-barcode text-slate-400 text-[1.1rem]"></i>
                <input 
                  ref="verificationInputRef" 
                  v-model="verificationScanBuffer" 
                  @keydown.enter.prevent="handleVerificationScan" 
                  :placeholder="t('packing.verification_placeholder')" 
                  class="w-full border-none px-3.5 py-3 text-[1rem] text-slate-800 outline-none bg-transparent font-mono" 
                  autocomplete="off"
                />
              </div>
            </div>
            
            <!-- Wrong scan error popup -->
            <div v-if="verificationError" class="absolute left-0 right-0 -bottom-10 text-center text-rose-600 text-[0.85rem] font-bold animate-in">
              <i class="fas fa-exclamation-circle mr-1"></i> {{ t('packing.verification_error') }}
            </div>
          </div>
        </div>

        <!-- Footer with home button -->
        <div class="px-8 py-5 bg-slate-50 border-t border-slate-100 flex justify-between items-center gap-3">
          <button 
            @click="resetSession" 
            class="bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 px-4 py-2 rounded-xl text-[0.85rem] font-semibold cursor-pointer transition-all flex items-center gap-1.5 active:scale-95"
          >
            <i class="fas fa-home text-slate-500"></i>
            <span>{{ t('packing.back_home') }}</span>
          </button>
          
          <span class="text-slate-400 text-[0.85rem] flex items-center gap-1.5">
            <i class="fas fa-keyboard animate-pulse"></i> {{ t('packing.waiting_scanner') }}
          </span>
        </div>

      </div>
    </div>
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
import jobOrderApi from '../features/job_order/api';
import type { Product, Carton, JobOrderSlot, JobOrderDetails } from '../types/api';

import AppHeader from '../core/components/AppHeader.vue';
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

// New Job Order steps & slots reactive state
const currentStep = ref<number>(1);
const inputJobOrder = ref<string>('');
const isLoadingJobOrder = ref<boolean>(false);
const jobOrderDetails = ref<JobOrderDetails | null>(null);
const jobOrderSlots = ref<JobOrderSlot[]>([]);
const cartonNumberStr = ref<string>('');
const selectedSlotId = ref<number | null>(null);
const jobOrderInputRef = ref<HTMLInputElement | null>(null);
const hasCartonNumberError = ref<boolean>(false);
const cartonNumberErrorText = ref<string>('');
const hasJobOrderError = ref<boolean>(false);
const jobOrderErrorText = ref<string>('');

const scannedCartonsCount = computed(() => {
  return jobOrderSlots.value.filter(s => s.status === 'SCANNED').length;
});

interface InvalidScan {
  sn: string;
  time: string;
  reason: string;
  type: 'pattern' | 'duplicate' | 'lockdown';
}

interface OverflowScan {
  sn: string;
  time: string;
  reason: string;
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
const hadJobOrder = ref<boolean>(false);
const savedSessionState = ref<any>(null);

const openEmergencyModal = () => {
  hadJobOrder.value = !!jobOrder.value;
  showEmergencyModal.value = true;
};
const isRescanMode = ref<boolean>(false);
const rescanCartonSN = ref<string>('');
const isSNManual = ref<boolean>(false);
const snExists = ref<boolean>(false);

const showCartonSlotsModal = ref<boolean>(false);
const showVerificationModal = ref<boolean>(false);
const cartonToVerify = ref<(Carton & { status?: string, items?: { item_sn: string }[] }) | null>(null);
const verificationScanBuffer = ref<string>('');
const verificationInputRef = ref<HTMLInputElement | null>(null);
const verificationError = ref<boolean>(false);

watch(inputJobOrder, () => {
  hasJobOrderError.value = false;
  jobOrderErrorText.value = '';
});

watch(cartonNumberStr, (newVal) => {
  if (!newVal.trim()) {
    hasCartonNumberError.value = false;
    cartonNumberErrorText.value = '';
    return;
  }
  const num = parseInt(newVal);
  if (isNaN(num)) {
    hasCartonNumberError.value = true;
    cartonNumberErrorText.value = 'Số sê-ri không hợp lệ!';
    selectedSlotId.value = null;
    return;
  }
  
  if (jobOrderSlots.value.length > 0) {
    const matchedSlot = jobOrderSlots.value.find(s => {
      const seqMatch = s.carton_sn.match(/\d{5}$/);
      return seqMatch ? parseInt(seqMatch[0]) === num : false;
    });
    
    if (!matchedSlot) {
      hasCartonNumberError.value = true;
      
      // Construct expected full Carton SN for display
      let yymm = '';
      if (customYYMM.value && customYYMM.value.length === 4) {
        yymm = customYYMM.value;
      } else {
        const now = new Date();
        const yy = String(now.getFullYear()).slice(-2);
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        yymm = `${yy}${mm}`;
      }
      const prefix = currentProduct.value 
        ? `${currentProduct.value.start_part || ''}${yymm}${currentProduct.value.middle_part || ''}`
        : '';
      const fullSn = `${prefix}${String(num).padStart(5, '0')}`;
      
      cartonNumberErrorText.value = `Sê-ri thùng ${fullSn} không nằm trong công lệnh!`;
      selectedSlotId.value = null;
    } else if (matchedSlot.status === 'SCANNED') {
      hasCartonNumberError.value = true;
      cartonNumberErrorText.value = `Thùng sê-ri ${matchedSlot.carton_sn} đã đóng gói rồi!`;
      selectedSlotId.value = null;
    } else {
      hasCartonNumberError.value = false;
      cartonNumberErrorText.value = '';
      selectedSlotId.value = matchedSlot.id;
      
      // Sync manual details
      const sn = matchedSlot.carton_sn;
      const seqMatch = sn.match(/\d{5}$/);
      if (seqMatch) {
        customSN.value = parseInt(seqMatch[0]).toString();
      }
      if (sn.length >= 6) {
        customYYMM.value = sn.slice(2, 6);
      }
      isSNManual.value = true;
    }
  } else {
    hasCartonNumberError.value = false;
    cartonNumberErrorText.value = '';
    selectedSlotId.value = null;
  }
});


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

const cartonNumberRange = computed(() => {
  if (jobOrderSlots.value.length === 0) return '';
  
  let minSeq = Infinity;
  let maxSeq = -Infinity;
  
  for (const slot of jobOrderSlots.value) {
    const seqMatch = slot.carton_sn.match(/\d{5}$/);
    if (seqMatch) {
      const seq = parseInt(seqMatch[0]);
      if (seq < minSeq) minSeq = seq;
      if (seq > maxSeq) maxSeq = seq;
    }
  }
  
  if (minSeq === Infinity || maxSeq === -Infinity) return '';
  return `${minSeq} -> ${maxSeq}`;
});

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

const submitJobOrder = async () => {
  const jo = inputJobOrder.value.trim();
  if (!jo) return;
  isLoadingJobOrder.value = true;
  hasJobOrderError.value = false;
  jobOrderErrorText.value = '';
  try {
    const res = await jobOrderApi.getJobOrderDetails(jo);
    jobOrderDetails.value = res.data;
    jobOrder.value = res.data.job_order;
    jobOrderSlots.value = res.data.slots;
    currentProduct.value = res.data.product;
    currentStep.value = 2;
    system.showNotification('Đã tải thông tin công lệnh thành công!', 'success');
    
    // Fetch last carton details for verification / backup restoration
    if (res.data.product) {
      const p = res.data.product;
      try {
        const lastCartonRes = await packingApi.getLastCarton(p.id);
        if (lastCartonRes.data) {
          lastCarton.value = lastCartonRes.data;
          if (lastCartonRes.data.status === 'FAILED' && lastCartonRes.data.items) {
            backupScannedItems.value = lastCartonRes.data.items.map((i: any) => i.item_sn);
          }
          if (lastCartonRes.data.status === 'PRINTED') {
            showVerificationModal.value = true;
            cartonToVerify.value = lastCartonRes.data;
            if (lastCartonRes.data.items) {
              scannedItems.value = lastCartonRes.data.items.map((i: any) => i.item_sn);
            }
          }
        }
      } catch (err) {
        console.warn('Error fetching last carton:', err);
      }
    }
  } catch (err: any) {
    console.error(err);
    const detail = t('packing.job_order_not_found', { jo: jo });
    hasJobOrderError.value = true;
    jobOrderErrorText.value = detail;
    system.showNotification(detail, 'error');
  } finally {
    isLoadingJobOrder.value = false;
  }
};

const changeJobOrder = () => {
  if (scannedItems.value.length > 0) {
    if (!confirm(t('packing.change_job_order_confirm'))) {
      return;
    }
  }
  currentStep.value = 1;
  inputJobOrder.value = '';
  jobOrder.value = '';
  jobOrderDetails.value = null;
  jobOrderSlots.value = [];
  selectedSlotId.value = null;
  cartonNumberStr.value = '';
  currentProduct.value = null;
  scannedItems.value = [];
  lastCarton.value = null;
  customSN.value = '';
  customYYMM.value = '';
  isSNManual.value = false;
  showCartonSlotsModal.value = false;
  
  nextTick(() => {
    if (jobOrderInputRef.value) jobOrderInputRef.value.focus();
  });
};

const enterScanning = () => {
  currentStep.value = 3;
  // Automatically select first pending slot
  const firstPending = jobOrderSlots.value.find(s => s.status === 'PENDING');
  if (firstPending) {
    selectSlot(firstPending);
  } else if (jobOrderSlots.value.length > 0) {
    selectSlot(jobOrderSlots.value[0]);
  }
  checkTemplateExists();
  focusScan();
};

const selectSlot = (slot: JobOrderSlot, confirmDiscard = true) => {
  hasCartonNumberError.value = false;
  cartonNumberErrorText.value = '';
  if (slot.status === 'SCANNED') {
    return;
  }

  if (confirmDiscard && scannedItems.value.length > 0 && selectedSlotId.value !== slot.id) {
    if (!confirm(t('packing.switch_slot_confirm'))) {
      return;
    }
  }
  
  selectedSlotId.value = slot.id;
  
  const sn = slot.carton_sn;
  const seqMatch = sn.match(/\d{5}$/);
  if (seqMatch) {
    const seqNum = parseInt(seqMatch[0]);
    cartonNumberStr.value = seqNum.toString();
    customSN.value = seqNum.toString();
  } else {
    cartonNumberStr.value = '';
    customSN.value = '';
  }
  if (sn.length >= 6) {
    customYYMM.value = sn.slice(2, 6);
  }
  
  isSNManual.value = true;
  scannedItems.value = [];
  
  focusScan();
};

const handleSlotClickInModal = (slot: JobOrderSlot) => {
  selectSlot(slot);
  if (selectedSlotId.value === slot.id) {
    showCartonSlotsModal.value = false;
  }
};

const handleCartonNumberSubmit = () => {
  const num = parseInt(cartonNumberStr.value);
  if (isNaN(num)) {
    hasCartonNumberError.value = true;
    cartonNumberErrorText.value = 'Vui lòng nhập số sê-ri thùng hợp lệ!';
    system.showNotification('Vui lòng nhập số sê-ri thùng hợp lệ!', 'error');
    selectedSlotId.value = null;
    return;
  }
  
  const matchedSlot = jobOrderSlots.value.find(s => {
    const seqMatch = s.carton_sn.match(/\d{5}$/);
    return seqMatch ? parseInt(seqMatch[0]) === num : false;
  });
  
  if (!matchedSlot) {
    hasCartonNumberError.value = true;
    
    let yymm = '';
    if (customYYMM.value && customYYMM.value.length === 4) {
      yymm = customYYMM.value;
    } else {
      const now = new Date();
      const yy = String(now.getFullYear()).slice(-2);
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      yymm = `${yy}${mm}`;
    }
    const prefix = currentProduct.value 
      ? `${currentProduct.value.start_part || ''}${yymm}${currentProduct.value.middle_part || ''}`
      : '';
    const fullSn = `${prefix}${String(num).padStart(5, '0')}`;
    
    cartonNumberErrorText.value = `Sê-ri thùng ${fullSn} không nằm trong công lệnh!`;
    system.showNotification(`Sê-ri thùng ${fullSn} không nằm trong công lệnh!`, 'error');
    selectedSlotId.value = null;
    return;
  }
  
  if (matchedSlot.status === 'SCANNED') {
    hasCartonNumberError.value = true;
    cartonNumberErrorText.value = `Thùng sê-ri ${matchedSlot.carton_sn} đã đóng gói rồi!`;
    system.showNotification(`Thùng sê-ri ${matchedSlot.carton_sn} đã hoàn thành rồi!`, 'warning');
    selectedSlotId.value = null;
    return;
  }
  
  hasCartonNumberError.value = false;
  cartonNumberErrorText.value = '';
  selectSlot(matchedSlot);
};

const playSuccessSound = () => {
  try {
    if (!audioCtx) return;
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.connect(g);
    g.connect(audioCtx.destination);
    o.type = 'sine';
    o.frequency.setValueAtTime(1200, audioCtx.currentTime);
    g.gain.setValueAtTime(0, audioCtx.currentTime);
    g.gain.linearRampToValueAtTime(0.5, audioCtx.currentTime + 0.01);
    g.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.15);
    o.start(audioCtx.currentTime);
    o.stop(audioCtx.currentTime + 0.15);
  } catch (e) { console.warn('Audio success failed:', e); }
};

const confirmVerification = async () => {
  if (!cartonToVerify.value) return;
  try {
    await printApi.updateCartonStatus(cartonToVerify.value.id, 'SUCCESS');
    playSuccessSound();
    
    if (lastCarton.value && lastCarton.value.id === cartonToVerify.value.id) {
      lastCarton.value.status = 'SUCCESS';
    }
    
    const cartonSn = cartonToVerify.value.carton_sn;
    
    // Update local slot status
    const matchedSlot = jobOrderSlots.value.find(s => s.carton_sn === cartonSn);
    if (matchedSlot) {
      matchedSlot.status = 'SCANNED';
      matchedSlot.carton_id = cartonToVerify.value.id;
      matchedSlot.scanned_at = new Date().toISOString();
    }
    
    awaitingNext.value = true;
    showVerificationModal.value = false;
    cartonToVerify.value = null;
    verificationScanBuffer.value = '';
    
    system.showNotification(t('packing.verification_success', { sn: cartonSn }), 'success');
    
    if (isRescanMode.value) {
      isRescanMode.value = false;
      rescanCartonSN.value = '';
      if (agentCheckInterval) {
        clearInterval(agentCheckInterval);
        agentCheckInterval = null;
      }
      if (!hadJobOrder.value) {
        resetSession();
      } else {
        if (savedSessionState.value) {
          const s = savedSessionState.value;
          currentStep.value = s.currentStep;
          selectedSlotId.value = s.selectedSlotId;
          cartonNumberStr.value = s.cartonNumberStr;
          customSN.value = s.customSN;
          customYYMM.value = s.customYYMM;
          isSNManual.value = s.isSNManual;
          scannedItems.value = s.scannedItems;
          cartonOrigin.value = s.cartonOrigin;
          jobOrder.value = s.jobOrder;
          currentProduct.value = s.currentProduct;
          savedSessionState.value = null;
        }
        awaitingNext.value = false;
        focusScan();
      }
      return;
    }
    
    // Automatically switch to next pending carton slot
    const nextPending = jobOrderSlots.value.find(s => s.status === 'PENDING');
    if (nextPending) {
      selectSlot(nextPending, false);
    } else {
      selectedSlotId.value = null;
      cartonNumberStr.value = '';
      customSN.value = '';
      customYYMM.value = '';
      isSNManual.value = false;
      system.showNotification('Đã quét xong toàn bộ số thùng của công lệnh!', 'success');
    }
  } catch (err: any) {
    console.error(err);
    system.showNotification(t('packing.update_status_failed'), 'error');
  }
};


const handleVerificationScan = () => {
  const scannedVal = verificationScanBuffer.value.trim();
  if (!scannedVal) return;
  
  if (!cartonToVerify.value) return;
  
  const expectedVal = cartonToVerify.value.carton_sn.trim();
  if (scannedVal.toLowerCase() === expectedVal.toLowerCase()) {
    verificationError.value = false;
    confirmVerification();
  } else {
    playScanAlert();
    verificationError.value = true;
    verificationScanBuffer.value = '';
    system.showNotification(t('packing.verification_error'), 'error');
    setTimeout(() => {
      verificationError.value = false;
    }, 1500);
  }
};

const refreshNextSN = async () => {
  if (currentStep.value === 3) return;
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
      overflowScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Carton Full' });
      system.showNotification(t('packing.carton_full', { sn }), 'warning');
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

  if (scannedItems.value.length >= currentProduct.value.packed_qty) {
    playScanAlert();
    overflowScans.value.push({ sn, time: new Date().toLocaleTimeString(), reason: 'Carton Full' });
    system.showNotification(t('packing.carton_full'), 'error');
    return;
  }

  scannedItems.value.push(sn);
  if (scannedItems.value.length === currentProduct.value.packed_qty) { 
    finalizeCarton(); 
  }
};

const handleScan = () => {
  const rawInput = scanBuffer.value.trim();
  if (!rawInput) return;

  const sns = rawInput.split(/\s*[\n\r\t,]+\s*/).map(s => s.trim()).filter(s => s.length > 0);
  
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
        slot_id: selectedSlotId.value || undefined,
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
      if (lastCarton.value) lastCarton.value.status = 'PRINTED';
      
      verificationScanBuffer.value = '';
      verificationError.value = false;
      cartonToVerify.value = lastCarton.value;
      showVerificationModal.value = true;
      
      system.showNotification(t('packing.carton_printed', { sn: cartonSn }), 'success');
      
      nextTick(() => {
        if (verificationInputRef.value) {
          verificationInputRef.value.focus();
        }
      });
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

const handlePrintExecution = async (cartonId: number, _cartonSn: string, skipStatusUpdate = false): Promise<string> => {
  try {
    if (settings.printMode === 'local') {
      const resXml = await printApi.download_carton_btxml(cartonId, currentProduct.value?.template_path || '');
      const xmlContent = resXml.data;
      
      const result = await printApi.agentPrint(
        settings.agentUrl, 
        xmlContent, 
        settings.printerName,
        settings.localTemplateDir
      );
      
      if (result.success) {
        if (!skipStatusUpdate) {
          await printApi.updateCartonStatus(cartonId, 'PRINTED');
        }
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
    const rawMsg = err.response?.data?.detail || err.message || 'Print connection error.';
    const finalMsg = typeof rawMsg === 'object' ? JSON.stringify(rawMsg) : String(rawMsg);
    return finalMsg;
  }
};

const closeEmergencyModal = () => {
  showEmergencyModal.value = false;
  if (!hadJobOrder.value) {
    resetSession();
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
    
    if (!currentProduct.value && carton.product) {
      currentProduct.value = carton.product;
    }

    const printResult = await handlePrintExecution(newCarton.id, newCarton.carton_sn, true);
    if (printResult === 'Success') { 
      system.showNotification(`Reprint successful: ${carton.carton_sn}`, 'success'); 
      showEmergencyModal.value = false;
      if (!hadJobOrder.value) {
        resetSession();
      }
    }
    else system.showNotification('Reprint failed: ' + printResult, 'error');
  } catch (err: any) { system.showNotification('Reprint error: ' + (err.response?.data?.detail || err.message), 'error'); }
};

const handleRescan = (carton: Carton) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  
  if (hadJobOrder.value) {
    savedSessionState.value = {
      currentStep: currentStep.value,
      selectedSlotId: selectedSlotId.value,
      cartonNumberStr: cartonNumberStr.value,
      customSN: customSN.value,
      customYYMM: customYYMM.value,
      isSNManual: isSNManual.value,
      scannedItems: [...scannedItems.value],
      cartonOrigin: cartonOrigin.value,
      jobOrder: jobOrder.value,
      currentProduct: currentProduct.value
    };
  }

  currentProduct.value = carton.product || null;
  scannedItems.value = [];
  invalidScans.value = [];
  overflowScans.value = [];
  awaitingNext.value = false;
  lastCarton.value = carton;
  agentErrorMessage.value = '';
  customSN.value = '';
  snPattern.value = '';
  
  jobOrder.value = carton.job_order || 'EMERGENCY_RESCAN';
  cartonOrigin.value = carton.carton_origin || 'VN';
  isRescanMode.value = true;
  rescanCartonSN.value = carton.carton_sn;
  showEmergencyModal.value = false;
  currentStep.value = 3;
  
  system.showNotification(`RESCAN MODE ACTIVE for ${carton.carton_sn}`, 'warning');
  checkAgentHealth();
  agentCheckInterval = setInterval(checkAgentHealth, 5000);
  focusScan();
};

const cancelRescan = () => {
  isRescanMode.value = false;
  rescanCartonSN.value = '';
  if (agentCheckInterval) {
    clearInterval(agentCheckInterval);
    agentCheckInterval = null;
  }
  if (!hadJobOrder.value) {
    resetSession();
  } else {
    if (savedSessionState.value) {
      const s = savedSessionState.value;
      currentStep.value = s.currentStep;
      selectedSlotId.value = s.selectedSlotId;
      cartonNumberStr.value = s.cartonNumberStr;
      customSN.value = s.customSN;
      customYYMM.value = s.customYYMM;
      isSNManual.value = s.isSNManual;
      scannedItems.value = s.scannedItems;
      cartonOrigin.value = s.cartonOrigin;
      jobOrder.value = s.jobOrder;
      currentProduct.value = s.currentProduct;
      savedSessionState.value = null;
    }
    focusScan();
  }
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
  if (scannedItems.value.length > 0) {
    if (!confirm(t('packing.reset_session_confirm'))) {
      return;
    }
  }
  currentStep.value = 1;
  inputJobOrder.value = '';
  jobOrder.value = '';
  jobOrderDetails.value = null;
  jobOrderSlots.value = [];
  selectedSlotId.value = null;
  cartonNumberStr.value = '';
  currentProduct.value = null; 
  scannedItems.value = []; 
  invalidScans.value = []; 
  overflowScans.value = []; 
  awaitingNext.value = false; 
  isRescanMode.value = false;
  rescanCartonSN.value = '';
  scanBuffer.value = ''; 
  showVerificationModal.value = false;
  cartonToVerify.value = null;
  showCartonSlotsModal.value = false;
  nextTick(() => { if (jobOrderInputRef.value) jobOrderInputRef.value.focus(); }); 
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

watch(showVerificationModal, (val) => {
  if (val) {
    nextTick(() => {
      if (verificationInputRef.value) {
        verificationInputRef.value.focus();
      }
    });
  }
});

watch([currentStep, inputJobOrder, jobOrderDetails, jobOrderSlots, cartonNumberStr, selectedSlotId, jobOrder, cartonOrigin, currentProduct, scannedItems, customSN, snPattern, awaitingNext, suggestedSNValue, backupScannedItems, lastCarton, invalidScans, isSNManual, overflowScans, isRescanMode, rescanCartonSN, showVerificationModal, cartonToVerify], () => {
  sessionStorage.setItem('packingState', JSON.stringify({ 
    currentStep: currentStep.value,
    inputJobOrder: inputJobOrder.value,
    jobOrderDetails: jobOrderDetails.value,
    jobOrderSlots: jobOrderSlots.value,
    cartonNumberStr: cartonNumberStr.value,
    selectedSlotId: selectedSlotId.value,
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
    rescanCartonSN: rescanCartonSN.value,
    showVerificationModal: showVerificationModal.value,
    cartonToVerify: cartonToVerify.value
  }));
}, { deep: true });

onMounted(() => {
  const saved = sessionStorage.getItem('packingState');
  if (saved) { 
    try { 
      const s = JSON.parse(saved); 
      if (s.currentStep !== undefined) currentStep.value = s.currentStep;
      if (s.inputJobOrder) inputJobOrder.value = s.inputJobOrder;
      if (s.jobOrderDetails) jobOrderDetails.value = s.jobOrderDetails;
      if (s.jobOrderSlots) jobOrderSlots.value = s.jobOrderSlots;
      if (s.cartonNumberStr) cartonNumberStr.value = s.cartonNumberStr;
      if (s.selectedSlotId !== undefined) selectedSlotId.value = s.selectedSlotId;
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
      if (s.showVerificationModal !== undefined) showVerificationModal.value = s.showVerificationModal;
      if (s.cartonToVerify) cartonToVerify.value = s.cartonToVerify;
    } catch (e) { console.error('Restore failed', e); } 
  }
  settings.loadSettings();
  checkSystem();
  checkAgentHealth();
  nextTick(() => { 
    if (showVerificationModal.value) {
      if (verificationInputRef.value) verificationInputRef.value.focus();
    } else if (currentStep.value === 1 && jobOrderInputRef.value) {
      jobOrderInputRef.value.focus();
    } else {
      focusScan();
    }
  });
  statusTimer = setInterval(() => { checkSystem(); refreshNextSN(); }, 3000);
  agentCheckInterval = setInterval(checkAgentHealth, 5000);
  window.addEventListener('click', (e) => { 
    if (showSettings.value || showEmergencyModal.value) return; 
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'SELECT') return; 
    
    if (showVerificationModal.value) {
      if (verificationInputRef.value) verificationInputRef.value.focus();
    } else if (currentStep.value === 3) {
      focusScan(); 
    }
  });
});

onUnmounted(() => { 
  if (statusTimer) clearInterval(statusTimer); 
  if (agentCheckInterval) clearInterval(agentCheckInterval);
});

</script>
