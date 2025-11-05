<template>
  <div class="undo-redo-buttons">
    <button :disabled="!canUndo" @click="undo" aria-label="Undo" :class="{ active: canUndo }">Undo</button>
    <button :disabled="!canRedo" @click="redo" aria-label="Redo" :class="{ active: canRedo }">Redo</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'UndoRedoButtons',
  setup() {
    const canUndo = ref(false);
    const canRedo = ref(false);

    const undo = () => {
      if (canUndo.value) {
        // Perform undo action
        canRedo.value = true;
        canUndo.value = false; // Update based on actual action history
      }
    };

    const redo = () => {
      if (canRedo.value) {
        // Perform redo action
        canUndo.value = true;
        canRedo.value = false; // Update based on actual action history
      }
    };

    return {
      canUndo,
      canRedo,
      undo,
      redo,
    };
  },
});
</script>

<style scoped>
.undo-redo-buttons {
  display: flex;
  gap: 10px;
}

button {
  cursor: pointer;
  padding: 8px 16px;
  border: none;
  background-color: var(--button-bg);
  color: var(--button-text-color);
  transition: background-color 0.3s;
}

button:disabled {
  background-color: var(--button-disabled-bg);
  cursor: not-allowed;
}

button.active {
  background-color: var(--button-active-bg);
}
</style>