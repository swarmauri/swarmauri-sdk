<template>
  <ol class="numbered-list" role="list" aria-label="Numbered Items">
    <li
      v-for="(item) in items"
      :key="item.value"
      :class="['list-item', { selected: selectedItem === item.value, disabled: item.disabled }]"
      @click="selectItem(item)"
      @mouseover="hoveredItem = item.value"
      @mouseleave="hoveredItem = null"
      :aria-disabled="item.disabled"
    >
      {{ item.label }}
    </li>
  </ol>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Item {
  value: string;
  label: string;
  disabled?: boolean;
}

export default defineComponent({
  name: 'NumberedList',
  props: {
    items: {
      type: Array as () => Item[],
      required: true,
    },
  },
  setup() {
    const selectedItem = ref<string | null>(null);
    const hoveredItem = ref<string | null>(null);

    const selectItem = (item: Item) => {
      if (item.disabled) return;
      selectedItem.value = item.value;
    };

    return { selectedItem, hoveredItem, selectItem };
  },
});
</script>

<style scoped lang="css">
.numbered-list {
  list-style-type: decimal;
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