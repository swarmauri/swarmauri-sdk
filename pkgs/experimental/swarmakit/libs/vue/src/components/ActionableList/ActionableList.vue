<template>
  <ul class="actionable-list" role="list">
    <li
      v-for="(item, index) in items"
      :key="index"
      class="actionable-list-item"
      :class="{ hovered: hoveredIndex === index, disabled: item.disabled, loading: item.loading }"
      @mouseenter="hoveredIndex = index"
      @mouseleave="hoveredIndex = null"
    >
      <span>{{ item.label }}</span>
      <button
        v-if="!item.disabled && !item.loading"
        @click="triggerAction(index)"
        :disabled="item.disabled"
        :aria-disabled="item.disabled ? 'true' : 'false'"
        class="action-button"
      >
        {{ item.actionLabel }}
      </button>
      <span v-if="item.loading" class="loading-spinner">Loading...</span>
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface ListItem {
  label: string;
  actionLabel: string;
  disabled?: boolean;
  loading?: boolean;
}

export default defineComponent({
  name: 'ActionableList',
  props: {
    items: {
      type: Array as () => ListItem[],
      required: true,
    },
  },
  setup() {
    const hoveredIndex = ref<number | null>(null);

    const triggerAction = (index: number) => {
      console.log(`Action triggered for item at index: ${index}`);
    };

    return { hoveredIndex, triggerAction };
  },
});
</script>

<style scoped lang="css">
.actionable-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.actionable-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--actionable-list-item-padding, 10px);
  border-bottom: var(--actionable-list-item-border-bottom, 1px solid #eee);
  transition: background-color 0.3s ease;
}

.actionable-list-item.hovered {
  background-color: var(--actionable-list-item-hover-bg, #f5f5f5);
}

.actionable-list-item.disabled {
  opacity: 0.6;
}

.actionable-list-item.loading {
  background-color: var(--actionable-list-item-loading-bg, #f0f0f0);
}

.action-button {
  background-color: var(--action-button-bg, #007bff);
  color: var(--action-button-color, #fff);
  border: none;
  padding: var(--action-button-padding, 5px 10px);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: var(--action-button-hover-bg, #0056b3);
}

.loading-spinner {
  font-style: italic;
  color: var(--loading-spinner-color, #999);
}
</style>