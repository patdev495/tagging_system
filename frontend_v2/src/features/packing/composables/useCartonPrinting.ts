import { ref, type Ref } from 'vue';
import { useI18n } from 'vue-i18n';
import packingApi from '../api';
import printApi from '../../print/api';
import { resolveCartonTemplatePath } from '../../print/utils/emergencyPrint';
import type { Product, Carton, JobOrderSlot } from '../../../types/api';

export interface UseCartonPrintingOptions {
  settings: any;
  system: any;
  currentProduct: Ref<Product | null>;
  jobOrder: Ref<string>;
  selectedSlotId: Ref<number | null>;
  cartonOrigin: Ref<string>;
  customSN: Ref<string>;
  customYYMM: Ref<string>;
  isSNManual: Ref<boolean>;
  snPreview: Ref<string>;
  snExists: Ref<boolean>;
  scannedItems: Ref<string[]>;
  jobOrderSlots: Ref<JobOrderSlot[]>;
  lastCarton: Ref<(Carton & { status?: string, items?: { item_sn: string }[] }) | null>;
  backupScannedItems: Ref<string[]>;
  isRescanMode: Ref<boolean>;
  rescanCartonSN: Ref<string>;
  showVerificationModal: Ref<boolean>;
  cartonToVerify: Ref<(Carton & { status?: string, items?: { item_sn: string }[] }) | null>;
  playSuccessSound: () => void;
  stopAgentPolling: () => void;
  resetSession: () => void;
  selectSlot: (slot: JobOrderSlot, confirmDiscard?: boolean) => void;
  focusScan: () => void;
  hadJobOrder: Ref<boolean>;
  savedSessionState: Ref<any>;
  currentStep: Ref<number>;
  cartonNumberStr: Ref<string>;
  suggestedSNPreview: Ref<string>;
  awaitingNext: Ref<boolean>;
}

export function useCartonPrinting(options: UseCartonPrintingOptions) {
  const { t } = useI18n();
  const isProcessing = ref<boolean>(false);
  const agentErrorMessage = ref<string>('');

  const handlePrintExecution = async (
    cartonId: number,
    _cartonSn: string,
    skipStatusUpdate = false,
    templatePathOverride = ''
  ): Promise<string> => {
    try {
      const templatePath = templatePathOverride || resolveCartonTemplatePath(null, options.currentProduct.value) || options.settings.templatePath || '';
      if (options.settings.printMode === 'local') {
        const resXml = await printApi.download_carton_btxml(cartonId, templatePath);
        const xmlContent = resXml.data;
        
        const result = await printApi.agentPrint(
          options.settings.agentUrl, 
          xmlContent, 
          options.settings.printerName,
          options.settings.localTemplateDir
        );
        
        if (result.success) {
          if (result.type === 'pdf' && result.data) {
            const link = document.createElement('a');
            link.href = `data:application/pdf;base64,${result.data}`;
            link.download = `Label_${_cartonSn}.pdf`;
            link.click();
          }
          if (!skipStatusUpdate) await printApi.updateCartonStatus(cartonId, 'PRINTED');
          return 'Success';
        } else {
          return result.message || 'Agent failed to print';
        }
      } else {
        const res = await printApi.serverPrint(cartonId, options.settings.printerName || undefined, templatePath || undefined);
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
      return typeof rawMsg === 'object' ? JSON.stringify(rawMsg) : String(rawMsg);
    }
  };

  const finalizeCarton = async (isRetry = false) => {
    if (!options.currentProduct.value) return;
    if (isProcessing.value && !isRetry) return;
    isProcessing.value = true;
    agentErrorMessage.value = '';
    try {
      let cartonId: number, cartonSn: string;
      if (isRetry && options.lastCarton.value?.id) {
        const res = await printApi.reprintCarton(options.lastCarton.value.id, options.settings.templatePath || '', options.settings.printerName);
        cartonId = res.data.id;
        cartonSn = res.data.carton_sn;
        options.lastCarton.value = { ...res.data, status: 'PRINTING' };
      } else if (options.isRescanMode.value && options.rescanCartonSN.value) {
        const items = [...options.scannedItems.value];
        const res = await packingApi.rescanCarton({ carton_sn: options.rescanCartonSN.value, items });
        cartonId = res.data.id;
        cartonSn = res.data.carton_sn;
        options.lastCarton.value = { ...res.data, status: 'PRINTING' };
      } else {
        if (options.snExists.value) {
          options.system.showNotification(t('packing.sn_exists', 'Mã sê-ri thùng đã tồn tại!'), 'error');
          isProcessing.value = false;
          return;
        }
        const items = [...options.scannedItems.value];
        if (items.length === 0) {
          options.system.showNotification(t('packing.no_items', 'Chưa có sản phẩm nào được quét!'), 'error');
          isProcessing.value = false;
          return;
        }
        if (!options.jobOrder.value || !options.selectedSlotId.value) {
          options.system.showNotification(t('packing.enter_job_order', 'Vui lòng chọn số thùng trước khi in!'), 'error');
          isProcessing.value = false;
          return;
        }
        
        options.lastCarton.value = { status: 'PRINTING', carton_sn: options.snPreview.value } as any;

        const res = await packingApi.createCarton({ 
          product_id: options.currentProduct.value.id, 
          items,
          job_order: options.jobOrder.value,
          slot_id: options.selectedSlotId.value,
          custom_sn: options.isSNManual.value ? parseInt(options.customSN.value) : undefined,
          carton_origin: options.cartonOrigin.value,
          custom_yymm: options.customYYMM.value || undefined
        });
        cartonId = res.data.id;
        cartonSn = res.data.carton_sn;
        options.lastCarton.value = { ...res.data, status: 'PRINTING' };
        options.backupScannedItems.value = items;
      }

      if (!cartonId) throw new Error('Invalid Carton ID received from server');

      const printResult = await handlePrintExecution(cartonId, cartonSn);
      if (printResult === 'Success') {
        if (options.lastCarton.value) options.lastCarton.value.status = 'PRINTED';
        options.cartonToVerify.value = options.lastCarton.value;
        options.showVerificationModal.value = true;
        options.system.showNotification(t('packing.carton_printed', { sn: cartonSn }), 'success');
      } else { 
        if (options.lastCarton.value) options.lastCarton.value.status = 'FAILED'; 
        agentErrorMessage.value = printResult; 
        options.system.showNotification(t('packing.print_failed', { error: printResult }), 'error'); 
      }
    } catch (err: any) {
      console.error(err);
      if (options.lastCarton.value && !isRetry) options.lastCarton.value.status = 'FAILED';
      let msg = err.response?.data?.detail || err.message || t('packing.server_error');
      if (msg === 'AGENT_CONNECTION_FAILED') msg = t('packing.agent_offline');
      options.system.showNotification(msg, 'error');
    } finally {
      isProcessing.value = false;
    }
  };

  const confirmVerification = async (verifiedCarton?: Carton) => {
    const target = verifiedCarton || options.cartonToVerify.value;
    if (!target) return;
    try {
      await printApi.updateCartonStatus(target.id, 'SUCCESS');
      options.playSuccessSound();
      
      if (options.lastCarton.value && options.lastCarton.value.id === target.id) {
        options.lastCarton.value.status = 'SUCCESS';
      }
      
      const cartonSn = target.carton_sn;
      const matchedSlot = options.jobOrderSlots.value.find(s => s.carton_sn === cartonSn);
      if (matchedSlot) {
        matchedSlot.status = 'SCANNED';
        matchedSlot.carton_id = target.id;
        matchedSlot.scanned_at = new Date().toISOString();
      }
      
      options.awaitingNext.value = true;
      options.showVerificationModal.value = false;
      options.cartonToVerify.value = null;
      
      options.system.showNotification(t('packing.verification_success', { sn: cartonSn }), 'success');
      
      if (options.isRescanMode.value) {
        options.isRescanMode.value = false;
        options.rescanCartonSN.value = '';
        options.stopAgentPolling();
        if (!options.hadJobOrder.value) options.resetSession();
        else {
          if (options.savedSessionState.value) {
            const s = options.savedSessionState.value;
            options.currentStep.value = s.currentStep;
            options.selectedSlotId.value = s.selectedSlotId;
            options.cartonNumberStr.value = s.cartonNumberStr;
            options.customSN.value = s.customSN;
            options.customYYMM.value = s.customYYMM;
            options.isSNManual.value = s.isSNManual;
            options.scannedItems.value = s.scannedItems;
            options.cartonOrigin.value = s.cartonOrigin;
            options.jobOrder.value = s.jobOrder;
            options.currentProduct.value = s.currentProduct;
            options.savedSessionState.value = null;
          }
          options.awaitingNext.value = false;
          options.focusScan();
        }
        return;
      }
      
      const nextPending = options.jobOrderSlots.value.find(s => s.status === 'PENDING');
      if (nextPending) {
        options.awaitingNext.value = true;
        options.focusScan();
      } else {
        options.awaitingNext.value = false;
        options.selectedSlotId.value = null;
        options.cartonNumberStr.value = '';
        options.customSN.value = '';
        options.suggestedSNPreview.value = '';
        options.customYYMM.value = '';
        options.isSNManual.value = false;
        options.system.showNotification('Đã quét xong toàn bộ số thùng của công lệnh!', 'success');
      }
    } catch (err: any) {
      console.error(err);
      options.system.showNotification(t('packing.update_status_failed', 'Cập nhật trạng thái thùng thất bại!'), 'error');
    }
  };

  const handleEmergencyReprint = async (carton: Carton) => {
    if (!carton.id) {
      options.system.showNotification('Invalid Carton ID', 'error');
      return;
    }
    try {
      const res = await printApi.reprintCarton(carton.id, options.settings.templatePath || '', options.settings.printerName);
      const newCarton = res.data;
      if (!newCarton?.id) throw new Error('Failed to create reprint record');

      const printResult = await handlePrintExecution(newCarton.id, newCarton.carton_sn, true, resolveCartonTemplatePath(carton));
      if (printResult === 'Success') { 
        options.system.showNotification(`Reprint successful: ${carton.carton_sn}`, 'success'); 
        return true;
      } else {
        options.system.showNotification('Reprint failed: ' + printResult, 'error');
        return false;
      }
    } catch (err: any) {
      options.system.showNotification('Reprint error: ' + (err.response?.data?.detail || err.message), 'error');
      return false;
    }
  };

  return {
    isProcessing,
    agentErrorMessage,
    handlePrintExecution,
    finalizeCarton,
    confirmVerification,
    handleEmergencyReprint,
  };
}
