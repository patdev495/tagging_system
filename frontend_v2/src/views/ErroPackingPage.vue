<template>
  <div class="h-screen w-full bg-slate-100 text-slate-800 flex flex-col p-2 md:p-3 overflow-hidden box-border select-none">
    <div class="w-full h-full flex flex-col bg-white border border-slate-200/90 rounded-2xl p-3 md:p-4 shadow-xl overflow-hidden box-border justify-between">
      
      <ErroFactoryPartNumberStep
        v-if="!selectedProduct && !pendingProduct"
        @resolved="resolveFactoryPartNumber"
      />

      <template v-else>
      <!-- Top Slim Navigation Header -->
      <header class="flex items-center justify-between pb-2 border-b border-slate-200 shrink-0">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 shadow-inner shrink-0">
            <i class="fas fa-weight-scale text-lg"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="font-black text-base md:text-lg text-slate-900 leading-tight">Trạm Cân Đóng Gói (Erro)</h1>
              <span class="px-2 py-0.5 text-[10px] font-black rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200 tracking-wide uppercase">
                Khách Hàng Erro
              </span>
            </div>
            <p class="text-[11px] text-slate-500 leading-none">Kiểm soát trọng lượng dung sai và in nhãn BarTender Erro</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Agent Status -->
          <div 
            :class="[
              'px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 text-xs font-bold transition-all shrink-0 cursor-help',
              isAgentOnline ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs' : 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse'
            ]"
            :title="isAgentOnline ? `Print Agent đang chạy (${settings.agentUrl || 'http://127.0.0.1:8080'})` : 'Chưa bật phần mềm NY Print Agent trên máy tính'"
          >
            <span class="relative flex h-2 w-2">
              <span v-if="isAgentOnline" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span :class="['relative inline-flex rounded-full h-2 w-2', isAgentOnline ? 'bg-emerald-500' : 'bg-rose-500']"></span>
            </span>
            <i class="fas fa-print text-xs"></i>
            <span>{{ isAgentOnline ? 'Agent Online' : 'Agent Offline' }}</span>
          </div>

          <!-- Scale Status -->
          <div 
            :class="[
              'px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 text-xs font-bold transition-all shrink-0',
              (isAgentOnline && scaleStatus.connected) ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs' : 'bg-rose-50 text-rose-700 border-rose-200'
            ]"
            :title="(isAgentOnline && scaleStatus.connected) ? `Cân đang kết nối cổng ${scaleStatus.port}` : 'Cân chưa kết nối hoặc mất tín hiệu COM'"
          >
            <span class="relative flex h-2 w-2">
              <span v-if="isAgentOnline && scaleStatus.connected" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span :class="['relative inline-flex rounded-full h-2 w-2', (isAgentOnline && scaleStatus.connected) ? 'bg-emerald-500' : 'bg-rose-500']"></span>
            </span>
            <i class="fas fa-weight-scale text-xs"></i>
            <span>{{ (isAgentOnline && scaleStatus.connected) ? `Cân Online (${scaleStatus.port || 'COM'})` : 'Cân Mất Kết Nối' }}</span>
          </div>

          <!-- Actions -->
          <button @click="showSettingsModal = true" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer">
            <i class="fas fa-cog text-slate-500"></i>
            <span>Cài Đặt</span>
          </button>
          <button @click="switchCustomer" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs">
            <i class="fas fa-exchange-alt"></i>
            <span>Đổi Khách</span>
          </button>
          <router-link to="/admin" class="px-2.5 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs" title="Trang quản trị hệ thống (Admin)">
            <i class="fas fa-user-shield text-indigo-600"></i>
            <span>Admin</span>
          </router-link>
        </div>
      </header>

      <!-- Active Product & Batch Bar -->
      <section class="my-2 px-4 py-2.5 rounded-xl bg-slate-50/90 border border-slate-200/90 shadow-xs flex items-center justify-between gap-3 shrink-0">
        <div class="flex items-center gap-5 md:gap-7 flex-wrap">
          <div v-if="selectedProduct" class="flex items-center gap-2">
            <span class="text-xs uppercase tracking-wider font-bold text-slate-400">CPN:</span>
            <span class="font-black text-base md:text-lg text-slate-900 font-mono">
              {{ selectedProduct.item_name }}
            </span>
            <span class="px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 font-bold text-xs">
              {{ selectedProduct.packed_qty }} PCS
            </span>
          </div>

          <div v-if="selectedProduct" class="flex items-center gap-2 border-l border-slate-200 pl-5 font-mono">
            <template v-if="selectedProduct.template_type === 'erro_05'">
              <span class="text-xs uppercase font-bold text-slate-400 font-sans">Prefix:</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.pkg_prefix || 'MC220TW1' }}</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.factory_item_code || '-' }}</span>
            </template>
            <template v-else-if="selectedProduct.template_type === 'erro_04'">
              <span class="text-xs uppercase font-bold text-slate-400 font-sans">Carton ID:</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.carton_id_prefix || '-' }}...</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.mfr_pn || '-' }}</span>
            </template>
            <template v-else-if="selectedProduct.template_type === 'erro_03'">
              <span class="text-xs uppercase font-bold text-slate-400 font-sans">Supplier:</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.pkg_prefix || '1012665' }}</span>
            </template>
            <template v-else-if="selectedProduct.template_type === 'erro_02'">
              <span class="text-xs uppercase font-bold text-slate-400 font-sans">SSCC/P-N:</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.pkg_prefix || '37033907' }}</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.mfr_pn || '-' }}</span>
            </template>
            <template v-else>
              <span class="text-xs uppercase font-bold text-slate-400 font-sans">Mfr/Prefix:</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.mfr_pn || 'NYS5998' }}</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-slate-700">{{ selectedProduct.pkg_prefix || 'VHK0010237' }}</span>
            </template>
          </div>

          <div class="flex items-center gap-2 border-l border-slate-200 pl-5 font-mono">
            <span class="text-xs uppercase font-bold text-slate-400 font-sans">PO/LOT:</span>
            <template v-if="selectedProduct?.template_type === 'erro_05'">
              <span class="font-bold text-sm text-indigo-900">PO: {{ activePO || '(Tùy chọn)' }}</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-indigo-900">LOT: {{ activeLot || 'Tự động' }}</span>
            </template>
            <template v-else-if="selectedProduct?.template_type === 'erro_02'">
              <span class="font-bold text-xs text-slate-500 italic bg-slate-100 px-2 py-0.5 rounded border border-slate-200">Không áp dụng (Tem 2)</span>
            </template>
            <template v-else-if="selectedProduct?.template_type === 'erro_03'">
              <span class="font-bold text-sm text-indigo-900">PO: {{ activePO || '(Tùy chọn)' }}</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-indigo-900">LOT: {{ activeLot || '92607933' }}</span>
            </template>
            <template v-else>
              <span class="font-bold text-sm text-indigo-900">PO: {{ activePO || 'Chưa nhập' }}</span>
              <span class="text-slate-300">|</span>
              <span class="font-bold text-sm text-indigo-900">LOT: {{ activeLot || 'Chưa nhập' }}</span>
            </template>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <button 
            v-if="selectedProduct?.template_type !== 'erro_02'"
            @click="showBatchModal = true" 
            class="px-2.5 py-1 rounded-lg bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold transition-all flex items-center gap-1 shadow-xs cursor-pointer"
          >
            <i class="fas fa-edit text-indigo-500"></i>
            <span>Đổi PO/LOT</span>
          </button>
          <button @click="clearSelectedProduct" :disabled="!selectedProduct" class="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white text-xs font-bold transition-all flex items-center gap-1 shadow-xs shadow-indigo-600/20 cursor-pointer">
            <i class="fas fa-boxes"></i>
            <span>Đổi Mã Hàng</span>
          </button>
        </div>
      </section>

      <!-- Offline Warning Banner -->
      <div v-if="!isAgentOnline" class="mb-2 px-3.5 py-2 rounded-xl bg-rose-50 border border-rose-300 text-rose-800 text-xs font-semibold flex items-center justify-between gap-3 shadow-xs animate-in">
        <div class="flex items-center gap-2.5">
          <div class="w-6 h-6 rounded-lg bg-rose-500 text-white flex items-center justify-center shrink-0">
            <i class="fas fa-exclamation-triangle text-xs"></i>
          </div>
          <div>
            <span class="font-black text-rose-900">Chưa kết nối phần mềm Print Agent!</span>
            <span class="text-rose-700 ml-1.5 text-[11px]">
              Vui lòng bật phần mềm <strong>NY Print Agent</strong> trên máy tính hoặc kiểm tra cổng <code>{{ settings.agentUrl || 'http://127.0.0.1:8080' }}</code> trong Cài Đặt.
            </span>
          </div>
        </div>
        <button @click="pollScaleStatus" class="px-2.5 py-1 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-all shrink-0 cursor-pointer shadow-xs flex items-center gap-1">
          <i class="fas fa-rotate-right text-[10px]"></i>
          <span>Thử Lại</span>
        </button>
      </div>

      <!-- Template Missing Warning Banner (Pre-flight Check) -->
      <div v-if="settings.printMode !== 'centralized' && isAgentOnline && templateMissing" class="mb-2 px-3.5 py-2 rounded-xl bg-amber-50 border border-amber-300 text-amber-800 text-xs font-semibold flex items-center justify-between gap-3 shadow-xs animate-in">
        <div class="flex items-center gap-2.5">
          <div class="w-6 h-6 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0">
            <i class="fas fa-file-circle-exclamation text-xs"></i>
          </div>
          <div>
            <span class="font-black text-amber-900">Chưa có file mẫu tem trên máy trạm: <code>{{ templateFilename }}</code>!</span>
            <span class="text-amber-700 ml-1.5 text-[11px]">
              Vui lòng sao chép file <strong>{{ templateFilename }}</strong> vào thư mục <code>{{ settings.localTemplateDir || 'D:\\PAT\\Templates' }}</code> trên máy tính này.
            </span>
          </div>
        </div>
        <button @click="checkTemplateExists" class="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition-all shrink-0 cursor-pointer shadow-xs flex items-center gap-1">
          <i class="fas fa-rotate-right text-[10px]"></i>
          <span>Kiểm Tra Lại</span>
        </button>
      </div>

      <!-- Main Packing Station Cockpit Grid -->
      <main class="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0">
        <!-- Left: Live Scale Gauge & Action Controls (8 Cols) -->
        <div class="lg:col-span-8 flex flex-col justify-between h-full gap-2 min-h-0">
          <ScaleDigitalGauge
            :scaleReading="scaleReading"
            :scaleStatus="scaleStatus"
            :isAgentOnline="isAgentOnline"
            :toleranceResult="toleranceResult"
            :selectedProduct="selectedProduct"
            :isPrinting="isPrinting"
          />

          <ErroSerialControl
            :currentSNPreview="currentSNPreview"
          />

          <!-- Giant Primary Print Action Button -->
          <button
            @click="triggerWeighAndPrint"
            :disabled="isPrinting || !selectedProduct || labelPreviewErrors.length > 0 || (settings.printMode !== 'centralized' && templateMissing)"
            :class="[
              'w-full py-3 md:py-3.5 rounded-xl font-black text-base md:text-lg transition-all flex items-center justify-center gap-2 cursor-pointer shadow-md shrink-0',
              (settings.printMode !== 'centralized' && templateMissing)
                ? 'bg-amber-600 hover:bg-amber-700 active:scale-[0.99] text-white shadow-amber-600/20'
              : (toleranceResult.canPrint && labelPreviewErrors.length === 0 && (selectedProduct?.template_type === 'erro_02' || selectedProduct?.template_type === 'erro_03' || selectedProduct?.template_type === 'erro_05' || (activePO?.trim() && activeLot?.trim()))
                  ? 'bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white shadow-emerald-600/30'
                  : 'bg-rose-600 hover:bg-rose-700 active:scale-[0.99] text-white shadow-rose-600/20')
            ]"
          >
            <i v-if="isPrinting" class="fas fa-spinner fa-spin text-lg"></i>
            <i v-else-if="settings.printMode !== 'centralized' && templateMissing" class="fas fa-file-circle-exclamation text-lg"></i>
            <i v-else-if="toleranceResult.canPrint" class="fas fa-print text-lg"></i>
            <i v-else class="fas fa-triangle-exclamation text-lg"></i>
            <span>{{ isPrinting ? 'ĐANG GỬI LỆNH IN...' : ((settings.printMode !== 'centralized' && templateMissing) ? `THIẾU FILE TEM ${templateFilename} - KIỂM TRA LẠI` : (labelPreviewErrors.length ? `THIẾU DỮ LIỆU TEM - KIỂM TRA PREVIEW` : (toleranceResult.canPrint ? 'CÂN & IN TEM ERRO [F9]' : 'LỆCH DUNG SAI - BẤM ĐỂ XEM LỖI [F9]'))) }}</span>
          </button>
        </div>

        <!-- Right: Session Stats & Last Carton Info (4 Cols) -->
        <div class="lg:col-span-4 flex flex-col h-full gap-2 min-h-0 justify-between">
          <ErroLabelPrintPreview
            :product="selectedProduct"
            :carton-s-n="currentSNPreview"
            :po="activePO"
            :lot="activeLot"
            :now="previewTime"
            @validation-change="labelPreviewErrors = $event"
          />
        </div>
      </main>

      <!-- Modals -->
      <ErroBatchConfigModal
        :show="showBatchModal"
        :po="activePO"
        :lot="activeLot"
        :isTem3="(pendingProduct || selectedProduct)?.template_type === 'erro_03'"
        @close="cancelBatchConfig"
        @save="saveBatchConfig"
      />

      <SettingsModal 
        :show="showSettingsModal"
        @close="showSettingsModal = false"
      />

      <ScaleToleranceErrorModal
        :show="showToleranceErrorModal"
        :details="toleranceErrorDetails"
        @close="showToleranceErrorModal = false"
      />
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSettingsStore } from '../core/stores/settings';
import { useSystemStore } from '../core/stores/system';
import type { Product } from '../types/api';

import SettingsModal from '../features/settings/components/SettingsModal.vue';
import ScaleDigitalGauge from '../features/packing/weight_scale/components/ScaleDigitalGauge.vue';
import ErroSerialControl from '../features/packing/weight_scale/components/ErroSerialControl.vue';
import ErroLabelPrintPreview from '../features/packing/weight_scale/components/ErroLabelPrintPreview.vue';
import ScaleToleranceErrorModal from '../features/packing/weight_scale/components/ScaleToleranceErrorModal.vue';
import ErroFactoryPartNumberStep from '../features/packing/weight_scale/components/ErroFactoryPartNumberStep.vue';
import ErroBatchConfigModal from '../features/packing/weight_scale/components/ErroBatchConfigModal.vue';

import { useScaleStream } from '../features/packing/weight_scale/composables/useScaleStream';
import { useErroSerialNumber } from '../features/packing/weight_scale/composables/useErroSerialNumber';
import { useWeighAndPrint } from '../features/packing/weight_scale/composables/useWeighAndPrint';
import { useAgentHealth } from '../features/packing/composables/useAgentHealth';

const router = useRouter();
const settings = useSettingsStore();
const system = useSystemStore();

// Modals State
const showBatchModal = ref(false);
const showSettingsModal = ref(false);

// Active Selection State
const selectedProduct = ref<Product | null>(null);
const pendingProduct = ref<Product | null>(null);
const activePO = ref<string>(localStorage.getItem('erro_active_po') || '');
const activeLot = ref<string>(localStorage.getItem('erro_active_lot') || '');
const labelPreviewErrors = ref<string[]>([]);
const previewTime = ref(new Date());

// 1. Scale Stream Composable
const {
  isAgentOnline,
  scaleReading,
  scaleStatus,
  pollScaleStatus,
  startPolling,
  stopPolling,
} = useScaleStream(() => settings.agentUrl || 'http://127.0.0.1:8080');

// 2. S/N Sequence Composable (Strict Monotonic - ADR 0005)
const {
  currentSNPreview,
  fetchNextSN,
  advanceSequence,
} = useErroSerialNumber(selectedProduct);

// 3. Weigh & Print Orchestrator Composable (No Reprint - ADR 0005)
const {
  isPrinting,
  lastPackedCarton,
  showToleranceErrorModal,
  toleranceErrorDetails,
  toleranceResult,
  triggerWeighAndPrint,
} = useWeighAndPrint({
  selectedProduct,
  activePO,
  activeLot,
  isAgentOnline,
  scaleReading,
  scaleStatus,
  advanceSequence,
  notify: (msg, type) => system.showNotification(msg, type),
  getSettings: () => ({
    agentUrl: settings.agentUrl,
    printerName: settings.printerName,
    templatePath: settings.templatePath,
    stationId: settings.stationId,
    localTemplateDir: settings.localTemplateDir,
  }),
  openProductModal: () => system.showNotification('Vui lòng quét hoặc nhập Factory P/N trước khi in', 'warning'),
  openBatchModal: () => { showBatchModal.value = true; },
});

// 4. Agent & Template Health Composable
const {
  templateMissing,
  templateFilename,
  checkTemplateExists,
} = useAgentHealth({
  settings: computed(() => ({
    printMode: settings.printMode || 'local',
    agentUrl: settings.agentUrl || 'http://127.0.0.1:8080',
    localTemplateDir: settings.localTemplateDir || 'D:\\PAT\\Templates',
  })),
  currentProduct: selectedProduct,
});

watch([selectedProduct, isAgentOnline], () => {
  if (isAgentOnline.value) {
    checkTemplateExists();
  }
});

watch(currentSNPreview, () => {
  previewTime.value = new Date();
});

watch(lastPackedCarton, async (carton) => {
  if (carton) await fetchNextSN();
});

// Navigation & Config Actions
const switchCustomer = () => {
  localStorage.removeItem('selected_customer');
  router.push('/');
};

const clearPackingSession = () => {
  activePO.value = '';
  activeLot.value = '';
  localStorage.removeItem('erro_active_po');
  localStorage.removeItem('erro_active_lot');
};

const activateProduct = (product: Product) => {
  selectedProduct.value = product;
  if (product.template_type === 'erro_03' && !activeLot.value) {
    activeLot.value = '92607933';
  }
  system.showNotification(`Đã chọn sản phẩm ${product.item_name}`, 'success');
  fetchNextSN();
};

const saveBatchConfig = (payload: { po: string; lot: string }) => {
  activePO.value = payload.po;
  activeLot.value = payload.lot;
  localStorage.setItem('erro_active_po', activePO.value);
  localStorage.setItem('erro_active_lot', activeLot.value);
  showBatchModal.value = false;
  if (pendingProduct.value) {
    const product = pendingProduct.value;
    pendingProduct.value = null;
    activateProduct(product);
  }
  system.showNotification('Đã cập nhật PO & LOT thành công', 'success');
};

const cancelBatchConfig = () => {
  showBatchModal.value = false;
  if (pendingProduct.value) {
    pendingProduct.value = null;
    clearPackingSession();
  }
};

const resolveFactoryPartNumber = (product: Product) => {
  clearPackingSession();
  if (product.template_type === 'erro_01' || product.template_type === 'erro_04') {
    pendingProduct.value = product;
    showBatchModal.value = true;
    return;
  }
  activateProduct(product);
};

const clearSelectedProduct = () => {
  selectedProduct.value = null;
  pendingProduct.value = null;
  clearPackingSession();
  localStorage.removeItem('erro_selected_product_id');
  system.showNotification('Hãy quét hoặc nhập Factory P/N để chọn mã hàng mới', 'info');
};

// Global Hotkeys Listener (F9, Enter, Esc)
const handleKeyDown = (event: KeyboardEvent) => {
  if (showToleranceErrorModal.value) {
    if (['Enter', 'Escape', ' ', 'Space'].includes(event.key) || ['Enter', 'Escape', 'Space'].includes(event.code)) {
      event.preventDefault();
      showToleranceErrorModal.value = false;
      return;
    }
  }

  if (event.key === 'F9' || event.code === 'F9' || event.keyCode === 120 || event.which === 120) {
    event.preventDefault();
    triggerWeighAndPrint();
  }
};

onMounted(() => {
  localStorage.removeItem('erro_selected_product_id');
  startPolling();
  window.addEventListener('keydown', handleKeyDown, true);
});

onUnmounted(() => {
  stopPolling();
  window.removeEventListener('keydown', handleKeyDown, true);
});
</script>
