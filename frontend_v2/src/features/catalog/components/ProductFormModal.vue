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
              <label class="text-xs font-bold text-slate-700 uppercase">Mẫu Tem BarTender (.btw) *</label>

              <!-- Erro products use their fixed canonical template. -->
              <div v-if="isErroProduct" class="w-full flex items-center gap-2 p-3 rounded-xl border border-purple-200 bg-purple-50/60 text-xs font-mono text-purple-900">
                <span class="px-2 py-0.5 rounded bg-purple-200 text-purple-800 font-bold uppercase text-[10px] shrink-0">Cố định Erro</span>
                <span class="font-bold flex-1 truncate">📄 {{ formData.template_type === 'erro_05' ? 'erro_05.btw' : (formData.template_type === 'erro_04' ? 'erro_04.btw' : (formData.template_type === 'erro_03' ? 'erro_03.btw' : (formData.template_type === 'erro_02' ? 'erro_02.btw' : 'erro_01.btw'))) }}</span>
                <span class="text-[11px] text-purple-600 font-sans hidden sm:inline shrink-0">({{ formData.template_type === 'erro_05' ? 'Erro 05 Pegatron NN9' : (formData.template_type === 'erro_04' ? 'Erro 04 PD027032' : (formData.template_type === 'erro_03' ? 'Erro 03 Luxshare NME' : (formData.template_type === 'erro_02' ? 'Erro 02 Pallet SSCC & ASIN' : 'Erro 01 Thùng Carton SN'))) }})</span>
              </div>

              <!-- For UI products: Select from 5 valid UI templates or retain existing DB value -->
              <div v-else class="space-y-1">
                <select 
                  v-model="formData.template_path" 
                  class="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none bg-white font-mono text-xs font-bold text-slate-800"
                >
                  <option v-if="formData.template_path && !UI_TEMPLATES.some(t => t.filename === formData.template_path)" :value="formData.template_path">
                    📄 {{ formData.template_path }} (Hiện tại trong DB)
                  </option>
                  <option v-for="t in UI_TEMPLATES" :key="t.filename" :value="t.filename">
                    📄 {{ t.label }}
                  </option>
                </select>
                <p class="text-[10px] text-slate-400">Chọn mẫu tem BarTender trong thư mục D:\PAT\Templates tương ứng với mặt hàng UI.</p>
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
              <optgroup label="Khách Hàng Erro">
                <option value="erro_05">Erro 05 (Pegatron NN9 PD016906 — erro_05.btw)</option>
                <option value="erro_04">Erro 04 (eero PD027032 — erro_04.btw)</option>
                <option value="erro_03">Erro 03 (Luxshare NME PD024364 — erro_03.btw)</option>
                <option value="erro_02">Erro 02 (PD027504 Pallet SSCC + ASIN — erro_02.btw)</option>
                <option value="erro_01">Erro 01 (PD014736 Carton SN + Rev — erro_01.btw)</option>
              </optgroup>
              <optgroup label="Khách Hàng UI">
                <option value="standard">Tiêu chuẩn (Standard - Tem thùng cơ bản)</option>
                <option value="detailed">Chi tiết (Detailed - Lưới 40 mã sê-ri con)</option>
              </optgroup>
            </select>
          </div>

          <!-- Erro Factory P/N 1-N Mapping Section -->
          <div v-if="['erro_01', 'erro_02', 'erro_03', 'erro_04', 'erro_05'].includes(formData.template_type)" class="p-4 bg-indigo-50/60 rounded-2xl border border-indigo-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase text-indigo-900 flex items-center gap-1.5">
                <i class="fas fa-barcode text-indigo-600"></i>
                <span>Factory P/N Áp Dụng (厂内料号 — 1-N Mapping)</span>
              </span>
              <span v-if="isEdit && initialData?.id" class="text-[10px] text-indigo-700 font-semibold bg-indigo-100 px-2 py-0.5 rounded">
                {{ mappings.length }} mã liên kết
              </span>
            </div>
            <p class="text-[11px] text-indigo-700">Mã công nhân quét/nhập tại trạm đóng gói để xác định Product và mẫu tem. Không dùng SKU để xác định tem.</p>

            <!-- Edit mode: 1-N Mapping Manager -->
            <div v-if="isEdit && initialData?.id" class="space-y-3 pt-1">
              <div v-if="isLoadingMappings" class="text-xs text-slate-500 py-1">Đang tải danh sách Factory P/N...</div>
              <div v-else-if="mappings.length > 0" class="flex flex-wrap gap-2 max-h-36 overflow-y-auto p-1 bg-white/70 rounded-xl border border-indigo-100">
                <div
                  v-for="m in mappings"
                  :key="m.id"
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-indigo-200 text-xs font-mono font-bold text-slate-800 shadow-xs"
                >
                  <span>{{ m.internal_factory_part_number }}</span>
                  <span class="text-[10px] px-1 py-0.2 bg-indigo-50 text-indigo-600 rounded font-sans font-normal">{{ m.source_drawing_code }}</span>
                  <button
                    type="button"
                    @click="deleteMapping(m.id)"
                    class="text-slate-400 hover:text-rose-600 ml-1 transition-colors cursor-pointer"
                    title="Xóa mapping"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
              <div v-else class="text-xs text-slate-500 italic py-1">Chưa có Factory P/N nào được liên kết cho Product này.</div>

              <!-- Add new mapping inline -->
              <div class="pt-2 border-t border-indigo-100 space-y-2">
                <div class="flex items-center gap-2">
                  <input
                    v-model="newPartNumber"
                    type="text"
                    placeholder="Nhập mã mới (VD: 1LAE0009D2U004MAAR)"
                    class="flex-1 p-2 rounded-xl border border-indigo-200 bg-white font-mono text-xs font-bold uppercase outline-none focus:ring-2 focus:ring-indigo-400"
                    @keydown.enter.prevent="addMapping"
                  />
                  <select
                    v-model="newDrawingCode"
                    class="p-2 rounded-xl border border-indigo-200 bg-white text-xs font-medium outline-none"
                  >
                    <option value="PD014736">PD014736 (erro_01)</option>
                    <option value="PD027504">PD027504 (erro_02)</option>
                    <option value="PD024364">PD024364 (erro_03)</option>
                    <option value="PD027032">PD027032 (erro_04)</option>
                    <option value="PD016906">PD016906 (erro_05)</option>
                    <option value="LEGACY">LEGACY</option>
                  </select>
                  <button
                    type="button"
                    @click="addMapping"
                    :disabled="!newPartNumber.trim() || isAddingMapping"
                    class="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer shrink-0"
                  >
                    {{ isAddingMapping ? 'Đang thêm...' : 'Thêm mã' }}
                  </button>
                </div>
                <div v-if="mappingError" class="text-xs font-semibold text-rose-600">{{ mappingError }}</div>
              </div>
            </div>

            <!-- Create mode: initial Factory P/N input -->
            <div v-else class="space-y-1">
              <input
                v-model="formData.internal_factory_part_number"
                type="text"
                placeholder="VD: 1LAE0009D2U004MAAR (tùy chọn ban đầu)"
                class="w-full p-2.5 rounded-xl border border-indigo-200 bg-white font-mono text-xs font-bold uppercase"
              />
              <p class="text-[10px] text-indigo-600">Sau khi lưu sản phẩm, bạn có thể quản lý nhiều Factory P/N ở phần Sửa.</p>
            </div>
          </div>

          <!-- Fields for Erro 05 (PD016906 Pegatron NN9) -->
          <div v-if="formData.template_type === 'erro_05'" class="p-4 bg-emerald-50/60 rounded-2xl border border-emerald-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase text-emerald-900 flex items-center gap-1.5"><i class="fas fa-microchip text-emerald-600"></i><span>Thông Số Erro 05 (Pegatron NN9 Ngoại Thùng)</span></span>
              <span class="text-[10px] text-emerald-700 font-semibold bg-emerald-100 px-2 py-0.5 rounded">PD016906 Rev I</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Tiền Tố Thùng (pkg_prefix) *</label><input v-model="formData.pkg_prefix" type="text" placeholder="MC220TW1" class="w-full p-2.5 rounded-xl border border-emerald-200 bg-white font-mono text-xs font-bold uppercase" /></div>
            </div>
            <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Mô Tả Quy Cách (Description) *</label><textarea v-model="formData.product_desc" rows="2" placeholder="X LED CABLE 30AWG 230mm" class="w-full p-2.5 rounded-xl border border-emerald-200 bg-white font-mono text-xs font-medium"></textarea></div>
          </div>

          <!-- Fields for Erro 04 (PD027032) -->
          <div v-if="formData.template_type === 'erro_04'" class="p-4 bg-rose-50/60 rounded-2xl border border-rose-200 space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Mã nguồn Erro 04 (115-…)</label><input v-model="formData.factory_item_code" required placeholder="115-00020" class="w-full p-2.5 rounded-xl border border-rose-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Carton ID Prefix *</label><select v-model="formData.carton_id_prefix" required class="w-full p-2.5 rounded-xl border border-rose-200 bg-white font-mono text-xs font-bold"><option disabled value="">Chọn H/K</option><option value="H">H - CAT6A</option><option value="K">K - CAT5E</option></select></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">UPC *</label><input v-model="formData.upc" required class="w-full p-2.5 rounded-xl border border-rose-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Supplier PN *</label><input v-model="formData.mfr_pn" required class="w-full p-2.5 rounded-xl border border-rose-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Revision *</label><input v-model="formData.revision" required class="w-full p-2.5 rounded-xl border border-rose-200 bg-white font-mono text-xs font-bold" /></div>
            </div>
            <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">SKU Description *</label><textarea v-model="formData.product_desc" required rows="2" class="w-full p-2.5 rounded-xl border border-rose-200 bg-white font-mono text-xs"></textarea></div>
          </div>

          <!-- Fields for Erro 03 (PD024364) -->
          <div v-if="formData.template_type === 'erro_03'" class="p-4 bg-amber-50/60 rounded-2xl border border-amber-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase text-amber-900 flex items-center gap-1.5"><i class="fas fa-industry text-amber-600"></i><span>Thông Số Erro 03 (Luxshare NME Ngoại Thùng)</span></span>
              <span class="text-[10px] text-amber-700 font-semibold bg-amber-100 px-2 py-0.5 rounded">PD024364 REV.M</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Mã Nhà Cung Cấp (Supplier Code) *</label><input v-model="formData.pkg_prefix" type="text" placeholder="1012665" class="w-full p-2.5 rounded-xl border border-amber-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">APN-Rev (Bản vẽ)</label><input v-model="formData.revision" type="text" placeholder="/" class="w-full p-2.5 rounded-xl border border-amber-200 bg-white font-mono text-xs font-bold uppercase" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Mã Liệu Luxshare *</label><input v-model="formData.luxshare_part_number" required type="text" placeholder="LLERJ014-NC-R" class="w-full p-2.5 rounded-xl border border-amber-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Customer Project *</label><input v-model="formData.customer_project" required type="text" placeholder="Andy Town/ Firefly" class="w-full p-2.5 rounded-xl border border-amber-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Production Stage *</label><input v-model="formData.production_stage" required type="text" placeholder="MP" class="w-full p-2.5 rounded-xl border border-amber-200 bg-white font-mono text-xs font-bold uppercase" /></div>
            </div>
            <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Mô Tả Sản Phẩm (Description) *</label><textarea v-model="formData.product_desc" rows="2" placeholder="CAT5E ETHERNET CABLE" class="w-full p-2.5 rounded-xl border border-amber-200 bg-white font-mono text-xs font-medium"></textarea></div>
          </div>

          <!-- Fields for Erro 02 (PD027504) -->
          <div v-else-if="formData.template_type === 'erro_02'" class="p-4 bg-sky-50/60 rounded-2xl border border-sky-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase text-sky-900 flex items-center gap-1.5"><i class="fas fa-barcode text-sky-600"></i><span>Thông Số Erro 02 (Pallet SSCC & Amazon ASIN)</span></span>
              <span class="text-[10px] text-sky-700 font-semibold bg-sky-100 px-2 py-0.5 rounded">PD027504</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Amazon ASIN *</label><input v-model="formData.asin" type="text" placeholder="B08G9M4HXS" class="w-full p-2.5 rounded-xl border border-sky-200 bg-white font-mono text-xs font-bold uppercase" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Unit UPC Barcode *</label><input v-model="formData.upc" type="text" placeholder="852582006785" class="w-full p-2.5 rounded-xl border border-sky-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">P/N Trên Tem (Spec No) *</label><input v-model="formData.mfr_pn" type="text" placeholder="NYS5998" class="w-full p-2.5 rounded-xl border border-sky-200 bg-white font-mono text-xs font-bold" /></div>
              <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">SSCC Company Prefix *</label><input v-model="formData.pkg_prefix" type="text" placeholder="37033907" class="w-full p-2.5 rounded-xl border border-sky-200 bg-white font-mono text-xs font-bold" /></div>
            </div>
            <div class="space-y-1"><label class="text-[11px] font-bold text-slate-700 uppercase">Mô Tả Sản Phẩm (Product Description) *</label><textarea v-model="formData.product_desc" rows="2" placeholder="ASSY,BAND WRAPPED..." class="w-full p-2.5 rounded-xl border border-sky-200 bg-white font-mono text-xs font-medium"></textarea></div>
          </div>

          <!-- Fields for Erro 01 or yearly prefix -->
          <div v-else-if="formData.template_type === 'erro_01' || formData.packing_mode === 'weight_scale'" class="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-100">
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
import { useProductForm, type ProductFormData } from '../composables/useProductForm';
import catalogApi from '../api';
import type { Customer, Product, ProductInternalFactoryPartNumber } from '../../../types/api';

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
  UI_TEMPLATES,
  isErroProduct,
  setPackingMode,
  onCustomerChange,
  onTemplateTypeChange,
  handleSubmit,
} = useProductForm(props, (_event, data) => emit('submit', data));

const mappings = ref<ProductInternalFactoryPartNumber[]>([]);
const isLoadingMappings = ref(false);
const isAddingMapping = ref(false);
const mappingError = ref('');
const newPartNumber = ref('');
const newDrawingCode = ref('PD014736');

const defaultDrawingForTemplate = (tmpl?: string) => {
  switch (tmpl) {
    case 'erro_01': return 'PD014736';
    case 'erro_02': return 'PD027504';
    case 'erro_03': return 'PD024364';
    case 'erro_04': return 'PD027032';
    case 'erro_05': return 'PD016906';
    default: return 'LEGACY';
  }
};

const loadMappings = async () => {
  if (!props.initialData?.id || !props.isEdit) {
    mappings.value = [];
    return;
  }
  isLoadingMappings.value = true;
  mappingError.value = '';
  try {
    const res = await catalogApi.getInternalFactoryPartNumbers(props.initialData.id);
    mappings.value = res.data || [];
  } catch (err: any) {
    console.warn('Could not load mappings:', err);
  } finally {
    isLoadingMappings.value = false;
  }
};

const addMapping = async () => {
  const code = newPartNumber.value.trim().toUpperCase();
  if (!code || !props.initialData?.id || isAddingMapping.value) return;

  isAddingMapping.value = true;
  mappingError.value = '';
  try {
    const res = await catalogApi.addInternalFactoryPartNumber(props.initialData.id, {
      internal_factory_part_number: code,
      source_drawing_code: newDrawingCode.value,
    });
    mappings.value.push(res.data);
    newPartNumber.value = '';
  } catch (err: any) {
    mappingError.value = err.response?.data?.error || err.response?.data?.detail || 'Không thể thêm Factory P/N.';
  } finally {
    isAddingMapping.value = false;
  }
};

const deleteMapping = async (mappingId: number) => {
  if (!props.initialData?.id) return;
  try {
    await catalogApi.deleteInternalFactoryPartNumber(props.initialData.id, mappingId);
    mappings.value = mappings.value.filter(m => m.id !== mappingId);
  } catch (err: any) {
    mappingError.value = err.response?.data?.error || err.response?.data?.detail || 'Không thể xóa Factory P/N.';
  }
};

watch(
  () => [props.show, props.initialData?.id] as const,
  ([show, id]) => {
    if (show && id && props.isEdit) {
      newDrawingCode.value = defaultDrawingForTemplate(props.initialData?.template_type);
      loadMappings();
    } else {
      mappings.value = [];
      newPartNumber.value = '';
      mappingError.value = '';
    }
  },
  { immediate: true }
);

watch(
  () => formData.value.template_type,
  (tmpl) => {
    newDrawingCode.value = defaultDrawingForTemplate(tmpl);
  }
);
</script>
