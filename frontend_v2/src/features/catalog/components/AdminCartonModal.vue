<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
    <form class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl space-y-4" @submit.prevent="submit">
      <div class="flex items-start justify-between gap-4">
        <div><h2 class="text-xl font-black text-slate-900">Tạo Carton Admin</h2><p class="text-sm text-slate-500">{{ product?.item_name }} · {{ product?.template_type }}</p></div>
        <button type="button" class="text-slate-400" @click="$emit('close')">✕</button>
      </div>
      <label class="block text-sm font-bold">Số thứ tự<input v-model.number="form.sequence" min="1" required type="number" class="mt-1 w-full rounded-lg border p-2" /></label>
      <label class="block text-sm font-bold">Lý do<input v-model.trim="form.reason" required class="mt-1 w-full rounded-lg border p-2" placeholder="Ví dụ: Bổ sung lịch sử tem" /></label>
      <label class="block text-sm font-bold">Công lệnh *<input v-model.trim="form.job_order" required class="mt-1 w-full rounded-lg border p-2" placeholder="Ví dụ: JO-2026-001" /></label>
      <label class="block text-sm font-bold">Trọng lượng (kg)<input v-model.number="form.weight" required type="number" step="0.001" class="mt-1 w-full rounded-lg border p-2" /></label>
      <label class="block text-sm font-bold">PO <span v-if="product?.template_type === 'erro_04'" class="text-rose-600">*</span><input v-model.trim="form.po_number" :required="product?.template_type === 'erro_04'" class="mt-1 w-full rounded-lg border p-2" /></label>
      <label class="block text-sm font-bold">Lot <span v-if="product?.template_type === 'erro_04'" class="text-rose-600">*</span><input v-model.trim="form.lot_number" :required="product?.template_type === 'erro_04'" class="mt-1 w-full rounded-lg border p-2" /></label>
      <div class="rounded-lg bg-amber-50 p-3 text-xs text-amber-900">Carton sẽ được tạo với Mã trạm <b>ADMIN</b>. Số đã tạo không thể thu hồi; in lỗi sẽ dùng Reprint.</div>
      <div class="flex justify-end gap-2"><button type="button" class="rounded-lg px-4 py-2" @click="$emit('close')">Hủy</button><button :disabled="submitting" class="rounded-lg bg-indigo-600 px-4 py-2 font-bold text-white disabled:opacity-50">{{ submitting ? 'Đang tạo…' : 'Tạo và in' }}</button></div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';
import type { Product } from '../../../types/api';
const props = defineProps<{ show: boolean; product: Product | null; submitting: boolean }>();
const emit = defineEmits<{ close: []; submit: [data: { sequence: number; reason: string; job_order: string; weight: number; po_number?: string; lot_number?: string }] }>();
const form = reactive({ sequence: 1, reason: '', job_order: '', weight: 0, po_number: '', lot_number: '' });
watch(() => props.product, (product) => { form.sequence = 1; form.reason = ''; form.job_order = ''; form.weight = product?.target_weight ?? 0; form.po_number = ''; form.lot_number = ''; }, { immediate: true });
const submit = () => emit('submit', { ...form, po_number: form.po_number || undefined, lot_number: form.lot_number || undefined });
</script>
