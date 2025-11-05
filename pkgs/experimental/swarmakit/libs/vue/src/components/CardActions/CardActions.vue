<template>
  <div class="card-actions">
    <button
      v-for="(action, index) in actions"
      :key="index"
      :class="{ hovered: hoveredIndex === index, disabled: action.disabled }"
      :disabled="action.disabled"
      @mouseover="hoveredIndex = index"
      @mouseleave="hoveredIndex = -1"
      @click="action.onClick"
    >
      {{ action.label }}
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

type Action = {
  label: string;
  onClick: () => void;
  disabled?: boolean;
};

export default defineComponent({
  name: 'CardActions',
  props: {
    actions: {
      type: Array as () => Action[],
      required: true,
    },
  },
  setup() {
    const hoveredIndex = ref<number | null>(-1);
    return { hoveredIndex };
  },
});
</script>

<style scoped lang="css">
.card-actions {
  display: flex;
  gap: var(--spacing-md);
}

button {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius);
  background-color: var(--color-primary);
  color: var(--color-text-light);
  cursor: pointer;
  transition: background-color 0.3s;
}

button.hovered {
  background-color: var(--color-primary-hover);
}

button.disabled {
  background-color: var(--color-disabled);
  cursor: not-allowed;
}
</style>