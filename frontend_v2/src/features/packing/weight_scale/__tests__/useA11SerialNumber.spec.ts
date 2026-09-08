import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ref } from 'vue';
import { useA11SerialNumber } from '../composables/useA11SerialNumber';
import catalogApi from '../../../catalog/api';
import type { Product } from '../../../../types/api';

vi.mock('../../../catalog/api', () => ({
  default: {
    getNextSN: vi.fn(),
  },
}));

describe('useA11SerialNumber Composable (Strict Monotonic Sequence - ADR 0005)', () => {
  const mockProduct = ref<Product | null>({
    id: 10,
    customer_id: 2,
    item_name: 'A11-Product-01',
    packed_qty: 190,
    pkg_prefix: 'VHK0010237',
    template_type: 'a11',
    allow_partial: 0,
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('computes S/N preview with default fallback format and auto mode', () => {
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

  it('strictly advances sequence automatically on advanceSequence without manual mode', () => {
    const { autoSequence, advanceSequence, isAutoSN } = useA11SerialNumber(mockProduct);

    expect(isAutoSN.value).toBe(true);
    autoSequence.value = 10;
    advanceSequence();
    expect(autoSequence.value).toBe(11);
  });
});
