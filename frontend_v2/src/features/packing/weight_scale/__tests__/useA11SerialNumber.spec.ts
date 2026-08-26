import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ref } from 'vue';
import { useA11SerialNumber } from '../composables/useA11SerialNumber';
import catalogApi from '../../../catalog/api';
import printApi from '../../../print/api';
import type { Product } from '../../../../types/api';

vi.mock('../../../catalog/api', () => ({
  default: {
    getNextSN: vi.fn(),
  },
}));

vi.mock('../../../print/api', () => ({
  default: {
    searchCarton: vi.fn(),
  },
}));

describe('useA11SerialNumber Composable', () => {
  const mockProduct = ref<Product | null>({
    id: 10,
    customer_id: 2,
    item_name: 'A11-Product-01',
    packed_qty: 190,
    pkg_prefix: 'VHK0010237',
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('computes S/N preview with default fallback format', () => {
    const { currentSNPreview, isAutoSN } = useA11SerialNumber(mockProduct);

    expect(isAutoSN.value).toBe(true);
    expect(currentSNPreview.value).toMatch(/^VHK0010237\d{4}000001$/);
  });

  it('updates sequence and YYMM when fetchNextSN succeeds', async () => {
    vi.mocked(catalogApi.getNextSN).mockResolvedValueOnce({
      data: { next_seq: 42, yymm: '2608' },
    } as any);

    const { fetchNextSN, currentSNPreview, autoSequence } = useA11SerialNumber(mockProduct);

    await fetchNextSN();

    expect(autoSequence.value).toBe(42);
    expect(currentSNPreview.value).toBe('VHK00102372608000042');
  });

  it('switches between Auto and Manual S/N mode', () => {
    const { isAutoSN, toggleSNMode, manualSequence } = useA11SerialNumber(mockProduct);

    expect(isAutoSN.value).toBe(true);
    toggleSNMode();
    expect(isAutoSN.value).toBe(false);
    expect(manualSequence.value).toBe(1);

    toggleSNMode();
    expect(isAutoSN.value).toBe(true);
  });

  it('advances sequence correctly in auto and manual mode', () => {
    const { isAutoSN, autoSequence, manualSequence, advanceSequence, toggleSNMode } = useA11SerialNumber(mockProduct);

    autoSequence.value = 10;
    advanceSequence();
    expect(autoSequence.value).toBe(11);

    toggleSNMode(); // switch to manual
    manualSequence.value = 50;
    advanceSequence();
    expect(manualSequence.value).toBe(51);
  });

  it('detects duplicate manual SN when searchCarton returns existing record', async () => {
    vi.useFakeTimers();
    vi.mocked(printApi.searchCarton).mockResolvedValueOnce({
      data: { id: 99, carton_sn: 'VHK00102372608000085' },
    } as any);

    const { toggleSNMode, manualSequence, snCheckError, checkManualSN } = useA11SerialNumber(mockProduct);

    toggleSNMode();
    manualSequence.value = 85;
    checkManualSN();

    await vi.advanceTimersByTimeAsync(350);

    expect(printApi.searchCarton).toHaveBeenCalled();
    expect(snCheckError.value).toContain('đã tồn tại');
    vi.useRealTimers();
  });
});
