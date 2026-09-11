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
              <div class="flex items-center justify-between">
                <label class="text-xs font-bold text-slate-700 uppercase">Mẫu Tem BarTender (.btw)</label>
                <div v-if="validationStatus" class="flex items-center gap-1.5 text-xs">
                  <span v-if="validationStatus.valid" class="text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    <span>Hợp lệ</span>
                  </span>
                  <span v-else class="text-rose-600 font-bold flex items-center gap-1" :title="validationStatus.message">
                    <AlertCircle class="w-3.5 h-3.5" />
                    <span>Không hợp lệ</span>
                  </span>
                </div>
              </div>
              <div class="flex gap-2">
                <div class="flex-1 flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 text-xs font-mono text-slate-800">
                  <span class="px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 font-bold uppercase text-[10px] shrink-0">Cố định</span>
                  <span class="font-bold flex-1 text-slate-900 truncate">📄 {{ formData.template_path || getCanonicalTemplateName(formData.template_type) }}</span>
                  <span class="text-[11px] text-slate-400 font-sans hidden sm:inline shrink-0">(Thư mục: D:\PAT\Templates)</span>
                </div>
                <button 
                  type="button" 
                  @click="checkTemplateValidity" 
                  :disabled="isValidating"
                  class="px-3 py-2 rounded-xl border border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 disabled:opacity-50 text-xs font-bold transition-colors flex items-center gap-1.5 cursor-pointer shrink-0"
                  title="Kiểm tra file trên BarTender Server"
                >
                  <div v-if="isValidating" class="w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                  <CheckCircle2 v-else class="w-3.5 h-3.5" />
                  <span>Kiểm Tra Server</span>
                </button>
              </div>
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

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-xs font-bold text-slate-700 uppercase">Min Weight (kg) *</label>
                <input 
                  v-model.number="formData.min_weight" 
                  type="number" 
                  step="0.001" 
                  required 
                  placeholder="12.300" 
                  class="w-full p-3 rounded-xl border border-emerald-300 bg-white focus:ring-2 focus:ring-emerald-500 outline-none font-mono font-bold text-sm text-slate-900"
                />
              </div>

              <div class="space-y-1.5">
                <label class="text-xs font-bold text-slate-700 uppercase">Max Weight (kg) *</label>
                <input 
                  v-model.number="formData.max_weight" 
                  type="number" 
                  step="0.001" 
                  required 
                  placeholder="12.700" 
                  class="w-full p-3 rounded-xl border border-emerald-300 bg-white focus:ring-2 focus:ring-emerald-500 outline-none font-mono font-bold text-sm text-slate-900"
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
              @change="onTemplateTypeChange"
              class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none bg-white font-medium text-sm"
            >
              <option value="standard">Tiêu chuẩn (Standard - Tem cơ bản)</option>
              <option value="detailed">Chi tiết (Detailed - Lưới 40 mã sê-ri con)</option>
              <option value="a11">A11 - Tem 1 (PD014736 Carton SN + Rev)</option>
              <option value="a11_tem2">A11 - Tem 2 (PD027504 Pallet SSCC + ASIN)</option>
            </select>
          </div>

          <!-- Fields for A11 Tem 2 (PD027504) -->
          <div v-if="formData.template_type === 'a11_tem2'" class="p-4 bg-sky-50/60 rounded-2xl border border-sky-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase text-sky-900 flex items-center gap-1.5">
                <i class="fas fa-barcode text-sky-600"></i>
                <span>Thông Số Tem 2 A11 (Pallet SSCC & Amazon ASIN)</span>
              </span>
              <span class="text-[10px] text-sky-700 font-semibold bg-sky-100 px-2 py-0.5 rounded">PD027504</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">Mã Xưởng (Factory P/N) *</label>
                <input 
                  v-model="formData.factory_pn" 
                  type="text" 
                  placeholder="1LAE0009D2U004MAAR" 
                  class="w-full p-2.5 rounded-xl border border-sky-200 bg-white focus:ring-2 focus:ring-sky-500 outline-none font-mono text-xs font-bold"
                >
                <p class="text-[10px] text-slate-400">厂内料号 để đối soát BOM xưởng.</p>
              </div>

              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">Amazon ASIN *</label>
                <input 
                  v-model="formData.asin" 
                  type="text" 
                  placeholder="B08G9M4HXS" 
                  class="w-full p-2.5 rounded-xl border border-sky-200 bg-white focus:ring-2 focus:ring-sky-500 outline-none font-mono text-xs font-bold uppercase"
                >
                <p class="text-[10px] text-slate-400">Mã định danh ASIN trên Amazon.</p>
              </div>

              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">Unit UPC Barcode *</label>
                <input 
                  v-model="formData.upc" 
                  type="text" 
                  placeholder="852582006785" 
                  class="w-full p-2.5 rounded-xl border border-sky-200 bg-white focus:ring-2 focus:ring-sky-500 outline-none font-mono text-xs font-bold"
                >
                <p class="text-[10px] text-slate-400">Mã vạch sản phẩm con in trên tem.</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">P/N Trên Tem (Spec No) *</label>
                <input 
                  v-model="formData.mfr_pn" 
                  type="text" 
                  placeholder="NYS5998 hoặc NYS5996" 
                  class="w-full p-2.5 rounded-xl border border-sky-200 bg-white focus:ring-2 focus:ring-sky-500 outline-none font-mono text-xs font-bold"
                >
                <p class="text-[10px] text-slate-400">In vào vùng P/N và barcode P/N.</p>
              </div>

              <div class="space-y-1">
                <label class="text-[11px] font-bold text-slate-700 uppercase">SSCC Company Prefix *</label>
                <input 
                  v-model="formData.pkg_prefix" 
                  type="text" 
                  placeholder="37033907" 
                  class="w-full p-2.5 rounded-xl border border-sky-200 bg-white focus:ring-2 focus:ring-sky-500 outline-none font-mono text-xs font-bold"
                >
                <p class="text-[10px] text-slate-400">Mặc định: 37033907 (Bộ đếm toàn cục).</p>
              </div>
            </div>

            <div class="space-y-1">
              <label class="text-[11px] font-bold text-slate-700 uppercase">Mô Tả Sản Phẩm (Product Description) *</label>
              <textarea 
                v-model="formData.product_desc" 
                rows="2"
                placeholder="ASSY,BAND WRAPPED,CAT5E ETHERNET CABLE 4.0mm OD:91CM,WHITE,RUBBER BAND" 
                class="w-full p-2.5 rounded-xl border border-sky-200 bg-white focus:ring-2 focus:ring-sky-500 outline-none font-mono text-xs font-medium"
              ></textarea>
              <p class="text-[10px] text-slate-400">Dòng mô tả quy cách in ở góc trái tem.</p>
            </div>
          </div>

          <!-- Fields for A11 Tem 1 or yearly prefix -->
          <div v-else-if="formData.template_type === 'a11' || formData.packing_mode === 'weight_scale'" class="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-100">
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
import { X, CheckCircle2, AlertCircle } from 'lucide-vue-next';
import { useProductForm, type ProductFormData } from '../composables/useProductForm';
import type { Customer, Product } from '../../../types/api';

export type { ProductFormData };

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

const {
  formData,
  isValidating,
  validationStatus,
  getCanonicalTemplateName,
  checkTemplateValidity,
  setPackingMode,
  onCustomerChange,
  onTemplateTypeChange,
  handleSubmit,
} = useProductForm(props, (_event, data) => emit('submit', data));
</script>
