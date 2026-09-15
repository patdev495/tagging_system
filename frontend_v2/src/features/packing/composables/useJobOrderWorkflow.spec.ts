import { defineComponent, ref, shallowRef } from 'vue';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useJobOrderWorkflow } from './useJobOrderWorkflow';
import jobOrderApi from '../../job_order/api';

vi.mock('../../job_order/api', () => ({
  default: {
    getJobOrderDetails: vi.fn(),
  },
}));

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: { en: { packing: { switch_slot_confirm: 'Switch slot?' } } },
});

describe('useJobOrderWorkflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('confirm', vi.fn(() => true));
  });

  it('keeps a resumed, verified carton waiting for the next-carton action without switching slots', async () => {
    const currentProduct = ref({ id: 1, item_name: 'UI Cable', packed_qty: 20 } as any);
    const workflowRef = shallowRef<ReturnType<typeof useJobOrderWorkflow> | null>(null);
    vi.mocked(jobOrderApi.getJobOrderDetails).mockResolvedValue({
      data: {
        job_order: 'JO-CURRENT',
        product: currentProduct.value,
        slots: [{ id: 101, status: 'PENDING', carton_sn: 'CN26095200001' }],
      },
    } as any);

    mount(defineComponent({
      setup() {
        workflowRef.value = useJobOrderWorkflow({
          system: { showNotification: vi.fn() },
          currentProduct,
          focusScan: vi.fn(),
          checkTemplateExists: vi.fn(),
          startPolling: vi.fn(),
          stopPolling: vi.fn(),
          playScanAlert: vi.fn(),
        });
        return {};
      },
      template: '<div />',
    }), { global: { plugins: [i18n] } });

    const workflow = workflowRef.value!;
    workflow.jobOrder.value = 'JO-CURRENT';
    workflow.scannedItems.value = ['ITEM-FROM-VERIFIED-CARTON'];
    workflow.awaitingNext.value = true;

    await workflow.enterScanning();

    expect(globalThis.confirm).not.toHaveBeenCalled();
    expect(workflow.selectedSlotId.value).toBeNull();
    expect(workflow.scannedItems.value).toEqual(['ITEM-FROM-VERIFIED-CARTON']);
  });
});
