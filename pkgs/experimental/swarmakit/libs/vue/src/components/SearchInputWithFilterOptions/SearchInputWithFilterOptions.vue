<template>
  <div class="search-container">
    <input 
      type="text" 
      :placeholder="placeholder" 
      :disabled="disabled"
      aria-label="Search input"
      v-model="query"
      @input="onInput"
    />
    <button 
      :aria-pressed="filtersActive" 
      @click="toggleFilters"
    >
      Filters
    </button>
    <div v-if="filtersActive" class="filter-options">
      <slot name="filters"></slot>
    </div>
    <div v-if="noResults" class="no-results">
      No Results Found
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SearchInputWithFilterOptions',
  props: {
    placeholder: {
      type: String,
      default: 'Search...',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    filtersActive: {
      type: Boolean,
      default: false,
    },
    noResults: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:filtersActive', 'input'],
  setup(props, { emit }) {
    const query = ref('');

    const onInput = () => {
      emit('input', query.value);
    };

    const toggleFilters = () => {
      emit('update:filtersActive', !props.filtersActive);
    };

    return {
      query,
      onInput,
      toggleFilters,
    };
  },
});
</script>

<style scoped>
@import './SearchInputWithFilterOptions.css';
</style>