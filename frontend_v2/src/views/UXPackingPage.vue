<template>
  <div class="h-screen w-full bg-slate-100 text-slate-800 flex flex-col p-2 md:p-3 overflow-hidden box-border select-none">
    <div class="w-full h-full flex flex-col bg-white border border-slate-200/90 rounded-2xl p-3 md:p-4 shadow-xl overflow-hidden box-border justify-between">
      
      <!-- Top Slim Navigation Header -->
      <header class="flex items-center justify-between pb-2 border-b border-slate-200 shrink-0">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 shadow-inner shrink-0">
            <i class="fas fa-weight-scale text-lg"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="font-black text-base md:text-lg text-slate-900 leading-tight">Trạm Cân Đóng Gói (UX)</h1>
              <span class="px-2 py-0.5 text-[10px] font-black rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200 tracking-wide uppercase">
                Tem A11
              </span>
            </div>
            <p class="text-[11px] text-slate-500 leading-none">Kiểm soát trọng lượng dung sai và in nhãn BarTender A11</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Scale Connection Status Indicator -->
          <div 
            :class="[
              'px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 text-xs font-bold transition-all shrink-0',
              scaleStatus.connected && scaleStatus.is_streaming !== false
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs'
                : 'bg-rose-50 text-rose-700 border-rose-200'
            ]"
          >
            <span class="relative flex h-2 w-2">
              <span v-if="scaleStatus.connected" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span :class="['relative inline-flex rounded-full h-2 w-2', scaleStatus.connected ? 'bg-emerald-500' : 'bg-rose-500']"></span>
            </span>
            <span>{{ scaleStatus.connected ? `Cân Online (${scaleStatus.port || 'COM'})` : 'Cân Mất Kết Nối' }}</span>
          </div>

          <!-- Quick Action Buttons -->
          <button
            @click="showReprintModal = true"
            class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
            title="In lại tem khẩn cấp"
          >
            <i class="fas fa-history text-slate-500"></i>
            <span>In Lại</span>
          </button>

          <button
            @click="showSettingsModal = true"
            class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <i class="fas fa-cog text-slate-500"></i>
            <span>Cài Đặt</span>
          </button>

          <button
            @click="switchCustomer"
            class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <i class="fas fa-exchange-alt"></i>
            <span>Đổi Khách</span>
          </button>
        </div>
      </header>

      <!-- Compact Active Product & Batch Bar -->
      <section class="my-2 px-3.5 py-2 rounded-xl bg-slate-50/90 border border-slate-200/90 shadow-xs flex items-center justify-between gap-3 shrink-0">
        <!-- Specs Details -->
        <div class="flex items-center gap-4 md:gap-6 flex-wrap">
          <div @click="openProductModal" class="flex items-center gap-2 cursor-pointer group hover:opacity-80 transition-all" title="Bấm để đổi sản phẩm">
            <span class="text-[10px] uppercase tracking-wider font-bold text-slate-400">CPN:</span>
            <span class="font-black text-sm md:text-base text-slate-900 font-mono group-hover:text-indigo-600 transition-colors">
              {{ selectedProduct?.item_name || 'Chưa chọn' }}
            </span>
            <span v-if="selectedProduct" class="px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700 font-bold text-[10px]">
              {{ selectedProduct.packed_qty }} PCS
            </span>
          </div>

          <div v-if="selectedProduct" class="flex items-center gap-2 border-l border-slate-200 pl-4 text-xs font-mono">
            <span class="text-[10px] uppercase font-bold text-slate-400 font-sans">Mfr/Prefix:</span>
            <span class="font-bold text-slate-700">{{ selectedProduct.mfr_pn || 'NYS5998' }}</span>
            <span class="text-slate-300">|</span>
            <span class="font-bold text-slate-700">{{ selectedProduct.pkg_prefix || 'VHK0010237' }}</span>
          </div>

          <div class="flex items-center gap-2 border-l border-slate-200 pl-4 text-xs font-mono">
            <span class="text-[10px] uppercase font-bold text-slate-400 font-sans">PO/LOT:</span>
            <span class="font-bold text-indigo-900">PO: {{ activePO || 'Chưa nhập' }}</span>
            <span class="text-slate-300">|</span>
            <span class="font-bold text-indigo-900">LOT: {{ activeLot || 'Chưa nhập' }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2 shrink-0">
          <button
            @click="showBatchModal = true"
            class="px-2.5 py-1 rounded-lg bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold transition-all flex items-center gap-1 shadow-xs cursor-pointer"
          >
            <i class="fas fa-edit text-indigo-500"></i>
            <span>Đổi PO/LOT</span>
          </button>

          <button
            @click="openProductModal"
            class="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-all flex items-center gap-1 shadow-xs shadow-indigo-600/20 cursor-pointer"
          >
            <i class="fas fa-boxes"></i>
            <span>Đổi Sản Phẩm</span>
          </button>
        </div>

      </section>

      <!-- Main Packing Station Cockpit Grid -->
      <main class="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-0">
        
        <!-- Left: Live Scale & Action Controls (8 Cols) -->
        <div class="lg:col-span-8 flex flex-col justify-between h-full gap-2 min-h-0">
          
          <!-- Live Digital Gauge Card -->
          <div class="p-4 md:p-5 rounded-2xl bg-slate-900 text-white shadow-lg flex-1 flex flex-col justify-between relative overflow-hidden min-h-0">
            <!-- Background Glow Effect -->
            <div 
              :class="[
                'absolute -right-20 -top-20 w-72 h-72 rounded-full blur-3xl opacity-20 transition-all duration-500 pointer-events-none',
                toleranceResult.status === 'READY' ? 'bg-emerald-400' :
                toleranceResult.status === 'UNSTABLE' ? 'bg-amber-400' :
                toleranceResult.status === 'UNDERWEIGHT' || toleranceResult.status === 'OVERWEIGHT' ? 'bg-rose-500' : 'bg-slate-600'
              ]"
            ></div>

            <!-- Top Row: Scale Pulse & Tare/Zero -->
            <div class="flex items-center justify-between mb-1 z-10 shrink-0">
              <div class="flex items-center gap-1.5 text-slate-400 text-[11px] font-bold uppercase tracking-wider">
                <i class="fas fa-satellite-dish text-emerald-400 animate-pulse"></i>
                <span>Tín Hiệu Cân Thời Gian Thực</span>
              </div>

              <!-- Tare & Zero Controls -->
              <div class="flex items-center gap-1.5">
                <button
                  @click="handleTare"
                  :disabled="!scaleStatus.connected || isPrinting"
                  class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 text-xs font-semibold transition-all flex items-center gap-1 cursor-pointer border border-slate-700 shadow-xs"
                >
                  <i class="fas fa-balance-scale-left text-xs"></i>
                  <span>Trừ Bì (Tare)</span>
                </button>

                <button
                  @click="handleZero"
                  :disabled="!scaleStatus.connected || isPrinting"
                  class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 text-xs font-semibold transition-all flex items-center gap-1 cursor-pointer border border-slate-700 shadow-xs"
                >
                  <i class="fas fa-crosshairs text-xs"></i>
                  <span>Zero</span>
                </button>
              </div>
            </div>

            <!-- Big Digital Reading Display -->
            <div class="flex flex-col items-center justify-center my-auto py-1 z-10">
              <div class="flex items-baseline gap-2">
                <span 
                  :class="[
                    'text-6xl md:text-7xl lg:text-8xl font-black font-mono tracking-tight transition-colors duration-200 leading-none',
                    toleranceResult.status === 'READY' ? 'text-emerald-400' :
                    toleranceResult.status === 'UNSTABLE' ? 'text-amber-400' :
                    toleranceResult.status === 'UNDERWEIGHT' || toleranceResult.status === 'OVERWEIGHT' ? 'text-rose-400' : 'text-slate-500'
                  ]"
                >
                  {{ formatWeight(scaleReading.weight) }}
                </span>
                <span class="text-xl md:text-2xl font-bold text-slate-400 font-mono">{{ scaleReading.unit || 'kg' }}</span>
              </div>

              <!-- Indicators: Stability & Tare -->
              <div class="flex items-center gap-2 mt-2">
                <span 
                  :class="[
                    'px-2.5 py-0.5 rounded-full text-[11px] font-bold flex items-center gap-1',
                    scaleReading.is_stable
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse'
                  ]"
                >
                  <i :class="scaleReading.is_stable ? 'fas fa-check-circle' : 'fas fa-spinner fa-spin'"></i>
                  <span>{{ scaleReading.is_stable ? 'ỔN ĐỊNH' : 'ĐANG DAO ĐỘNG' }}</span>
                </span>

                <span v-if="scaleReading.is_tare" class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  TARE (ĐÃ TRỪ BÌ)
                </span>
              </div>
            </div>

            <!-- Visual Tolerance Bar & Targets -->
            <div class="pt-2.5 border-t border-slate-800/90 z-10 shrink-0">
              <!-- Prominent 3-Pillar Weight Badges -->
              <div class="grid grid-cols-3 gap-2 mb-2">
                <!-- Min Limit Badge -->
                <div class="px-2.5 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700/80 flex flex-col items-start shadow-xs">
                  <div class="flex items-center gap-1 text-[10px] font-extrabold uppercase tracking-wider text-amber-400">
                    <i class="fas fa-arrow-down-short-wide text-[9px]"></i>
                    <span>Tối Thiểu (Min)</span>
                  </div>
                  <span class="font-mono font-black text-sm md:text-base text-slate-100 mt-0.5">
                    {{ selectedProduct?.min_weight?.toFixed(3) || '0.150' }} <span class="text-[11px] font-normal text-slate-400">kg</span>
                  </span>
                </div>

                <!-- Target Weight Badge (Highlighted Centerpiece) -->
                <div class="px-2.5 py-1.5 rounded-xl bg-emerald-950/80 border border-emerald-500/50 flex flex-col items-center shadow-md shadow-emerald-950/60 ring-1 ring-emerald-500/20">
                  <div class="flex items-center gap-1 text-[10px] font-black uppercase tracking-wider text-emerald-400">
                    <i class="fas fa-bullseye text-[10px]"></i>
                    <span>Mục Tiêu Chuẩn</span>
                  </div>
                  <span class="font-mono font-black text-base md:text-lg text-emerald-300 mt-0.5 leading-tight">
                    {{ selectedProduct?.target_weight?.toFixed(3) || '0.180' }} <span class="text-xs font-bold text-emerald-400">kg</span>
                  </span>
                </div>

                <!-- Max Limit Badge -->
                <div class="px-2.5 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700/80 flex flex-col items-end shadow-xs">
                  <div class="flex items-center gap-1 text-[10px] font-extrabold uppercase tracking-wider text-rose-400">
                    <span>Tối Đa (Max)</span>
                    <i class="fas fa-arrow-up-wide-short text-[9px]"></i>
                  </div>
                  <span class="font-mono font-black text-sm md:text-base text-slate-100 mt-0.5">
                    {{ selectedProduct?.max_weight?.toFixed(3) || '0.200' }} <span class="text-[11px] font-normal text-slate-400">kg</span>
                  </span>
                </div>
              </div>

              <!-- High-Visibility Dynamic Gauge Track Bar -->
              <div class="relative h-4 bg-slate-950 rounded-full overflow-hidden p-0.5 flex items-center border border-slate-700 shadow-inner">
                <!-- Underweight Left Zone -->
                <div class="absolute left-0 w-[16.6%] h-full bg-amber-500/15"></div>
                <!-- Acceptable Green Safe Zone -->
                <div class="absolute left-[16.6%] right-[16.6%] h-full bg-gradient-to-r from-emerald-500/30 via-emerald-400/50 to-emerald-500/30 border-x border-emerald-400/60 flex items-center justify-center">
                  <!-- Center Target Line -->
                  <div class="w-0.5 h-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,1)]"></div>
                </div>
                <!-- Overweight Right Zone -->
                <div class="absolute right-0 w-[16.6%] h-full bg-rose-500/15"></div>

                <!-- Dynamic Live Needle Pointer -->
                <div 
                  :class="[
                    'absolute top-0 bottom-0 w-3 -ml-1.5 rounded-full border shadow-md transition-all duration-150',
                    toleranceResult.status === 'READY' ? 'bg-emerald-400 border-white shadow-[0_0_8px_rgba(52,211,153,1)]' :
                    toleranceResult.status === 'UNSTABLE' ? 'bg-amber-400 border-white shadow-[0_0_8px_rgba(251,191,36,1)]' :
                    toleranceResult.status === 'UNDERWEIGHT' || toleranceResult.status === 'OVERWEIGHT' ? 'bg-rose-500 border-white shadow-[0_0_8px_rgba(244,63,94,1)]' : 'bg-white border-slate-900'
                  ]"
                  :style="{ left: `${calculateGaugePercent(scaleReading.weight)}%` }"
                ></div>
              </div>
            </div>
          </div>


          <!-- Bottom Cockpit: Combined Status & S/N Control -->
          <div class="grid grid-cols-1 md:grid-cols-12 gap-2 shrink-0">
            <!-- Tolerance Gatekeeper Status Chip (Col 6) -->
            <div 
              :class="[
                'md:col-span-6 px-3 py-2 rounded-xl border flex items-center justify-between gap-2 transition-all duration-200',
                toleranceResult.status === 'READY'
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900' :
                toleranceResult.status === 'UNSTABLE'
                  ? 'bg-amber-50 border-amber-200 text-amber-900' :
                toleranceResult.status === 'UNDERWEIGHT' || toleranceResult.status === 'OVERWEIGHT'
                  ? 'bg-rose-50 border-rose-200 text-rose-900' :
                  'bg-slate-100 border-slate-200 text-slate-600'
              ]"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <div 
                  :class="[
                    'w-7 h-7 rounded-lg flex items-center justify-center text-xs shrink-0',
                    toleranceResult.status === 'READY' ? 'bg-emerald-500 text-white shadow-xs' :
                    toleranceResult.status === 'UNSTABLE' ? 'bg-amber-500 text-white' :
                    toleranceResult.status === 'UNDERWEIGHT' || toleranceResult.status === 'OVERWEIGHT' ? 'bg-rose-500 text-white' : 'bg-slate-400 text-white'
                  ]"
                >
                  <i :class="getToleranceIcon(toleranceResult.status)"></i>
                </div>
                <div class="truncate">
                  <h3 class="font-bold text-xs leading-tight truncate">{{ getToleranceTitle(toleranceResult.status) }}</h3>
                  <p class="text-[10px] opacity-80 truncate">{{ toleranceResult.message }}</p>
                </div>
              </div>

              <span 
                :class="[
                  'px-2 py-0.5 rounded text-[10px] font-black tracking-wide uppercase shrink-0',
                  toleranceResult.status === 'READY' ? 'bg-emerald-200 text-emerald-900' :
                  toleranceResult.status === 'UNSTABLE' ? 'bg-amber-200 text-amber-900' :
                  toleranceResult.status === 'UNDERWEIGHT' || toleranceResult.status === 'OVERWEIGHT' ? 'bg-rose-200 text-rose-900' : 'bg-slate-200 text-slate-800'
                ]"
              >
                {{ toleranceResult.status }}
              </span>
            </div>

            <!-- S/N Sequence Configuration Chip (Col 6) -->
            <div class="md:col-span-6 px-3 py-2 rounded-xl bg-slate-50 border border-slate-200/90 shadow-xs flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <div class="w-7 h-7 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 font-black text-xs shrink-0">
                  #
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[10px] font-bold uppercase text-slate-500">Sê-ri:</span>
                    <span :class="['px-1.5 py-0.2 rounded text-[9px] font-black uppercase', isAutoSN ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800']">
                      {{ isAutoSN ? 'Tự Động' : 'Thủ Công' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span class="font-mono font-black text-xs md:text-sm text-indigo-950 tracking-tight truncate select-all">
                      {{ currentSNPreview }}
                    </span>
                    <span v-if="snCheckError" class="text-[10px] text-rose-600 font-bold" :title="snCheckError">
                      <i class="fas fa-exclamation-triangle"></i>
                    </span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-1.5 shrink-0">
                <input
                  v-if="!isAutoSN"
                  v-model.number="manualSequence"
                  type="number"
                  min="1"
                  placeholder="85"
                  class="w-16 px-2 py-1 rounded border border-slate-300 font-mono font-bold text-xs text-slate-800 focus:ring-1 focus:ring-indigo-500 outline-none"
                  @input="checkManualSN"
                />

                <button
                  @click="toggleSNMode"
                  type="button"
                  :class="[
                    'px-2 py-1 rounded-lg font-bold text-[11px] flex items-center gap-1 transition-all cursor-pointer shadow-xs',
                    isAutoSN 
                      ? 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200' 
                      : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200'
                  ]"
                >
                  <i :class="isAutoSN ? 'fas fa-pen' : 'fas fa-rotate-right'"></i>
                  <span>{{ isAutoSN ? 'Sửa' : 'Auto' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Giant Primary Print Action Button -->
          <button
            @click="triggerWeighAndPrint"
            :disabled="isPrinting"
            :class="[
              'w-full py-3 md:py-3.5 rounded-xl font-black text-base md:text-lg transition-all flex items-center justify-center gap-2 cursor-pointer shadow-md shrink-0',
              toleranceResult.canPrint && activePO && activeLot && (isAutoSN || !snCheckError)
                ? 'bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white shadow-emerald-600/30'
                : 'bg-rose-600 hover:bg-rose-700 active:scale-[0.99] text-white shadow-rose-600/20'
            ]"
          >
            <i v-if="isPrinting" class="fas fa-spinner fa-spin text-lg"></i>
            <i v-else-if="toleranceResult.canPrint" class="fas fa-print text-lg"></i>
            <i v-else class="fas fa-triangle-exclamation text-lg"></i>
            <span>{{ isPrinting ? 'ĐANG GỬI LỆNH IN...' : (toleranceResult.canPrint ? 'CÂN & IN TEM A11 [F9]' : 'LỆCH DUNG SAI - BẤM ĐỂ XEM LỖI [F9]') }}</span>
          </button>
        </div>

        <!-- Right: Session Stats & Last Carton Info (4 Cols) -->
        <div class="lg:col-span-4 flex flex-col h-full gap-2 min-h-0 justify-between">
          
          <!-- Compact Session Packaging Counter -->
          <div class="px-3.5 py-2.5 rounded-xl bg-white border border-slate-200 shadow-xs flex items-center justify-between shrink-0">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Tiến Độ Phiên Này</span>
              <div class="flex items-baseline gap-1.5 mt-0.5">
                <span class="text-3xl font-black text-slate-900 font-mono leading-none">{{ sessionPackedCount }}</span>
                <span class="text-xs font-bold text-slate-500">thùng ({{ sessionPackedCount * (selectedProduct?.packed_qty || 190) }} pcs)</span>
              </div>
            </div>
            
            <button 
              @click="resetSessionCount" 
              class="px-2 py-1 rounded bg-slate-50 hover:bg-rose-50 text-[11px] text-slate-400 hover:text-rose-600 transition-colors border border-slate-200 hover:border-rose-200 cursor-pointer flex items-center gap-1 font-bold"
              title="Reset số đếm"
            >
              <i class="fas fa-redo"></i> Reset
            </button>
          </div>

          <!-- Last Carton Print Result Card (Scrollable Body) -->
          <div class="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs flex-1 flex flex-col min-h-0 overflow-hidden">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100 mb-2 shrink-0">
              <div class="flex items-center gap-1.5">
                <i class="fas fa-box text-indigo-500"></i>
                <span class="font-bold text-xs text-slate-900">Thùng Vừa In Gần Nhất</span>
              </div>
              <span 
                v-if="lastPackedCarton"
                class="px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-emerald-100 text-emerald-800"
              >
                {{ lastPackedCarton.status || 'SUCCESS' }}
              </span>
            </div>

            <div v-if="lastPackedCarton" class="flex-1 min-h-0 flex flex-col justify-between text-xs">
              <div class="space-y-2 overflow-y-auto pr-1">
                <div>
                  <span class="text-[10px] text-slate-400 font-bold uppercase">Mã S/N Thùng:</span>
                  <p class="font-mono font-bold text-xs text-indigo-900 bg-indigo-50/60 p-1.5 rounded border border-indigo-100 select-all truncate mt-0.5">
                    {{ lastPackedCarton.carton_sn }}
                  </p>
                </div>

                <div class="grid grid-cols-2 gap-1.5">
                  <div class="bg-slate-50 p-1.5 rounded border border-slate-100">
                    <span class="text-[10px] text-slate-400 font-bold uppercase block">Trọng lượng:</span>
                    <p class="font-mono font-bold text-emerald-700 text-xs">
                      {{ lastPackedCarton.weight ? lastPackedCarton.weight.toFixed(3) : '-' }} kg
                    </p>
                  </div>
                  <div class="bg-slate-50 p-1.5 rounded border border-slate-100">
                    <span class="text-[10px] text-slate-400 font-bold uppercase block">Date Code:</span>
                    <p class="font-mono font-bold text-slate-700 text-xs">
                      {{ lastPackedCarton.date_code || '-' }}
                    </p>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-1.5">
                  <div class="bg-slate-50 p-1.5 rounded border border-slate-100">
                    <span class="text-[10px] text-slate-400 font-bold uppercase block">PO Number:</span>
                    <p class="font-mono font-semibold text-slate-700 text-xs truncate">
                      {{ lastPackedCarton.po_number || '-' }}
                    </p>
                  </div>
                  <div class="bg-slate-50 p-1.5 rounded border border-slate-100">
                    <span class="text-[10px] text-slate-400 font-bold uppercase block">Lot Number:</span>
                    <p class="font-mono font-semibold text-slate-700 text-xs truncate">
                      {{ lastPackedCarton.lot_number || '-' }}
                    </p>
                  </div>
                </div>

                <div class="text-[11px] text-slate-400 flex items-center justify-between pt-1">
                  <span>Thời gian:</span>
                  <span class="text-slate-600 font-medium">{{ formatDateTime(lastPackedCarton.created_at) }}</span>
                </div>
              </div>

              <div class="pt-2 border-t border-slate-100 mt-2 shrink-0">
                <button
                  @click="reprintLastCarton"
                  :disabled="isPrinting"
                  class="w-full py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <i class="fas fa-redo text-xs"></i>
                  <span>In Lại Thùng Này (Reprint)</span>
                </button>
              </div>
            </div>

            <!-- Empty State for Last Carton -->
            <div v-else class="flex-1 flex flex-col items-center justify-center text-center p-4 text-slate-400">
              <i class="fas fa-inbox text-2xl mb-1 opacity-30"></i>
              <p class="text-xs">Chưa có thùng nào được đóng trong phiên này</p>
            </div>
          </div>
        </div>
      </main>

      <!-- ================= MODALS ================= -->

      <!-- 1. Product Selection Modal -->
      <div v-if="showProductModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
        <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full p-6 border border-slate-100 flex flex-col gap-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100">
            <div class="flex items-center gap-2.5">
              <i class="fas fa-boxes text-indigo-600 text-lg"></i>
              <h2 class="font-bold text-lg text-slate-900">Chọn Sản Phẩm Khách Hàng UX</h2>
            </div>
            <div class="flex items-center gap-1.5">
              <button 
                @click="loadUXProducts" 
                :disabled="isLoadingProducts" 
                class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-slate-100 transition-all cursor-pointer"
                title="Làm mới danh sách sản phẩm từ CSDL"
              >
                <i :class="['fas fa-rotate', isLoadingProducts ? 'animate-spin text-indigo-600' : '']"></i>
              </button>
              <button @click="showProductModal = false" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg">
                <i class="fas fa-times text-lg"></i>
              </button>
            </div>
          </div>


          <div class="space-y-3 max-h-[60vh] overflow-y-auto">
            <div
              v-for="p in uxProducts"
              :key="p.id"
              @click="selectProduct(p)"
              :class="[
                'p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between',
                selectedProduct?.id === p.id
                  ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
                  : 'border-slate-200 hover:border-indigo-200 hover:bg-slate-50'
              ]"
            >
              <div>
                <div class="flex items-center gap-2">
                  <h4 class="font-black text-base text-slate-900 font-mono">{{ p.item_name }}</h4>
                  <span class="px-2 py-0.5 rounded-md bg-indigo-100 text-indigo-700 text-xs font-bold">{{ p.packed_qty }} PCS</span>
                </div>
                <p class="text-xs text-slate-500 mt-1">
                  Mfr P/N: <strong class="text-slate-700">{{ p.mfr_pn || 'NYS5998' }}</strong> | 
                  Tiền tố: <strong class="text-slate-700">{{ p.pkg_prefix || 'VHK0010237' }}</strong>
                </p>
                <p class="text-xs text-emerald-700 font-mono mt-0.5">
                  Dải trọng lượng: {{ p.min_weight?.toFixed(3) || '12.300' }}kg - {{ p.max_weight?.toFixed(3) || '12.700' }}kg
                </p>
              </div>
              <div v-if="selectedProduct?.id === p.id" class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs">
                <i class="fas fa-check"></i>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-2">
            <button
              @click="showProductModal = false"
              class="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-all cursor-pointer"
            >
              Đóng
            </button>
          </div>
        </div>
      </div>

      <!-- 2. Batch (PO & LOT) Configuration Modal -->
      <div v-if="showBatchModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
        <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-6 border border-slate-100 flex flex-col gap-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100">
            <div class="flex items-center gap-2.5">
              <i class="fas fa-tags text-indigo-600 text-lg"></i>
              <h2 class="font-bold text-lg text-slate-900">Cấu Hình PO & LOT Đóng Hàng</h2>
            </div>
            <button @click="showBatchModal = false" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg">
              <i class="fas fa-times text-lg"></i>
            </button>
          </div>

          <form @submit.prevent="saveBatchConfig" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Mã Đơn Hàng (PO Number) *
              </label>
              <input
                v-model="batchForm.po"
                type="text"
                required
                placeholder="Ví dụ: B432-22156381"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm font-mono"
              />
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Mã Số Lô (Lot Number) *
              </label>
              <input
                v-model="batchForm.lot"
                type="text"
                required
                placeholder="Ví dụ: 92608521"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm font-mono"
              />
            </div>

            <div class="flex justify-end gap-2.5 pt-2">
              <button
                type="button"
                @click="showBatchModal = false"
                class="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-all cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="submit"
                class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-all cursor-pointer shadow-md shadow-indigo-600/20"
              >
                Lưu Thông Tin
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 3. Settings Modal -->
      <SettingsModal 
        :show="showSettingsModal"
        @close="showSettingsModal = false"
      />

      <!-- 4. Emergency Reprint Modal -->
      <EmergencyReprintModal
        :show="showReprintModal"
        @close="showReprintModal = false"
        @reprint="handleEmergencyReprint"
      />

      <!-- 5. High-Visibility Weight Tolerance Error Modal -->
      <div 
        v-if="showToleranceErrorModal" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in"
        @click.self="showToleranceErrorModal = false"
      >
        <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full p-6 md:p-7 border-2 border-rose-500 flex flex-col gap-4 md:gap-5 relative overflow-hidden animate-shake">
          <!-- Top Accent Gradient Line -->
          <div class="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-rose-500 via-amber-500 to-rose-500"></div>

          <!-- Modal Header -->
          <div class="flex items-center gap-3.5">
            <div class="w-13 h-13 md:w-14 md:h-14 rounded-2xl bg-rose-100 border border-rose-200 flex items-center justify-center text-rose-600 text-2xl shrink-0 shadow-inner">
              <i class="fas fa-triangle-exclamation animate-bounce"></i>
            </div>
            <div>
              <span class="px-2 py-0.5 rounded-md bg-rose-100 text-rose-800 font-extrabold text-[10px] uppercase tracking-wider">
                Khóa In Trọng Lượng
              </span>
              <h2 class="font-black text-lg md:text-xl text-slate-900 leading-tight mt-0.5">
                {{ toleranceErrorDetails?.title || 'Trọng Lượng Không Hợp Lệ' }}
              </h2>
            </div>
          </div>

          <!-- Alert Message Detail Box -->
          <div class="p-3 rounded-xl bg-rose-50 border border-rose-200/80 text-rose-900 text-xs md:text-sm font-semibold flex items-center gap-2.5">
            <i class="fas fa-circle-exclamation text-rose-600 text-base shrink-0"></i>
            <span>{{ toleranceErrorDetails?.message || 'Trọng lượng trên cân không đạt dải tiêu chuẩn cho phép đóng gói.' }}</span>
          </div>

          <!-- Weight Comparison Cards Grid -->
          <div class="grid grid-cols-2 gap-2.5">
            <!-- Current Measured Weight -->
            <div class="p-3.5 rounded-2xl bg-slate-900 text-white flex flex-col justify-between shadow-md">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Trọng Lượng Cân Được</span>
              <div class="my-1">
                <span class="text-3xl md:text-4xl font-black font-mono text-rose-400">
                  {{ formatWeight(toleranceErrorDetails?.currentWeight) }}
                </span>
                <span class="text-xs font-bold text-slate-400 font-mono ml-1">kg</span>
              </div>
              <span class="text-[10px] font-bold text-rose-300 flex items-center gap-1">
                <i class="fas fa-times-circle"></i> NGOÀI DẢI CHO PHÉP
              </span>
            </div>

            <!-- Standard Product Target Range -->
            <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Dải Tiêu Chuẩn Cho Phép</span>
              <div class="space-y-1 my-1 text-xs">
                <div class="flex justify-between font-mono">
                  <span class="text-slate-500">Tối thiểu:</span>
                  <strong class="text-slate-800">{{ formatWeight(toleranceErrorDetails?.minWeight) }} kg</strong>
                </div>
                <div class="flex justify-between font-mono">
                  <span class="text-emerald-700 font-bold">Chuẩn:</span>
                  <strong class="text-emerald-700 font-black">{{ formatWeight(toleranceErrorDetails?.targetWeight) }} kg</strong>
                </div>
                <div class="flex justify-between font-mono">
                  <span class="text-slate-500">Tối đa:</span>
                  <strong class="text-slate-800">{{ formatWeight(toleranceErrorDetails?.maxWeight) }} kg</strong>
                </div>
              </div>
              <span class="text-[10px] font-bold text-emerald-700 flex items-center gap-1">
                <i class="fas fa-check-circle"></i> Tiêu Chuẩn Sản Phẩm
              </span>
            </div>
          </div>

          <!-- Operator Action Guide -->
          <div class="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-200">
            👉 <strong>Hướng dẫn:</strong> Vui lòng kiểm tra lại số lượng hàng trong thùng, đặt cân ngay ngắn và chờ cân ổn định trước khi thử in lại.
          </div>

          <!-- Confirm / Dismiss Action Button -->
          <button
            @click="showToleranceErrorModal = false"
            class="w-full py-3.5 rounded-xl bg-rose-600 hover:bg-rose-700 active:scale-[0.99] text-white font-black text-sm md:text-base transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-rose-600/30"
          >
            <i class="fas fa-check text-base"></i>
            <span>ĐÃ HIỂU & XÁC NHẬN [ENTER / ESC]</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSettingsStore } from '../core/stores/settings';
import { useSystemStore } from '../core/stores/system';
import catalogApi from '../features/catalog/api';
import packingApi from '../features/packing/api';
import printApi from '../features/print/api';
import scaleApi from '../features/packing/scaleApi';
import { evaluateScaleTolerance, type ScaleToleranceResult } from '../features/packing/utils/scaleTolerance';
import SettingsModal from '../features/settings/components/SettingsModal.vue';
import EmergencyReprintModal from '../features/print/components/EmergencyReprintModal.vue';
import type { Product, Carton, ScaleReading, ScaleStatus } from '../types/api';

const router = useRouter();
const settings = useSettingsStore();
const system = useSystemStore();

// Modals State
const showProductModal = ref(false);
const showBatchModal = ref(false);
const showSettingsModal = ref(false);
const showReprintModal = ref(false);
const showToleranceErrorModal = ref(false);
const toleranceErrorDetails = ref<{
  status: string;
  title: string;
  message: string;
  currentWeight: number;
  minWeight: number;
  targetWeight: number;
  maxWeight: number;
} | null>(null);

// Active Selection State
const uxProducts = ref<Product[]>([]);
const selectedProduct = ref<Product | null>(null);
const activePO = ref<string>(localStorage.getItem('ux_active_po') || 'B432-22156381');
const activeLot = ref<string>(localStorage.getItem('ux_active_lot') || '92608521');
const batchForm = ref({ po: activePO.value, lot: activeLot.value });

// Scale State
const scaleReading = ref<ScaleReading>({
  weight: 0.0,
  unit: 'kg',
  is_stable: false,
  is_tare: false,
  is_net: false,
});
const scaleStatus = ref<ScaleStatus>({
  connected: false,
  port: '',
  baudrate: 9600,
  is_streaming: false,
});

// S/N Sequence State (Auto Increment vs Manual Input)
const isAutoSN = ref<boolean>(true);
const autoSequence = ref<number>(1);
const manualSequence = ref<number | null>(null);
const snCheckError = ref<string>('');
const currentYYMM = ref<string>('');

// Printing & Session State
const isPrinting = ref(false);
const sessionPackedCount = ref<number>(Number(sessionStorage.getItem('ux_session_count') || '0'));
const lastPackedCarton = ref<Carton | null>(null);

// Scale Stream Interval ID
let scalePollInterval: any = null;
let statusPollInterval: any = null;

// Fetch Next S/N sequence from backend
const fetchNextSN = async () => {
  if (!selectedProduct.value) return;
  try {
    const res = await catalogApi.getNextSN(selectedProduct.value.id);
    if (res.data) {
      autoSequence.value = res.data.next_seq || 1;
      currentYYMM.value = res.data.yymm || '';
      if (manualSequence.value === null || isAutoSN.value) {
        manualSequence.value = autoSequence.value;
      }
    }
  } catch (err) {
    console.warn('Could not fetch next S/N sequence:', err);
  }
};

// Preview Carton S/N
const currentSNPreview = computed<string>(() => {
  if (!selectedProduct.value) return '-';
  const prefix = selectedProduct.value.pkg_prefix || 'VHK0010237';
  let yymm = currentYYMM.value;
  if (!yymm || yymm.length !== 4) {
    const now = new Date();
    const yy = String(now.getFullYear()).slice(-2);
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    yymm = `${yy}${mm}`;
  }
  const seq = isAutoSN.value ? autoSequence.value : (manualSequence.value || 1);
  return `${prefix}${yymm}${String(seq).padStart(6, '0')}`;
});

// Toggle between Auto and Manual S/N mode
const toggleSNMode = () => {
  if (isAutoSN.value) {
    isAutoSN.value = false;
    manualSequence.value = autoSequence.value;
    checkManualSN();
  } else {
    isAutoSN.value = true;
    snCheckError.value = '';
    fetchNextSN();
  }
};

let checkSNTimer: any = null;
const checkManualSN = () => {
  snCheckError.value = '';
  if (!manualSequence.value || manualSequence.value <= 0) {
    snCheckError.value = 'Số thùng phải lớn hơn 0';
    return;
  }
  clearTimeout(checkSNTimer);
  checkSNTimer = setTimeout(async () => {
    try {
      const sn = currentSNPreview.value;
      const res = await printApi.searchCarton(sn);
      if (res.data && res.data.id) {
        snCheckError.value = `Sê-ri ${sn} đã tồn tại trong lịch sử!`;
      }
    } catch {
      // Not found is clean/valid
      snCheckError.value = '';
    }
  }, 300);
};

// Evaluate Tolerance Reactively
const toleranceResult = computed<ScaleToleranceResult>(() => {
  return evaluateScaleTolerance({
    isConnected: scaleStatus.value.connected,
    currentWeight: scaleReading.value.weight,
    isStable: scaleReading.value.is_stable,
    product: selectedProduct.value ? {
      min_weight: selectedProduct.value.min_weight ?? 12.300,
      target_weight: selectedProduct.value.target_weight ?? 12.500,
      max_weight: selectedProduct.value.max_weight ?? 12.700,
    } : null,
  });
});

// Scale Gauge Needle Calculation (0% - 100%)
const calculateGaugePercent = (currentWeight: number): number => {
  const min = selectedProduct.value?.min_weight ?? 0.150;
  const max = selectedProduct.value?.max_weight ?? 0.200;
  const range = max - min;
  if (range <= 0) return 50;

  // Safe green zone spans 16.6% to 83.4%
  const gaugeMin = min - 0.25 * range;
  const gaugeMax = max + 0.25 * range;
  const percent = ((currentWeight - gaugeMin) / (gaugeMax - gaugeMin)) * 100;
  return Math.min(Math.max(percent, 2), 98);
};

// Formatting Helpers
const formatWeight = (val?: number) => {
  if (val === undefined || val === null) return '0.000';
  return val.toFixed(3);
};

const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleTimeString('vi-VN') + ' ' + d.toLocaleDateString('vi-VN');
};

const getToleranceIcon = (status: string) => {
  switch (status) {
    case 'READY': return 'fas fa-check';
    case 'UNSTABLE': return 'fas fa-wave-square';
    case 'UNDERWEIGHT': return 'fas fa-arrow-down';
    case 'OVERWEIGHT': return 'fas fa-arrow-up';
    default: return 'fas fa-unlink';
  }
};

const getToleranceTitle = (status: string) => {
  switch (status) {
    case 'READY': return 'ĐẠT CHUẨN TRỌNG LƯỢNG';
    case 'UNSTABLE': return 'CÂN CHƯA ỔN ĐỊNH';
    case 'UNDERWEIGHT': return 'THIẾU TRỌNG LƯỢNG';
    case 'OVERWEIGHT': return 'THỪA TRỌNG LƯỢNG';
    default: return 'CHƯA KẾT NỐI CÂN';
  }
};

// Switch Customer Navigation
const switchCustomer = () => {
  localStorage.removeItem('selected_customer');
  router.push('/');
};

// Batch Config Form Save
const saveBatchConfig = () => {
  activePO.value = batchForm.value.po.trim();
  activeLot.value = batchForm.value.lot.trim();
  localStorage.setItem('ux_active_po', activePO.value);
  localStorage.setItem('ux_active_lot', activeLot.value);
  showBatchModal.value = false;
  system.showNotification('Đã cập nhật PO & LOT thành công', 'success');
};

// Product Selection & Dynamic Refresh
const isLoadingProducts = ref(false);

const loadUXProducts = async () => {
  isLoadingProducts.value = true;
  try {
    const res = await catalogApi.getProductsByCustomerCode('UX');
    uxProducts.value = res.data;

    // Refresh selectedProduct if currently chosen
    if (selectedProduct.value) {
      const refreshed = uxProducts.value.find(p => p.id === selectedProduct.value!.id);
      if (refreshed) {
        selectedProduct.value = refreshed;
      }
    }
  } catch (err) {
    console.error('Failed to reload UX products', err);
  } finally {
    isLoadingProducts.value = false;
  }
};

const openProductModal = async () => {
  showProductModal.value = true;
  await loadUXProducts();
};

const selectProduct = async (p: Product) => {
  try {
    const res = await catalogApi.getProduct(p.id);
    selectedProduct.value = res.data || p;
  } catch {
    selectedProduct.value = p;
  }
  localStorage.setItem('ux_selected_product_id', String(p.id));
  showProductModal.value = false;
  system.showNotification(`Đã chọn sản phẩm ${selectedProduct.value.item_name}`, 'success');
  fetchNextSN();
};


// Scale Operations
const handleTare = async () => {
  try {
    const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
    await scaleApi.tareScale(agentUrl);
    system.showNotification('Đã gửi lệnh trừ bì (Tare) tới cân', 'info');
  } catch (err: any) {
    system.showNotification('Lỗi trừ bì: ' + err.message, 'error');
  }
};

const handleZero = async () => {
  try {
    const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
    await scaleApi.zeroScale(agentUrl);
    system.showNotification('Đã gửi lệnh Zero tới cân', 'info');
  } catch (err: any) {
    system.showNotification('Lỗi Zero: ' + err.message, 'error');
  }
};

// Scale Polling Stream Loop
const pollScale = async () => {
  const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
  try {
    const reading = await scaleApi.getScaleCurrent(agentUrl);
    if (reading) {
      scaleReading.value = reading;
      scaleStatus.value.connected = true;
    }
  } catch (err) {
    scaleStatus.value.connected = false;
  }
};

const pollScaleStatus = async () => {
  const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
  try {
    const status = await scaleApi.getScaleStatus(agentUrl);
    if (status) {
      scaleStatus.value = status;
    }
  } catch (err) {
    scaleStatus.value.connected = false;
  }
};

// Main Print Execution Flow (Weigh & Pack)
const triggerWeighAndPrint = async () => {
  if (!selectedProduct.value) {
    system.showNotification('Vui lòng chọn sản phẩm trước khi in', 'warning');
    showProductModal.value = true;
    return;
  }

  if (!activePO.value || !activeLot.value) {
    system.showNotification('Vui lòng nhập PO và LOT trước khi in', 'warning');
    showBatchModal.value = true;
    return;
  }

  if (!toleranceResult.value.canPrint) {
    toleranceErrorDetails.value = {
      status: toleranceResult.value.status,
      title: getToleranceTitle(toleranceResult.value.status),
      message: toleranceResult.value.message,
      currentWeight: scaleReading.value.weight,
      minWeight: selectedProduct.value?.min_weight ?? 0.150,
      targetWeight: selectedProduct.value?.target_weight ?? 0.180,
      maxWeight: selectedProduct.value?.max_weight ?? 0.200,
    };
    showToleranceErrorModal.value = true;
    return;
  }

  if (!isAutoSN.value) {
    if (!manualSequence.value || manualSequence.value <= 0) {
      system.showNotification('Vui lòng nhập số thùng hợp lệ (> 0)', 'warning');
      return;
    }
    if (snCheckError.value) {
      system.showNotification(snCheckError.value, 'error');
      return;
    }
  }

  if (isPrinting.value) return;

  isPrinting.value = true;
  const currentWeight = scaleReading.value.weight;

  try {
    // 1. Call Backend API to Allocate UX SN and generate A11 BTXML
    const res = await packingApi.weighPackCarton({
      product_id: selectedProduct.value.id,
      weight: currentWeight,
      po_number: activePO.value,
      lot_number: activeLot.value,
      printer_name: settings.printerName || undefined,
      template_path: settings.templatePath || undefined,
      station_id: settings.stationId || undefined,
      custom_sn: isAutoSN.value ? undefined : (manualSequence.value || undefined),
    });

    const newCarton = res.data;
    const btxmlContent = (newCarton as any).btxml;

    if (!btxmlContent) {
      throw new Error('Backend did not return BTXML payload');
    }

    // 2. Send BTXML to Print Agent
    const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
    const printResult = await printApi.agentPrint(
      agentUrl,
      btxmlContent,
      settings.printerName || undefined,
      settings.localTemplateDir || undefined
    );

    // If PDF export, trigger automatic download / view
    if (printResult?.type === 'pdf' && printResult?.data) {
      const link = document.createElement('a');
      link.href = `data:application/pdf;base64,${printResult.data}`;
      link.download = `${newCarton.carton_sn || 'label'}.pdf`;
      link.click();
    }

    // 3. Confirm SUCCESS status on backend
    try {
      await printApi.updateCartonStatus(newCarton.id, 'SUCCESS');
      newCarton.status = 'SUCCESS';
    } catch (e) {
      console.warn('Status confirmation warning:', e);
    }

    // 4. Update session and last carton
    lastPackedCarton.value = newCarton;
    sessionPackedCount.value += 1;
    sessionStorage.setItem('ux_session_count', String(sessionPackedCount.value));

    // 5. Advance serial number counter
    if (isAutoSN.value) {
      autoSequence.value += 1;
    } else {
      manualSequence.value = (manualSequence.value || 1) + 1;
      checkManualSN();
    }

    system.showNotification(`Đã in thành công tem thùng: ${newCarton.carton_sn}`, 'success');

  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.response?.data?.error || err.message || 'Lỗi không xác định khi in';
    system.showNotification(`In thất bại: ${errorMsg}`, 'error');
  } finally {
    isPrinting.value = false;
  }
};

// Reprint Last Carton
const reprintLastCarton = async () => {
  if (!lastPackedCarton.value) return;
  await handleEmergencyReprint(lastPackedCarton.value);
};

// Emergency Reprint Handler
const handleEmergencyReprint = async (carton: Carton) => {
  try {
    isPrinting.value = true;
    const res = await printApi.reprintCarton(
      carton.id,
      settings.templatePath || '',
      settings.printerName || ''
    );
    const reprintCarton = res.data;
    const btxml = (reprintCarton as any).btxml;

    if (btxml) {
      const agentUrl = settings.agentUrl || 'http://127.0.0.1:8080';
      const printResult = await printApi.agentPrint(agentUrl, btxml, settings.printerName, settings.localTemplateDir);
      if (printResult?.type === 'pdf' && printResult?.data) {
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${printResult.data}`;
        link.download = `Reprint_${carton.carton_sn}.pdf`;
        link.click();
      }
      system.showNotification(`In lại thành công tem thùng: ${carton.carton_sn}`, 'success');
      showReprintModal.value = false;
    } else {
      throw new Error('No BTXML returned for reprint');
    }
  } catch (err: any) {
    system.showNotification(`In lại thất bại: ${err.response?.data?.error || err.message}`, 'error');
  } finally {
    isPrinting.value = false;
  }
};

// Session Counter Reset
const resetSessionCount = () => {
  if (confirm('Bạn có chắc muốn đặt lại bộ đếm số thùng trong ca về 0?')) {
    sessionPackedCount.value = 0;
    sessionStorage.setItem('ux_session_count', '0');
  }
};

// Global Hotkey (F9) Listener
const handleKeyDown = (event: KeyboardEvent) => {
  if (showToleranceErrorModal.value) {
    if (event.key === 'Enter' || event.key === 'Escape' || event.key === ' ') {
      event.preventDefault();
      showToleranceErrorModal.value = false;
      return;
    }
  }

  if (event.key === 'F9') {
    event.preventDefault();
    triggerWeighAndPrint();
  }
};


// Lifecycle Hooks
onMounted(async () => {
  // Load UX Products
  await loadUXProducts();

  // Auto-select saved or first product
  const savedProdId = localStorage.getItem('ux_selected_product_id');
  if (savedProdId) {
    selectedProduct.value = uxProducts.value.find(p => p.id === Number(savedProdId)) || uxProducts.value[0] || null;
  } else if (uxProducts.value.length > 0) {
    selectedProduct.value = uxProducts.value[0];
  }

  if (selectedProduct.value) {
    await fetchNextSN();
  }


  // Start polling scale
  pollScale();
  pollScaleStatus();
  scalePollInterval = setInterval(pollScale, 100);
  statusPollInterval = setInterval(pollScaleStatus, 2000);

  // Register F9 hotkey
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  if (scalePollInterval) clearInterval(scalePollInterval);
  if (statusPollInterval) clearInterval(statusPollInterval);
  window.removeEventListener('keydown', handleKeyDown);
});
</script>
