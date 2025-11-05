<template>
  <div class="chip-container" role="list">
    <div
      v-for="(chip, index) in chips"
      :key="index"
      class="chip"
      :class="{ selectable, removable }"
      @click="toggleSelect(index)"
      role="listitem"
      tabindex="0"
      :aria-pressed="chip.selected"
    >
      <span>{{ chip.label }}</span>
      <button
        v-if="removable"
        class="remove-button"
        aria-label="Remove chip"
        @click.stop="removeChip(index)"
      >
        &times;
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Chip {
  label: string;
  selected: boolean;
}

export default defineComponent({
  name: 'Chips',
  props: {
    selectable: {
      type: Boolean,
      default: false,
    },
    removable: {
      type: Boolean,
      default: false,
    },
    grouped: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const chips = ref<Chip[]>([
      { label: 'Chip 1', selected: false },
      { label: 'Chip 2', selected: false },
      { label: 'Chip 3', selected: false },
    ]);

    const toggleSelect = (index: number) => {
      chips.value[index].selected = !chips.value[index].selected;
    };

    const removeChip = (index: number) => {
      chips.value.splice(index, 1);
    };

    return { chips, toggleSelect, removeChip };
  },
});
</script>

<style scoped lang="css">
.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--chip-gap, 8px);
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: var(--chip-padding, 8px 12px);
  border-radius: var(--chip-radius, 16px);
  background-color: var(--chip-bg-color, #e0e0e0);
  color: var(--chip-text-color, #333);
  cursor: pointer;
  transition: background-color 0.3s;
}

.chip.selectable:hover {
  background-color: var(--chip-hover-bg-color, #d0d0d0);
}

.chip[aria-pressed="true"] {
  background-color: var(--chip-selected-bg-color, #b0b0b0);
}

.remove-button {
  margin-left: var(--chip-remove-margin, 8px);
  background: none;
  border: none;
  color: var(--chip-remove-color, #666);
  cursor: pointer;
}

.remove-button:hover {
  color: var(--chip-remove-hover-color, #333);
}
</style>