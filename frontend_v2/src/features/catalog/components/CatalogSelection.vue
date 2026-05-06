<template>
  <section class="selection-panel">
    <div class="selection-header-row">
      <div class="control-group customer-select">
        <label>{{ t('catalog.customer') }}</label>
        <select v-model="selectedCustomerId" @change="onCustomerChange" class="modern-select">
          <option value="" disabled>{{ t('catalog.choose_customer') }}</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
        </select>
      </div>

      <div class="control-group product-search" v-if="selectedCustomerId">
        <label>{{ t('catalog.search_product') }}</label>
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            v-model="productSearch" 
            :placeholder="t('catalog.filter_items')" 
            class="modern-input-small"
            ref="productSearchInput"
          />
        </div>
      </div>
    </div>

    <div class="control-group" v-if="selectedCustomerId">
      <div class="product-grid">
        <div 
          v-for="p in filteredProducts" 
          :key="p.id" 
          class="product-card"
          @click="$emit('select-product', p)"
        >
          <h3>{{ p.item_name }}</h3>
          <p>UPC: {{ p.upc }}</p>
          <div class="qty-tag">{{ t('catalog.target') }}: {{ p.packed_qty }}</div>
        </div>
        <div v-if="filteredProducts.length === 0" class="no-results-hint">
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

<style scoped>
.selection-header-row {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.customer-select {
  width: 250px;
  margin-bottom: 0;
}
.product-search {
  flex: 1;
  margin-bottom: 0;
}
.customer-select label, .product-search label {
  margin-bottom: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  display: block;
}
.control-group label {
  display: block;
  margin-bottom: 10px;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}
.modern-select {
  width: 100%;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  color: #1e293b;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
  height: 42px;
  padding: 0 12px;
  font-size: 0.95rem;
}
.modern-select:focus { border-color: #3b82f6; }
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.search-input-wrapper .search-icon {
  position: absolute;
  left: 18px;
  color: #3b82f6;
  font-size: 0.95rem;
}
.search-input-wrapper input.modern-input-small {
  padding-left: 48px;
  width: 100%;
  height: 42px;
}
.modern-input-small {
  padding: 10px 14px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}
.modern-input-small:focus {
  background: white;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-top: 20px;
}
.product-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.product-card:hover {
  background: white;
  transform: translateY(-4px);
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.product-card h3 { margin: 0 0 8px 0; color: #0f172a; }
.product-card p { color: #64748b; font-size: 0.85rem; margin-bottom: 12px; }
.qty-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #eff6ff;
  color: #2563eb;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}
.no-results-hint {
  grid-column: 1 / -1;
  padding: 40px;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px dashed #e2e8f0;
}
</style>
