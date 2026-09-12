import { ref, computed, type Ref } from 'vue';
import catalogApi from '../../../catalog/api';
import type { Product } from '../../../../types/api';

/**
 * Composable for managing Customer Erro carton serial numbers.
 * Per ADR 0006, Customer Erro strictly mandates automatic, monotonic serial numbers.
 * Manual sequence editing and toggling are completely removed.
 */
export function useErroSerialNumber(selectedProduct: Ref<Product | null>) {
  const isAutoSN = ref<boolean>(true);
  const autoSequence = ref<number>(1);
  const currentYYMM = ref<string>('');

  const fetchNextSN = async () => {
    if (!selectedProduct.value) return;
    try {
      const res = await catalogApi.getNextSN(selectedProduct.value.id);
      if (res?.data) {
        autoSequence.value = res.data.next_seq || 1;
        currentYYMM.value = res.data.yymm || '';
      }
    } catch (err) {
      console.warn('Could not fetch next S/N sequence:', err);
    }
  };

  const currentSNPreview = computed<string>(() => {
    if (!selectedProduct.value) return '-';
    if (selectedProduct.value.template_type === 'erro_03') {
      const supplierCode = selectedProduct.value.pkg_prefix || '1012665';
      const now = new Date();
      const yy = String(now.getFullYear()).slice(-2);
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const dd = String(now.getDate()).padStart(2, '0');
      const seqStr = String(autoSequence.value).padStart(4, '0');
      return `${supplierCode}${yy}${mm}${dd}${seqStr}`;
    }
    if (selectedProduct.value.template_type === 'erro_02') {
      const prefix = selectedProduct.value.pkg_prefix || '37033907';
      const seqStr = String(autoSequence.value).padStart(7, '0');
      return `(00) 0 ${prefix} ${seqStr}`;
    }
    const prefix = selectedProduct.value.pkg_prefix || 'VHK0010237';
    let yymm = currentYYMM.value;
    if (!yymm || yymm.length !== 4) {
      const now = new Date();
      const yy = String(now.getFullYear()).slice(-2);
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      yymm = `${yy}${mm}`;
    }
    return `${prefix}${yymm}${String(autoSequence.value).padStart(6, '0')}`;
  });

  const advanceSequence = () => {
    autoSequence.value += 1;
  };

  return {
    isAutoSN,
    autoSequence,
    currentYYMM,
    currentSNPreview,
    fetchNextSN,
    advanceSequence,
  };
}
