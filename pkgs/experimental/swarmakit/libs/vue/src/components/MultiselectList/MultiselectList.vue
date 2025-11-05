<template>
  <div class="multiselect-list" role="listbox" aria-multiselectable="true">
    <ul class="item-list" role="list" aria-label="Selectable Items">
      <li
        v-for="(item) in items"
        :key="item.value"
        :class="['list-item', { selected: selectedItems.includes(item.value), disabled: item.disabled }]"
        @click="toggleItemSelection(item)"
        @mouseover="hoveredItem = item.value"
        @mouseleave="hoveredItem = null"
        :aria-selected="selectedItems.includes(item.value)"
        :aria-disabled="item.disabled"
      >
        {{ item.label }}
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Item {
  value: string;
  label: string;
  disabled?: boolean;
}

export default defineComponent({
  name: 'MultiselectList',
  props: {
    items: {
      type: Array as () => Item[],
      required: true,
    },
  },
  setup() {
    const selectedItems = ref<string[]>([]);
    const hoveredItem = ref<string | null>(null);

    const toggleItemSelection = (item: Item) => {
      if (item.disabled) return;
      const index = selectedItems.value.indexOf(item.value);
      if (index === -1) {
        selectedItems.value.push(item.value);
      } else {
        selectedItems.value.splice(index, 1);
      }
    };

    return { selectedItems, hoveredItem, toggleItemSelection };
  },
});
</script>

<style scoped lang="css">
.multiselect-list {
  width: 100%;
}

.item-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.list-item {
  padding: var(--list-item-padding, 8px);
  border-bottom: var(--list-item-border, 1px solid #ccc);
  cursor: pointer;
  transition: background-color 0.2s;
}

.list-item.selected {
  background-color: var(--selected-bg, #d1e7dd);
  color: var(--selected-color, #0f5132);
}

.list-item.disabled {
  background-color: var(--disabled-bg, #f8f9fa);
  color: var(--disabled-color, #6c757d);
  cursor: not-allowed;
}

.list-item:hover:not(.disabled) {
  background-color: var(--hover-bg, #e2e6ea);
}
</style>