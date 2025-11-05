<template>
  <div class="grouped-list">
    <div
      v-for="(group, groupIndex) in groups"
      :key="groupIndex"
      class="group"
    >
      <div class="group-header" @click="toggleGroup(groupIndex)">
        {{ group.name }}
      </div>
      <ul v-show="expandedGroups[groupIndex]" class="group-items" role="list" aria-label="Group items">
        <li
          v-for="(item, itemIndex) in group.items"
          :key="itemIndex"
          :class="['list-item', { 'selected': selectedItem === item }]"
          @click="selectItem(item)"
          @mouseover="hoveredItem = item"
          @mouseleave="hoveredItem = null"
          :aria-selected="selectedItem === item"
          role="option"
        >
          {{ item }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Group {
  name: string;
  items: string[];
}

export default defineComponent({
  name: 'GroupedList',
  props: {
    groups: {
      type: Array as () => Group[],
      required: true,
    },
  },
  setup() {
    const expandedGroups = ref<boolean[]>([]);
    const selectedItem = ref<string | null>(null);
    const hoveredItem = ref<string | null>(null);

    const toggleGroup = (index: number) => {
      expandedGroups.value[index] = !expandedGroups.value[index];
    };

    const selectItem = (item: string) => {
      selectedItem.value = item;
    };

    return { expandedGroups, selectedItem, hoveredItem, toggleGroup, selectItem };
  },
});
</script>

<style scoped lang="css">
.grouped-list {
  width: 100%;
}

.group {
  margin-bottom: var(--group-margin-bottom, 20px);
}

.group-header {
  cursor: pointer;
  background-color: var(--group-header-bg, #f5f5f5);
  padding: var(--group-header-padding, 10px);
  border: var(--group-header-border, 1px solid #ccc);
}

.group-items {
  list-style-type: none;
  padding: 0;
}

.list-item {
  padding: var(--list-item-padding, 8px);
  cursor: pointer;
  background-color: var(--list-item-bg, #fff);
}

.list-item:hover {
  background-color: var(--list-item-hover-bg, #e0e0e0);
}

.list-item.selected {
  background-color: var(--list-item-selected-bg, #d0d0d0);
}
</style>