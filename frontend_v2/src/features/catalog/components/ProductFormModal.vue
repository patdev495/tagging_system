<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-3xl overflow-hidden animate-in fade-in zoom-in duration-200 my-8 border border-slate-100">
      
      <!-- Modal Header -->
      <div class="p-6 bg-slate-900 text-white flex justify-between items-center">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-lg">
            <i class="fas fa-box"></i>
          </div>
          <div>
            <h2 class="text-xl font-bold tracking-tight">{{ isEdit ? 'Cập Nhật Sản Phẩm' : 'Thêm Sản Phẩm Mới' }}</h2>
            <p class="text-xs text-slate-400 mt-0.5">Khối cấu hình thông minh tự thích ứng theo Chế độ đóng gói & Mẫu tem.</p>
          </div>
        </div>
        <button @click="$emit('close')" class="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer">
          <X class="w-6 h-6" />
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
        
        <!-- SECTION 1: THÔNG TIN CƠ BẢN -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-2 border-b border-slate-100 text-slate-900 font-bold text-sm">
            <i class="fas fa-info-circle text-indigo-600"></i>
            <span>1. Thông Tin Khách Hàng & Sản Phẩm</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <label class="text-xs font-bold text-slate-700 uppercase">Khách Hàng (Customer) *</label>
              <select 
                v-model="formData.customer_id" 
                @change="onCustomerChange" 
                required 
                class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none bg-white font-medium text-sm"
              >
                <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
              </select>
            </div>

            <div class="space-y-1.5">
              <label class="text-xs font-bold text-slate-700 uppercase">Mã Sản Phẩm / CPN (Product Name) *</label>
              <input 
                v-model="formData.item_name" 
                type="text" 
                required 
                placeholder="VD: 840-00083 hoặc UVC-G4-PRO" 
                class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-sm font-bold"
              >
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <label class="text-xs font-bold text-slate-700 uppercase">Số Lượng / Thùng (Packed QTY) *</label>
              <input 
                v-model.number="formData.packed_qty" 
                type="number" 
                required 
                min="1" 
                class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-sm font-bold"
              >
            </div>

            <div class="space-y-1.5">
              <label class="text-xs font-bold text-slate-700 uppercase">Đường Dẫn File Tem BarTender (.btw)</label>
              <input 
                v-model="formData.template_path" 
                type="text" 
                placeholder="VD: D:\PAT\Templates\a11.btw" 
                class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-xs text-slate-700"
              >
            </div>
          </div>
        </div>

        <!-- SECTION 2: CHẾ ĐỘ ĐÓNG GÓI -->
        <div class="space-y-4 pt-2">
          <div class="flex items-center gap-2 pb-2 border-b border-slate-100 text-slate-900 font-bold text-sm">
            <i class="fas fa-sliders text-indigo-600"></i>
            <span>2. Chế Độ Xác Thực & Đóng Gói (Packing Mode)</span>
          </div>

          <!-- Packing Mode Cards Selector -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div 
              @click="setPackingMode('item_scan')"
              :class="[
                'p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start gap-3',
                formData.packing_mode === 'item_scan' 
                  ? 'border-indigo-600 bg-indigo-50/50 shadow-xs' 
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              ]"
            >
              <div :class="['w-8 h-8 rounded-lg flex items-center justify-center shrink-0 font-bold', formData.packing_mode === 'item_scan' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600']">
                <i class="fas fa-barcode"></i>
              </div>
              <div>
                <div class="font-bold text-sm text-slate-900">Quét Từng Sản Phẩm Con (Item Scan)</div>
                <p class="text-xs text-slate-500 mt-0.5">Quét barcode sê-ri từng sản phẩm con cho đến khi đủ số lượng thùng.</p>
              </div>
            </div>

            <div 
              @click="setPackingMode('weight_scale')"
              :class="[
                'p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start gap-3',
                formData.packing_mode === 'weight_scale' 
                  ? 'border-emerald-600 bg-emerald-50/50 shadow-xs' 
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              ]"
            >
              <div :class="['w-8 h-8 rounded-lg flex items-center justify-center shrink-0 font-bold', formData.packing_mode === 'weight_scale' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600']">
                <i class="fas fa-weight-scale"></i>
              </div>
              <div>
                <div class="font-bold text-sm text-slate-900">Cân Trọng Lượng (Weight Scale)</div>
                <p class="text-xs text-slate-500 mt-0.5">Đóng gói theo cân điện tử và kiểm soát dải dung sai trọng lượng.</p>
              </div>
            </div>
          </div>

          <!-- Mode Specific Configurations -->
          <!-- 1. Item Scan Extra Settings -->
          <div v-if="formData.packing_mode === 'item_scan'" class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-1">
                <label class="text-xs font-bold text-slate-700 uppercase">Mã Vạch Sản Phẩm (UPC / GTIN)</label>
                <input 
                  v-model="formData.upc" 
                  type="text" 
                  placeholder="VD: 810010074102 (để trống nếu không có)" 
                  class="w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-xs"
                >
              </div>

              <div class="flex items-center pt-5">
                <label class="flex items-center gap-2.5 cursor-pointer select-none">
                  <input 
                    v-model="formData.allow_partial" 
                    type="checkbox" 
                    :true-value="1" 
                    :false-value="0" 
                    class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                  >
                  <span class="text-xs font-bold text-slate-700">Cho phép đóng thùng thiếu (Allow Partial Packing)</span>
                </label>
              </div>
            </div>
          </div>

          <!-- 2. Weight Scale Tolerance Gatekeeper Settings -->
          <div v-if="formData.packing_mode === 'weight_scale'" class="p-4 bg-emerald-50/60 rounded-2xl border border-emerald-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase text-emerald-900 flex items-center gap-1.5">
                <i class="fas fa-shield-halved text-emerald-600"></i>
                <span>Dung Sai Trọng Lượng Chuẩn (Weight Tolerance Gatekeeper)</span>
              </span>
              <span class="text-[10px] text-emerald-700 font-semibold bg-emerald-100 px-2 py-0.5 rounded">Đơn vị: kg</span>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">Min Weight (kg) *</label>
                <input 
                  v-model.number="formData.min_weight" 
                  type="number" 
                  step="0.001" 
                  required 
                  placeholder="12.300" 
                  class="w-full p-2.5 rounded-xl border border-emerald-300 bg-white focus:ring-2 focus:ring-emerald-500 outline-none font-mono font-bold text-sm text-slate-900"
                />
              </div>

              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">Target Weight (kg) *</label>
                <input 
                  v-model.number="formData.target_weight" 
                  type="number" 
                  step="0.001" 
                  required 
                  placeholder="12.500" 
                  class="w-full p-2.5 rounded-xl border border-emerald-300 bg-white focus:ring-2 focus:ring-emerald-500 outline-none font-mono font-bold text-sm text-slate-900"
                />
              </div>

              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">Max Weight (kg) *</label>
                <input 
                  v-model.number="formData.max_weight" 
                  type="number" 
                  step="0.001" 
                  required 
                  placeholder="12.700" 
                  class="w-full p-2.5 rounded-xl border border-emerald-300 bg-white focus:ring-2 focus:ring-emerald-500 outline-none font-mono font-bold text-sm text-slate-900"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- SECTION 3: QUY TẮC SINH S/N & TRƯỜNG IN TRÊN TEM -->
        <div class="space-y-4 pt-2">
          <div class="flex items-center gap-2 pb-2 border-b border-slate-100 text-slate-900 font-bold text-sm">
            <i class="fas fa-tag text-indigo-600"></i>
            <span>3. Quy Cách Tem In & Sinh Mã S/N Thùng (Label & S/N Specs)</span>
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-bold text-slate-700 uppercase">Kiểu Định Dạng Tem In (Template Type) *</label>
            <select 
              v-model="formData.template_type" 
              class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none bg-white font-medium text-sm"
            >
              <option value="standard">Tiêu chuẩn (Standard - Tem cơ bản)</option>
              <option value="detailed">Chi tiết (Detailed - Lưới 40 mã sê-ri con)</option>
              <option value="a11">A11 (Tiêu chuẩn khách hàng A11)</option>
            </select>
          </div>

          <!-- Fields for A11 or yearly prefix -->
          <div v-if="formData.template_type === 'a11' || formData.packing_mode === 'weight_scale'" class="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-100">
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-700 uppercase">PKG Prefix (Carton SN) *</label>
              <input 
                v-model="formData.pkg_prefix" 
                type="text" 
                placeholder="VHK0010237" 
                class="w-full p-2.5 rounded-xl border border-purple-200 bg-white focus:ring-2 focus:ring-purple-500 outline-none font-mono text-xs font-bold"
              >
              <p class="text-[10px] text-slate-400">Tiền tố sinh số thùng reset hàng năm.</p>
            </div>

            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-700 uppercase">MFR P/N (Spec No) *</label>
              <input 
                v-model="formData.mfr_pn" 
                type="text" 
                placeholder="NYS5998" 
                class="w-full p-2.5 rounded-xl border border-purple-200 bg-white focus:ring-2 focus:ring-purple-500 outline-none font-mono text-xs font-bold"
              >
              <p class="text-[10px] text-slate-400">Mã chứng nhận spec nội bộ.</p>
            </div>

            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-700 uppercase">Revision</label>
              <input 
                v-model="formData.revision" 
                type="text" 
                placeholder="B" 
                class="w-full p-2.5 rounded-xl border border-purple-200 bg-white focus:ring-2 focus:ring-purple-500 outline-none font-mono text-xs font-bold uppercase"
              >
              <p class="text-[10px] text-slate-400">Để trống = không hiện ô Rev trên tem.</p>
            </div>
          </div>

          <!-- Fields for Standard / UI monthly prefix -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-700 uppercase">S/N Start Part</label>
              <input 
                v-model="formData.start_part" 
                type="text" 
                placeholder="VN hoặc CN" 
                class="w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-xs font-bold"
              >
              <p class="text-[10px] text-slate-400">Tiền tố quốc gia trước tháng YYMM (VD: CN2608...).</p>
            </div>

            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-700 uppercase">S/N Middle Part</label>
              <input 
                v-model="formData.middle_part" 
                type="text" 
                placeholder="11, 16, A, B..." 
                class="w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-xs font-bold"
              >
              <p class="text-[10px] text-slate-400">Ký tự phân loại sản phẩm sau tháng YYMM.</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="pt-4 flex gap-3 border-t border-slate-100">
          <button 
            type="button" 
            @click="$emit('close')" 
            class="flex-1 px-4 py-3 rounded-xl border border-slate-200 font-bold text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer text-sm"
          >
            Hủy Bỏ
          </button>
          <button 
            type="submit" 
            :disabled="isSubmitting" 
            class="flex-1 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-all shadow-md shadow-indigo-200 disabled:opacity-50 cursor-pointer text-sm flex items-center justify-center gap-2"
          >
            <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
            <span>{{ isSubmitting ? 'Đang lưu...' : (isEdit ? 'Cập Nhật Sản Phẩm' : 'Lưu Sản Phẩm') }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { X } from 'lucide-vue-next';
import type { Customer, Product } from '../../../types/api';

export interface ProductFormData {
  item_name: string;
  upc: string;
  packed_qty: number;
  start_part: string;
  middle_part: string;
  template_type: 'standard' | 'detailed' | 'a11';
  template_path: string;
  allow_partial: number;
  customer_id: number | null;
  packing_mode: 'item_scan' | 'weight_scale';
  target_weight: number | null;
  min_weight: number | null;
  max_weight: number | null;
  weight_unit: string;
  mfr_pn: string;
  pkg_prefix: string;
  revision: string;
}

const props = defineProps<{
  show: boolean;
  isEdit: boolean;
  isSubmitting: boolean;
  customers: Customer[];
  initialData?: Product | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'submit', data: ProductFormData): void;
}>();

const formData = ref<ProductFormData>({
  item_name: '',
  upc: '',
  packed_qty: 1,
  start_part: 'VN',
  middle_part: '',
  template_type: 'standard',
  template_path: '',
  allow_partial: 0,
  customer_id: null,
  packing_mode: 'item_scan',
  target_weight: 12.500,
  min_weight: 12.300,
  max_weight: 12.700,
  weight_unit: 'kg',
  mfr_pn: 'NYS5998',
  pkg_prefix: 'VHK0010237',
  revision: 'B',
});

watch(
  () => [props.show, props.initialData],
  ([isOpen]) => {
    if (!isOpen) return;
    if (props.isEdit && props.initialData) {
      const p = props.initialData;
      formData.value = {
        item_name: p.item_name,
        upc: p.upc || '',
        packed_qty: p.packed_qty,
        start_part: p.start_part || '',
        middle_part: p.middle_part || '',
        template_type: (p.template_type as 'standard' | 'detailed' | 'a11') || 'standard',
        template_path: p.template_path || '',
        allow_partial: p.allow_partial || 0,
        customer_id: p.customer_id,
        packing_mode: p.packing_mode || 'item_scan',
        target_weight: p.target_weight ?? 12.500,
        min_weight: p.min_weight ?? 12.300,
        max_weight: p.max_weight ?? 12.700,
        weight_unit: p.weight_unit || 'kg',
        mfr_pn: p.mfr_pn || 'NYS5998',
        pkg_prefix: p.pkg_prefix || 'VHK0010237',
        revision: p.revision ?? '',
      };
    } else {
      const defaultCustomerId = props.customers.length > 0 ? props.customers[0].id : null;
      formData.value = {
        item_name: '',
        upc: '',
        packed_qty: 1,
        start_part: 'VN',
        middle_part: '',
        template_type: 'standard',
        template_path: '',
        allow_partial: 0,
        customer_id: defaultCustomerId,
        packing_mode: 'item_scan',
        target_weight: 12.500,
        min_weight: 12.300,
        max_weight: 12.700,
        weight_unit: 'kg',
        mfr_pn: 'NYS5998',
        pkg_prefix: 'VHK0010237',
        revision: 'B',
      };
      if (defaultCustomerId) {
        onCustomerChange();
      }
    }
  },
  { immediate: true }
);

const setPackingMode = (mode: 'item_scan' | 'weight_scale') => {
  formData.value.packing_mode = mode;
  if (mode === 'weight_scale' && formData.value.template_type !== 'a11') {
    formData.value.template_type = 'a11';
    if (!formData.value.template_path) {
      formData.value.template_path = 'D:\\PAT\\Templates\\a11.btw';
    }
  } else if (mode === 'item_scan' && formData.value.template_type === 'a11') {
    formData.value.template_type = 'standard';
  }
};

const onCustomerChange = () => {
  if (props.isEdit) return;
  const selectedCust = props.customers.find(c => c.id === formData.value.customer_id);
  if (!selectedCust) return;

  const code = (selectedCust.code || '').toUpperCase();
  if (code === 'A11') {
    formData.value.packing_mode = 'weight_scale';
    formData.value.template_type = 'a11';
    formData.value.template_path = formData.value.template_path || 'D:\\PAT\\Templates\\a11.btw';
    formData.value.packed_qty = formData.value.packed_qty === 1 ? 190 : formData.value.packed_qty;
    formData.value.pkg_prefix = formData.value.pkg_prefix || 'VHK0010237';
    formData.value.mfr_pn = formData.value.mfr_pn || 'NYS5998';
    formData.value.revision = formData.value.revision || 'B';
    formData.value.target_weight = 12.500;
    formData.value.min_weight = 12.300;
    formData.value.max_weight = 12.700;
    formData.value.weight_unit = 'kg';
  } else if (code === 'UI') {
    formData.value.packing_mode = 'item_scan';
    formData.value.template_type = 'standard';
    formData.value.template_path = formData.value.template_path || 'D:\\PAT\\Templates\\carton.btw';
    formData.value.start_part = formData.value.start_part || 'VN';
    formData.value.packed_qty = formData.value.packed_qty === 190 ? 10 : formData.value.packed_qty;
  }
};

const handleSubmit = () => {
  emit('submit', { ...formData.value });
};
</script>
