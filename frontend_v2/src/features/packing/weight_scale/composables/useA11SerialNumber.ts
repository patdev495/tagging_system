import { ref, computed, type Ref } from 'vue';
import catalogApi from '../../../catalog/api';
import printApi from '../../../print/api';
import type { Product } from '../../../../types/api';

export function useA11SerialNumber(selectedProduct: Ref<Product | null>) {
  const isAutoSN = ref<boolean>(true);
  const autoSequence = ref<number>(1);
  const manualSequence = ref<number | null>(null);
  const snCheckError = ref<string>('');
  const currentYYMM = ref<string>('');

  const fetchNextSN = async () => {
    if (!selectedProduct.value) return;
    try {
      const res = await catalogApi.getNextSN(selectedProduct.value.id);
      if (res?.data) {
        autoSequence.value = res.data.next_seq || 1;
        currentYYMM.value = res.data.yymm || '';
        if (manualSequence.value === null || isAutoSN.value) {
          manualSequence.value = autoSequence.value;
        }
      }
    } catch (err) {
      console.warn('Could not fetch next S/N sequence:', err);
    }
  };

  const currentSNPreview = computed<string>(() => {
    if (!selectedProduct.value) return '-';
    const prefix = selectedProduct.value.pkg_prefix || 'VHK0010237';
    let yymm = currentYYMM.value;
    if (!yymm || yymm.length !== 4) {
      const now = new Date();
      const yy = String(now.getFullYear()).slice(-2);
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      yymm = `${yy}${mm}`;
    }
    const seq = isAutoSN.value ? autoSequence.value : (manualSequence.value || 1);
    return `${prefix}${yymm}${String(seq).padStart(6, '0')}`;
  });

  const toggleSNMode = () => {
    if (isAutoSN.value) {
      isAutoSN.value = false;
      manualSequence.value = autoSequence.value;
      checkManualSN();
    } else {
      isAutoSN.value = true;
      snCheckError.value = '';
      fetchNextSN();
    }
  };

  let checkSNTimer: any = null;
  const checkManualSN = () => {
    snCheckError.value = '';
    if (!manualSequence.value || manualSequence.value <= 0) {
      snCheckError.value = 'Số thùng phải lớn hơn 0';
      return;
    }
    clearTimeout(checkSNTimer);
    checkSNTimer = setTimeout(async () => {
      try {
        const sn = currentSNPreview.value;
        const res = await printApi.searchCarton(sn);
        if (res.data && res.data.id) {
          snCheckError.value = `Sê-ri ${sn} đã tồn tại trong lịch sử!`;
        }
      } catch {
        // Not found is clean/valid
        snCheckError.value = '';
      }
    }, 300);
  };

  const advanceSequence = () => {
    if (isAutoSN.value) {
      autoSequence.value += 1;
    } else {
      manualSequence.value = (manualSequence.value || 1) + 1;
      checkManualSN();
    }
  };

  return {
    isAutoSN,
    autoSequence,
    manualSequence,
    snCheckError,
    currentYYMM,
    currentSNPreview,
    fetchNextSN,
    toggleSNMode,
    checkManualSN,
    advanceSequence,
  };
}
