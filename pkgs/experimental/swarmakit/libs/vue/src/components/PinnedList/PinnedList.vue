<template>
  <ul class="pinned-list">
    <li
      v-for="item in items"
      :key="item.id"
      :class="[
        'pinned-list-item',
        { pinned: item.pinned, selected: item.id === selectedItem, hover: item.id === hoveredItem }
      ]"
      @click="selectItem(item.id)"
      @mouseover="hoveredItem = item.id"
      @mouseleave="hoveredItem = null"
      :aria-selected="item.id === selectedItem ? 'true' : 'false'"
    >
      {{ item.label }}
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent, ref} from 'vue';

interface ListItem {
  id: number;
  label: string;
  pinned: boolean;
}

export default defineComponent({
  name: 'PinnedList',
  props: {
    items: {
      type: Array as () => ListItem[],
      required: true,
    },
    selectedItem: {
      type: Number,
      required: true,
    },
  },
  setup(_, { emit }) {
    const hoveredItem = ref<number | null>(null);

    const selectItem = (id: number) => {
      emit('update:selectedItem', id);
    };

    return { hoveredItem, selectItem };
  },
});
</script>

<style scoped lang="css">
.pinned-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.pinned-list-item {
  padding: var(--list-item-padding, 10px 15px);
  margin: 4px 0;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: var(--list-border-radius, 4px);
}

.pinned-list-item.pinned {
  background-color: var(--pinned-bg, #ffc107);
}

.pinned-list-item.selected {
  background-color: var(--selected-bg, #007bff);
  color: var(--selected-color, #fff);
}

.pinned-list-item.hover:not(.selected) {
  background-color: var(--hover-bg, #e9ecef);
}
</style>