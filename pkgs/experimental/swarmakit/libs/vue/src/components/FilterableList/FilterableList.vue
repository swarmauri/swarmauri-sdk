<template>
  <div class="filterable-list">
    <input
      type="text"
      v-model="filterText"
      placeholder="Filter items..."
      aria-label="Filter items"
      class="filter-input"
    />
    <button @click="clearFilter" class="clear-button">Clear Filter</button>
    <ul role="list" aria-label="Filtered list">
      <li
        v-for="(item, index) in filteredItems"
        :key="index"
        class="list-item"
      >
        {{ item }}
      </li>
    </ul>
    <p v-if="filteredItems.length === 0" class="no-results">No results found</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'FilterableList',
  props: {
    items: {
      type: Array as () => string[],
      required: true,
    },
  },
  setup(props) {
    const filterText = ref('');

    const filteredItems = computed(() =>
      props.items.filter((item) =>
        item.toLowerCase().includes(filterText.value.toLowerCase())
      )
    );

    const clearFilter = () => {
      filterText.value = '';
    };

    return { filterText, filteredItems, clearFilter };
  },
});
</script>

<style scoped lang="css">
.filterable-list {
  width: 100%;
}

.filter-input {
  width: 100%;
  padding: var(--input-padding, 10px);
  margin-bottom: var(--input-margin-bottom, 10px);
  border: var(--input-border, 1px solid #ccc);
  border-radius: var(--input-border-radius, 4px);
}

.clear-button {
  margin-bottom: var(--button-margin-bottom, 10px);
  padding: var(--button-padding, 10px);
  border: none;
  background-color: var(--button-background-color, #f0f0f0);
  cursor: pointer;
}

.list-item {
  padding: var(--list-item-padding, 5px 0);
  border-bottom: var(--list-item-border-bottom, 1px solid #ddd);
}

.no-results {
  color: var(--no-results-color, #777);
}
</style>