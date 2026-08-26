import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import JobOrderInputStep from '../components/JobOrderInputStep.vue';
import ProductCardStep from '../components/ProductCardStep.vue';
import type { JobOrderDetails } from '../../../types/api';

const i18n = createI18n({
  legacy: false,
  locale: 'vi',
  messages: {
    vi: {
      packing: {
        enter_job_order_title: 'Nhập Số Công Lệnh',
        enter_job_order_desc: 'Vui lòng quét hoặc nhập mã công lệnh',
        job_order_placeholder: 'Nhập số công lệnh...',
        confirm: 'Xác Nhận',
        job_order: 'Công lệnh',
        change_job_order: 'Đổi công lệnh',
        total_qty: 'Tổng Số Lượng',
        total_cartons: 'Tổng Số Thùng',
      },
    },
  },
});

describe('Job Order Packing Steps', () => {
  it('JobOrderInputStep emits update:modelValue on typing and submit on form submit', async () => {
    const wrapper = mount(JobOrderInputStep, {
      props: {
        modelValue: 'JO-123',
        isLoading: false,
        hasError: false,
        errorText: '',
      },
      global: {
        plugins: [i18n],
      },
    });

    const input = wrapper.find('input');
    expect(input.element.value).toBe('JO-123');

    await input.setValue('JO-999');
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['JO-999']);

    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.emitted('submit')).toBeTruthy();
  });

  it('ProductCardStep renders product specs and emits events', async () => {
    const mockDetails: JobOrderDetails = {
      job_order: 'JO-123',
      product: {
        id: 1,
        customer_id: 1,
        item_name: 'U-Pro-Accessory',
        upc: '810012345678',
        packed_qty: 20,
        template_type: 'standard',
        allow_partial: 0,
      },
      total_qty: 200,
      total_cartons: 10,
      slots: [],
    };

    const wrapper = mount(ProductCardStep, {
      props: {
        jobOrder: 'JO-123',
        jobOrderDetails: mockDetails,
      },
      global: {
        plugins: [i18n],
      },
    });

    expect(wrapper.text()).toContain('U-Pro-Accessory');
    expect(wrapper.text()).toContain('810012345678');
    expect(wrapper.text()).toContain('200');

    // Click change job order
    const changeBtn = wrapper.find('button');
    await changeBtn.trigger('click');
    expect(wrapper.emitted('changeJobOrder')).toBeTruthy();

    // Click product card
    const card = wrapper.find('.group');
    await card.trigger('click');
    expect(wrapper.emitted('enterScanning')).toBeTruthy();
  });
});
