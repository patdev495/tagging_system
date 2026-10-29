import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import ProductFormModal from './ProductFormModal.vue';
import type { Customer, Product } from '../../../types/api';

vi.mock('../../print/api', () => ({
  default: {
    getTemplates: vi.fn().mockResolvedValue({ data: { templates: [] } }),
    whoami: vi.fn().mockResolvedValue({ data: { ip: '127.0.0.1' } }),
  },
}));

describe('ProductFormModal', () => {
  beforeEach(() => setActivePinia(createPinia()));

  it('lets an admin edit Customer Project and Production Stage for an Erro 03 Product', async () => {
    const erro: Customer = { id: 1, code: 'ERRO', name: 'Erro', is_active: true };
    const product: Product = {
      id: 3,
      customer_id: erro.id,
      item_name: '2M21-00508-0004H',
      packed_qty: 190,
      template_type: 'erro_03',
      allow_partial: 0,
      packing_mode: 'weight_scale',
      luxshare_part_number: 'LLERJ014-NC-R',
      customer_project: 'Andy Town/ Firefly',
      production_stage: 'MP',
    };

    const wrapper = mount(ProductFormModal, {
      props: { show: true, isEdit: true, isSubmitting: false, customers: [erro], initialData: product },
    });

    expect(wrapper.text()).toContain('Customer Project *');
    expect(wrapper.text()).toContain('Production Stage *');
    expect(wrapper.text()).toContain('Mã Liệu Luxshare *');
    expect((wrapper.find('input[placeholder="LLERJ014-NC-R"]').element as HTMLInputElement).value)
      .toBe('LLERJ014-NC-R');
    expect((wrapper.find('input[placeholder="Andy Town/ Firefly"]').element as HTMLInputElement).value)
      .toBe('Andy Town/ Firefly');
    expect((wrapper.find('input[placeholder="MP"]').element as HTMLInputElement).value).toBe('MP');
    expect(wrapper.text()).not.toContain('Mẫu Tem BarTender (.btw)');
    expect(wrapper.text()).toContain('File tem tương ứng: erro_03.btw');

    const templateType = wrapper.findAll('select').find(select => select.find('option[value="erro_02"]').exists());
    await templateType?.setValue('erro_02');
    expect(wrapper.text()).toContain('File tem tương ứng: erro_02.btw');
  });

  it('lists UI templates used by products and saves only the selected local filename', async () => {
    const ui: Customer = { id: 2, code: 'UI', name: 'Universal Instruments', is_active: true };
    const products = [
      { id: 1, customer_id: 2, item_name: 'A', packed_qty: 10, template_type: 'standard', template_path: 'D:\\PAT\\Templates\\carton_base.btw' },
      { id: 2, customer_id: 2, item_name: 'B', packed_qty: 10, template_type: 'standard', template_path: 'carton_base.btw' },
      { id: 3, customer_id: 2, item_name: 'C', packed_qty: 10, template_type: 'detailed', template_path: 'carton_detail_1M_W.btw' },
    ] as Product[];
    const wrapper = mount(ProductFormModal, {
      props: { show: true, isEdit: false, isSubmitting: false, customers: [ui], products },
    });

    const select = wrapper.find('select[required][class*="font-mono"]');
    expect(select.findAll('option').map(option => option.attributes('value')))
      .toEqual(['', 'carton_base.btw', 'carton_detail_1M_W.btw']);

    const input = wrapper.find('input[type="file"]');
    Object.defineProperty(input.element, 'files', { configurable: true, value: [new File(['test'], 'new_label.btw')] });
    await input.trigger('change');
    expect((select.element as HTMLSelectElement).value).toBe('new_label.btw');

    await wrapper.find('form').trigger('submit');
    expect(wrapper.emitted('submit')?.[0]?.[0]).toMatchObject({ template_path: 'new_label.btw' });
  });
});
