<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SortControl',
  props: {
    columns: {
      type: Array as () => string[],
      default: () => [],
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['sort'],
  setup(props, { emit }) {
    const sortState = ref<{ [key: string]: 'asc' | 'desc' | null }>({});
    
    const toggleSort = (column: string) => {
      if (props.disabled) return;
      if (!sortState.value[column] || sortState.value[column] === 'desc') {
        sortState.value[column] = 'asc';
      } else {
        sortState.value[column] = 'desc';
      }
      emit('sort', { column, order: sortState.value[column] });
    };

    const getSortIcon = (column: string) => {
      return sortState.value[column] === 'asc' ? '↑' : sortState.value[column] === 'desc' ? '↓' : '';
    };

    return {
      sortState,
      toggleSort,
      getSortIcon,
    };
  },
});
</script>

<template>
  <div class="sort-control">
    <div
      v-for="column in columns"
      :key="column"
      class="sort-button"
      :class="{ disabled: disabled }"
      @click="toggleSort(column)"
      :aria-disabled="disabled"
      role="button"
    >
      {{ column }} <span>{{ getSortIcon(column) }}</span>
    </div>
  </div>
</template>

<style scoped lang="css">
.sort-control {
  display: flex;
  gap: 10px;
}

.sort-button {
  padding: 8px;
  border: 1px solid var(--button-border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.sort-button:hover {
  background-color: var(--button-hover-bg);
}

.sort-button.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.sort-button span {
  margin-left: 5px;
}
</style>