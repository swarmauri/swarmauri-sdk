<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

interface Filter {
  type: 'text' | 'dropdown' | 'date';
  label: string;
  options?: string[];
  value: string | Date | null;
}

export default defineComponent({
  name: 'DataFilterPanel',
  props: {
    filters: {
      type: Array as () => Filter[],
      required: true,
    },
    disabled: Boolean,
  },
  setup(props) {
    const activeFilters = ref<Filter[]>([...props.filters]);
    const isPanelCollapsed = ref(true);

    const togglePanel = () => {
      isPanelCollapsed.value = !isPanelCollapsed.value;
    };

    const applyFilters = () => {
      // Logic to apply filters
    };

    const clearFilters = () => {
      activeFilters.value = props.filters.map(filter => ({ ...filter, value: null }));
    };

    watch(activeFilters, applyFilters, { deep: true });

    return {
      activeFilters,
      isPanelCollapsed,
      togglePanel,
      clearFilters,
    };
  },
});
</script>

<template>
  <div class="data-filter-panel" :class="{ disabled: disabled }">
    <button @click="togglePanel">{{ isPanelCollapsed ? 'Show Filters' : 'Hide Filters' }}</button>
    <div v-if="!isPanelCollapsed" class="filters">
      <div v-for="(filter, index) in activeFilters" :key="index" class="filter">
        <label>{{ filter.label }}</label>
        <div v-if="filter.type === 'text'">
          <input type="text" v-model="filter.value" :disabled="disabled" />
        </div>
        <div v-else-if="filter.type === 'dropdown'">
          <select v-model="filter.value" :disabled="disabled">
            <option v-for="option in filter.options" :key="option" :value="option">{{ option }}</option>
          </select>
        </div>
        <div v-else-if="filter.type === 'date'">
          <input type="date" v-model="filter.value" :disabled="disabled" />
        </div>
      </div>
      <button @click="clearFilters" :disabled="disabled">Clear Filters</button>
    </div>
  </div>
</template>

<style scoped lang="css">
.data-filter-panel {
  --panel-bg: #f4f4f9;
  --panel-border: #ccc;
  --panel-text-color: #333;
  --button-bg: #007bff;
  --button-color: #ffffff;
  --button-disabled-bg: #d6d6d6;
  --button-disabled-color: #8a8a8a;
}

.data-filter-panel {
  padding: 16px;
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  color: var(--panel-text-color);
}

button {
  background-color: var(--button-bg);
  color: var(--button-color);
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  margin-top: 8px;
}

button:disabled {
  background-color: var(--button-disabled-bg);
  color: var(--button-disabled-color);
  cursor: not-allowed;
}

.filters {
  margin-top: 16px;
}

.filter {
  margin-bottom: 12px;
}
</style>