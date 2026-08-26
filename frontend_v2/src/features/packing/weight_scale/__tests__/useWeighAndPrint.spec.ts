import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ref } from 'vue';
import { useWeighAndPrint } from '../composables/useWeighAndPrint';
import packingApi from '../../api';
import printApi from '../../../print/api';
import type { Product, ScaleReading, ScaleStatus } from '../../../../types/api';

vi.mock('../../api', () => ({
  default: {
    weighPackCarton: vi.fn(),
  },
}));

vi.mock('../../../print/api', () => ({
  default: {
    agentPrint: vi.fn(),
    updateCartonStatus: vi.fn(),
    reprintCarton: vi.fn(),
  },
}));

describe('useWeighAndPrint Composable', () => {
  const selectedProduct = ref<Product | null>({
    id: 10,
    customer_id: 2,
    item_name: 'A11-Standard',
    packed_qty: 190,
    pkg_prefix: 'VHK0010237',
    template_type: 'a11',
    allow_partial: 0,
    min_weight: 12.3,
    target_weight: 12.5,
    max_weight: 12.7,
  });

  const activePO = ref('PO-2026-001');
  const activeLot = ref('LOT-9988');
  const isAgentOnline = ref(true);
  const scaleReading = ref<ScaleReading>({
    weight: 12.502,
    unit: 'kg',
    is_stable: true,
    is_tare: false,
    is_net: false,
  });
  const scaleStatus = ref<ScaleStatus>({
    connected: true,
    port: 'COM3',
    baudrate: 9600,
    is_streaming: true,
  });
  const isAutoSN = ref(true);
  const manualSequence = ref<number | null>(null);
  const snCheckError = ref('');
  const advanceSequence = vi.fn();
  const notify = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('evaluates tolerance correctly as READY when weight is within tolerance and stable', () => {
    const { toleranceResult } = useWeighAndPrint({
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
      getSettings: () => ({ agentUrl: 'http://127.0.0.1:8080' }),
    });

    expect(toleranceResult.value.status).toBe('READY');
    expect(toleranceResult.value.canPrint).toBe(true);
  });

  it('blocks printing and opens error modal when tolerance fails (e.g. underweight)', async () => {
    scaleReading.value.weight = 10.0; // underweight

    const { toleranceResult, triggerWeighAndPrint, showToleranceErrorModal, toleranceErrorDetails } = useWeighAndPrint({
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
      getSettings: () => ({ agentUrl: 'http://127.0.0.1:8080' }),
    });

    expect(toleranceResult.value.canPrint).toBe(false);

    await triggerWeighAndPrint();

    expect(showToleranceErrorModal.value).toBe(true);
    expect(toleranceErrorDetails.value?.status).toBe('UNDERWEIGHT');
    expect(packingApi.weighPackCarton).not.toHaveBeenCalled();
  });

  it('executes full weigh & print flow when conditions are valid', async () => {
    scaleReading.value.weight = 12.505;

    vi.mocked(packingApi.weighPackCarton).mockResolvedValueOnce({
      data: {
        id: 123,
        carton_sn: 'VHK00102372608000001',
        weight: 12.505,
        status: 'PENDING',
        btxml: '<XMLScript Version="2.0"></XMLScript>',
      },
    } as any);

    vi.mocked(printApi.agentPrint).mockResolvedValueOnce({
      type: 'raw',
      status: 'success',
    } as any);

    vi.mocked(printApi.updateCartonStatus).mockResolvedValueOnce({} as any);

    const { triggerWeighAndPrint, lastPackedCarton, sessionPackedCount } = useWeighAndPrint({
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
      getSettings: () => ({ agentUrl: 'http://127.0.0.1:8080' }),
    });

    sessionPackedCount.value = 0;
    await triggerWeighAndPrint();

    expect(packingApi.weighPackCarton).toHaveBeenCalled();
    expect(printApi.agentPrint).toHaveBeenCalled();
    expect(printApi.updateCartonStatus).toHaveBeenCalledWith(123, 'SUCCESS');
    expect(advanceSequence).toHaveBeenCalled();
    expect(lastPackedCarton.value?.carton_sn).toBe('VHK00102372608000001');
    expect(sessionPackedCount.value).toBe(1);
    expect(notify).toHaveBeenCalledWith(expect.stringContaining('Đã in thành công'), 'success');
  });
});
