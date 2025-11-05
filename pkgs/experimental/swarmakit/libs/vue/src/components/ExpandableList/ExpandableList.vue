<template>
  <div class="expandable-list" role="list" aria-label="Expandable list">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="list-item"
      :aria-expanded="selectedItem === index"
      @click="toggleItem(index)"
      @mouseover="hoverItem(index)"
      @mouseleave="hoverItem(null)"
    >
      <div class="item-header">
        {{ item.title }}
      </div>
      <div v-if="selectedItem === index" class="item-content">
        {{ item.content }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ExpandableList',
  props: {
    items: {
      type: Array as () => Array<{ title: string; content: string }>,
      required: true,
    },
  },
  setup() {
    const selectedItem = ref<number | null>(null);
    const hoveredItem = ref<number | null>(null);

    const toggleItem = (index: number) => {
      selectedItem.value = selectedItem.value === index ? null : index;
    };

    const hoverItem = (index: number | null) => {
      hoveredItem.value = index;
    };

    return { selectedItem, hoveredItem, toggleItem, hoverItem };
  },
});
</script>

<style scoped lang="css">
.expandable-list {
  list-style: none;
  padding: 0;
}

.list-item {
  margin: var(--item-margin, 5px 0);
  padding: var(--item-padding, 10px);
  border: var(--item-border, 1px solid #ccc);
  cursor: pointer;
}

.list-item:hover {
  background-color: var(--hover-background-color, #f0f0f0);
}

.item-header {
  font-weight: var(--item-header-font-weight, bold);
}

.item-content {
  margin-top: var(--item-content-margin-top, 5px);
}
</style>