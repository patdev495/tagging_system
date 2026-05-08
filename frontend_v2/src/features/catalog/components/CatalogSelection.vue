<template>
  <section class="selection-panel">
    <div class="flex gap-4 items-center mb-6 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div class="w-[250px]">
        <label class="mb-1.5 text-[0.75rem] font-bold text-slate-400 uppercase block">{{ t('catalog.customer') }}</label>
        <select v-model="selectedCustomerId" @change="onCustomerChange" class="w-full h-[42px] px-3 py-0 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-[0.95rem] outline-none transition-colors focus:border-blue-500">
          <option value="" disabled>{{ t('catalog.choose_customer') }}</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
        </select>
      </div>

      <div class="flex-1" v-if="selectedCustomerId">
        <label class="mb-1.5 text-[0.75rem] font-bold text-slate-400 uppercase block">{{ t('catalog.search_product') }}</label>
        <div class="relative flex items-center">
          <i class="fas fa-search absolute left-[18px] text-blue-500 text-[0.95rem]"></i>
          <input 
            v-model="productSearch" 
            :placeholder="t('catalog.filter_items')" 
            class="pl-12 w-full h-[42px] bg-white border border-slate-300 rounded-[10px] text-[1rem] font-semibold text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-3 focus:ring-blue-500/10"
            ref="productSearchInput"
          />
        </div>
      </div>
    </div>

    <div v-if="selectedCustomerId">
      <div class="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-5 mt-5">
        <div 
          v-for="p in filteredProducts" 
          :key="p.id" 
          class="bg-slate-50 border border-slate-200 rounded-2xl p-5 cursor-pointer transition-all duration-200 ease-out hover:bg-white hover:-translate-y-1 hover:border-blue-500 hover:shadow-xl"
          @click="$emit('select-product', p)"
        >
          <h3 class="m-0 mb-2 text-slate-900 font-bold">{{ p.item_name }}</h3>
          <p class="text-slate-500 text-[0.85rem] mb-3">UPC: {{ p.upc }}</p>
          <div class="inline-block px-2.5 py-1 bg-blue-50 text-blue-600 rounded-md text-[0.75rem] font-semibold">{{ t('catalog.target') }}: {{ p.packed_qty }}</div>
        </div>
        <div v-if="filteredProducts.length === 0" class="col-span-full p-10 text-center text-slate-400 italic bg-slate-50 rounded-xl border border-dashed border-slate-200">
           {{ t('catalog.no_products') }}
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import catalogApi from '../api';

const { t } = useI18n();

const emit = defineEmits(['select-product']);

const customers = ref([]);
const products = ref([]);
const selectedCustomerId = ref('');
const productSearch = ref('');
const productSearchInput = ref(null);

const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value;
  const q = productSearch.value.toLowerCase();
  return products.value.filter(p => 
    p.item_name.toLowerCase().includes(q) || 
    p.upc.toLowerCase().includes(q)
  );
});

const loadCustomers = async () => {
  try {
    const res = await catalogApi.getCustomers();
    customers.value = res.data;
    if (customers.value.length > 0 && !selectedCustomerId.value) {
      selectedCustomerId.value = customers.value[0].id;
      loadProducts();
      nextTick(() => {
        if (productSearchInput.value) productSearchInput.value.focus();
      });
    }
  } catch (err) {
    console.error('Cannot connect to API', err);
  }
};

const loadProducts = async () => {
  if (!selectedCustomerId.value) return;
  try {
    const res = await catalogApi.getCustomerProducts(selectedCustomerId.value);
    products.value = res.data;
    productSearch.value = '';
    nextTick(() => {
      if (productSearchInput.value) productSearchInput.value.focus();
    });
  } catch (err) {
    console.error('Error loading products', err);
  }
};

const onCustomerChange = () => {
  loadProducts();
};

const focusSearch = () => {
  nextTick(() => {
    if (productSearchInput.value) productSearchInput.value.focus();
  });
};

onMounted(() => {
  loadCustomers();
});

defineExpose({ focusSearch });
</script>
