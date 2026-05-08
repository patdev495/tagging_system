<template>
  <div class="min-h-screen p-3 md:p-4 text-slate-800 flex justify-center bg-radial-at-tr from-slate-50 to-slate-200">
    <div class="w-full max-w-[1100px] transition-all duration-500 ease-out flex flex-col bg-white/95 backdrop-blur-2xl border border-white/80 rounded-[20px] p-4 shadow-2xl shadow-slate-900/5" :class="{ 'max-w-[1550px]': currentProduct }">
      <AppHeader
        :isAudioActive="isAudioActive"
        @toggle-audio="toggleAudio"
        @show-emergency="showEmergencyModal = true"
        @show-settings="showSettings = true"
        @home="resetSession"
      />

      <CatalogSelection
        v-if="!currentProduct"
        ref="catalogRef"
        @select-product="selectProduct"
      />

      <section class="mt-2.5" v-else>
        <div class="flex gap-6 items-start lg:flex-col lg:items-stretch">
          <div class="flex-[1.4] min-w-0">
            <SessionHeader
              ref="sessionRef"
              :product="currentProduct"
              v-model:jobOrder="jobOrder"
              v-model:cartonOrigin="cartonOrigin"
              v-model:customSN="customSN"
              v-model:isSNManual="isSNManual"
              v-model:snPattern="snPattern"
              v-model:customYYMM="customYYMM"
              :suggestedSNValue="suggestedSNValue"
              :snPreview="snPreview"
              :snExists="snExists"
              @back="resetSession"
              @focus-scan="focusScan"
            />

            <div v-if="isRescanMode" class="bg-orange-50 border border-orange-100 rounded-xl p-2.5 md:p-4 mb-4 flex justify-between items-center text-orange-900 animate-in">
              <div class="flex items-center gap-3">
                <i class="fas fa-redo-alt fa-spin text-orange-500"></i>
                <span><strong>{{ t('packing.rescan_mode', { sn: rescanCartonSN }) }}</strong></span>
              </div>
              <button @click="isRescanMode = false; rescanCartonSN = '';" class="bg-orange-100 border-none px-3 py-1.5 rounded-lg text-orange-900 font-semibold cursor-pointer transition-colors hover:bg-orange-200 flex items-center gap-1.5 text-[0.85rem]">
                <i class="fas fa-times"></i> {{ t('packing.cancel') }}
              </button>
            </div>

            <div class="mb-4 bg-white p-3 md:p-4 rounded-2xl shadow-inner-sm border border-slate-100">
              <!-- Cảnh báo Agent Offline (Chỉ hiện khi ở chế độ Local) -->
              <div v-if="settings.printMode === 'local' && !agentConnected" class="bg-linear-to-br from-rose-50 to-rose-100 border-2 border-rose-500 rounded-xl p-3 md:p-4 mb-4 shadow-md shadow-rose-500/10 animate-in">
                <div class="flex items-center gap-3 text-rose-800">
                  <i class="fas fa-exclamation-triangle fa-beat text-[1.5rem] text-rose-500"></i>
                  <span class="text-[0.95rem]"><strong>{{ t('packing.agent_offline') }}</strong></span>
                </div>
              </div>

              <!-- Cảnh báo Thiếu File Tem -->
              <div v-if="settings.printMode === 'local' && agentConnected && templateMissing" class="bg-linear-to-br from-orange-50 to-orange-100 border-2 border-orange-500 rounded-xl p-3 md:p-4 mb-4 shadow-md shadow-orange-500/10 animate-in">
                <div class="flex items-center gap-3 text-orange-800">
                  <i class="fas fa-file-circle-exclamation fa-beat text-[1.5rem] text-orange-500"></i>
                  <span class="text-[0.95rem]"><strong>{{ t('packing.template_missing', { file: templateFilename }) }}</strong></span>
                </div>
              </div>

              <div class="flex justify-between items-end mb-2">
                <span class="text-[1.25rem] font-extrabold text-slate-900">{{ scannedItems.length }} / {{ currentProduct?.packed_qty || 0 }}</span>
                <span class="text-[0.9rem] text-blue-600 font-bold bg-blue-50 px-2.5 py-1 rounded-lg">{{ progressPercent }}%</span>
              </div>
              <div class="h-3.5 bg-slate-100 rounded-full overflow-hidden relative">
                <div class="h-full bg-linear-to-r from-blue-500 to-emerald-500 transition-all duration-600 ease-out shadow-[0_0_10px_rgba(59,130,246,0.3)]" :style="{ width: progressPercent + '%' }"></div>
              </div>
            </div>

            <PrintStatusBanner
              :lastCarton="lastCarton"
              :agentErrorMessage="agentErrorMessage"
              @retry="finalizeCarton(true)"
            />

            <ScanBuffer
              ref="scanRef"
              v-model:scanBuffer="scanBuffer"
              :disabled="isProcessing || (settings.printMode === 'local' && (!agentConnected || templateMissing))"
              :placeholder="(settings.printMode === 'local' && !agentConnected) ? t('packing.scan_placeholder_offline') : (templateMissing ? t('packing.scan_placeholder_missing') : t('packing.scan_placeholder'))"
              :jobOrder="jobOrder"
              :awaitingNext="awaitingNext"
              :invalidScans="invalidScans"
              :overflowScans="overflowScans"
              :allowPartial="currentProduct && currentProduct.allow_partial === 1"
              :scannedCount="scannedItems.length"
              @scan="handleScan"
              @next-carton="startNextCarton"
              @pack-now="finalizeCarton()"
              @clear-invalid="invalidScans = []"
              @clear-overflow="overflowScans = []"
            />
          </div>

          <ScannedList
            :items="scannedItems"
            @clear="scannedItems = []"
          />
        </div>
      </section>
    </div>

    <SettingsModal :show="showSettings" @close="showSettings = false" />
    <EmergencyReprintModal 
      :show="showEmergencyModal" 
      @close="showEmergencyModal = false" 
      @reprint="handleEmergencyReprint" 
      @rescan="handleRescan"
    />
  </div>
</template>
