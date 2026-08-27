import { ref, computed, type Ref } from 'vue';
import packingApi from '../../api';
import printApi from '../../../print/api';
import { evaluateScaleTolerance, type ScaleToleranceResult } from '../../utils/scaleTolerance';
import type { Product, Carton, ScaleReading, ScaleStatus } from '../../../../types/api';

export interface WeighAndPrintSettings {
  agentUrl?: string;
  printerName?: string;
  templatePath?: string;
  stationId?: string;
  localTemplateDir?: string;
}

export interface UseWeighAndPrintOptions {
  selectedProduct: Ref<Product | null>;
  activePO: Ref<string>;
  activeLot: Ref<string>;
  isAgentOnline: Ref<boolean>;
  scaleReading: Ref<ScaleReading>;
  scaleStatus: Ref<ScaleStatus>;
  isAutoSN: Ref<boolean>;
  manualSequence: Ref<number | null>;
  snCheckError: Ref<string>;
  advanceSequence: () => void;
  notify?: (message: string, type: 'info' | 'success' | 'warning' | 'error') => void;
  getSettings?: () => WeighAndPrintSettings;
  openProductModal?: () => void;
  openBatchModal?: () => void;
}

export function useWeighAndPrint(options: UseWeighAndPrintOptions) {
  const {
    selectedProduct,
    activePO,
    activeLot,
    isAgentOnline,
    scaleReading,
    scaleStatus,
    isAutoSN,
    manualSequence,
    snCheckError,
    advanceSequence,
    notify,
    getSettings = (): WeighAndPrintSettings => ({}),
    openProductModal,
    openBatchModal,
  } = options;

  const isPrinting = ref(false);
  const sessionPackedCount = ref<number>(
    Number(sessionStorage.getItem('a11_session_count') || sessionStorage.getItem('ux_session_count') || '0')
  );
  const lastPackedCarton = ref<Carton | null>(null);

  const showToleranceErrorModal = ref(false);
  const toleranceErrorDetails = ref<{
    status: string;
    title: string;
    message: string;
    currentWeight: number;
    minWeight: number;
    targetWeight: number;
    maxWeight: number;
  } | null>(null);

  const getToleranceTitle = (status: string) => {
    switch (status) {
      case 'READY': return 'ĐẠT CHUẨN TRỌNG LƯỢNG';
      case 'UNSTABLE': return 'CÂN CHƯA ỔN ĐỊNH';
      case 'UNDERWEIGHT': return 'THIẾU TRỌNG LƯỢNG';
      case 'OVERWEIGHT': return 'THỪA TRỌNG LƯỢNG';
      case 'DISCONNECTED': return !isAgentOnline.value ? 'CHƯA BẬT PRINT AGENT' : 'CHƯA KẾT NỐI CÂN';
      default: return 'CHƯA KẾT NỐI CÂN';
    }
  };

  const toleranceResult = computed<ScaleToleranceResult>(() => {
    return evaluateScaleTolerance({
      isConnected: isAgentOnline.value && scaleStatus.value.connected,
      currentWeight: scaleReading.value.weight,
      isStable: scaleReading.value.is_stable,
      product: selectedProduct.value ? {
        min_weight: selectedProduct.value.min_weight ?? 12.300,
        target_weight: selectedProduct.value.target_weight ?? 12.500,
        max_weight: selectedProduct.value.max_weight ?? 12.700,
      } : null,
    });
  });

  const calculateGaugePercent = (currentWeight: number): number => {
    if (!isAgentOnline.value || !scaleStatus.value.connected) return 50;
    const min = selectedProduct.value?.min_weight ?? 0.150;
    const max = selectedProduct.value?.max_weight ?? 0.200;
    const range = max - min;
    if (range <= 0) return 50;

    const gaugeMin = min - 0.25 * range;
    const gaugeMax = max + 0.25 * range;
    const percent = ((currentWeight - gaugeMin) / (gaugeMax - gaugeMin)) * 100;
    return Math.min(Math.max(percent, 2), 98);
  };

  const triggerWeighAndPrint = async () => {
    if (!selectedProduct.value) {
      notify?.('Vui lòng chọn sản phẩm trước khi in', 'warning');
      openProductModal?.();
      return;
    }

    if (!activePO.value || !activeLot.value) {
      notify?.('Vui lòng nhập PO và LOT trước khi in', 'warning');
      openBatchModal?.();
      return;
    }

    if (!toleranceResult.value.canPrint) {
      toleranceErrorDetails.value = {
        status: toleranceResult.value.status,
        title: getToleranceTitle(toleranceResult.value.status),
        message: toleranceResult.value.message,
        currentWeight: scaleReading.value.weight,
        minWeight: selectedProduct.value?.min_weight ?? 0.150,
        targetWeight: selectedProduct.value?.target_weight ?? 0.180,
        maxWeight: selectedProduct.value?.max_weight ?? 0.200,
      };
      showToleranceErrorModal.value = true;
      return;
    }

    if (!isAutoSN.value) {
      if (!manualSequence.value || manualSequence.value <= 0) {
        notify?.('Vui lòng nhập số thùng hợp lệ (> 0)', 'warning');
        return;
      }
      if (snCheckError.value) {
        notify?.(snCheckError.value, 'error');
        return;
      }
    }

    if (isPrinting.value) return;

    isPrinting.value = true;
    const currentWeight = scaleReading.value.weight;
    const settings = getSettings();

    try {
      // 1. Call Backend API to Allocate A11 SN and generate A11 BTXML
      const res = await packingApi.weighPackCarton({
        product_id: selectedProduct.value.id,
        weight: currentWeight,
        po_number: activePO.value,
        lot_number: activeLot.value,
        printer_name: settings.printerName || undefined,
        template_path: settings.templatePath || undefined,
        station_id: settings.stationId || undefined,
        custom_sn: isAutoSN.value ? undefined : (manualSequence.value || undefined),
      });

      const newCarton = res.data;
      const btxmlContent = (newCarton as any).btxml;

      if (!btxmlContent) {
        throw new Error('Backend did not return BTXML payload');
      }

      // 2. Send BTXML to Print Agent
      const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
      const printResult = await printApi.agentPrint(
        agentUrl,
        btxmlContent,
        settings.printerName || undefined,
        settings.localTemplateDir || undefined
      );

      // If PDF export, trigger automatic download / view
      if (printResult?.type === 'pdf' && printResult?.data) {
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${printResult.data}`;
        link.download = `${newCarton.carton_sn || 'label'}.pdf`;
        link.click();
      }

      // 3. Confirm SUCCESS status on backend
      try {
        await printApi.updateCartonStatus(newCarton.id, 'SUCCESS');
        newCarton.status = 'SUCCESS';
      } catch (e) {
        console.warn('Status confirmation warning:', e);
      }

      // 4. Update session and last carton
      lastPackedCarton.value = newCarton;
      sessionPackedCount.value += 1;
      sessionStorage.setItem('a11_session_count', String(sessionPackedCount.value));
      sessionStorage.setItem('ux_session_count', String(sessionPackedCount.value));

      // 5. Advance serial number counter
      advanceSequence();

      notify?.(`Đã in thành công tem thùng: ${newCarton.carton_sn}`, 'success');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.error || err.message || 'Lỗi không xác định khi in';
      notify?.(`In thất bại: ${errorMsg}`, 'error');
    } finally {
      isPrinting.value = false;
    }
  };

  const handleEmergencyReprint = async (carton: Carton) => {
    const settings = getSettings();
    try {
      isPrinting.value = true;
      const res = await printApi.reprintCarton(
        carton.id,
        settings.templatePath || '',
        settings.printerName || ''
      );
      const reprintCarton = res.data;
      const btxml = (reprintCarton as any).btxml;

      if (btxml) {
        const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
        const printResult = await printApi.agentPrint(agentUrl, btxml, settings.printerName, settings.localTemplateDir);
        if (printResult?.type === 'pdf' && printResult?.data) {
          const link = document.createElement('a');
          link.href = `data:application/pdf;base64,${printResult.data}`;
          link.download = `Reprint_${carton.carton_sn}.pdf`;
          link.click();
        }
        notify?.(`In lại thành công tem thùng: ${carton.carton_sn}`, 'success');
        return true;
      } else {
        throw new Error('No BTXML returned for reprint');
      }
    } catch (err: any) {
      notify?.(`In lại thất bại: ${err.response?.data?.error || err.message}`, 'error');
      return false;
    } finally {
      isPrinting.value = false;
    }
  };

  const reprintLastCarton = async () => {
    if (!lastPackedCarton.value) return;
    await handleEmergencyReprint(lastPackedCarton.value);
  };

  const resetSessionCount = () => {
    if (confirm('Bạn có chắc muốn đặt lại bộ đếm số thùng trong ca về 0?')) {
      sessionPackedCount.value = 0;
      sessionStorage.setItem('a11_session_count', '0');
      sessionStorage.setItem('ux_session_count', '0');
    }
  };

  return {
    isPrinting,
    sessionPackedCount,
    lastPackedCarton,
    showToleranceErrorModal,
    toleranceErrorDetails,
    toleranceResult,
    calculateGaugePercent,
    triggerWeighAndPrint,
    handleEmergencyReprint,
    reprintLastCarton,
    resetSessionCount,
    getToleranceTitle,
  };
}
