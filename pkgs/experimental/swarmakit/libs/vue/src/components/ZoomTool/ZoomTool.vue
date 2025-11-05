<template>
  <div class="zoom-tool">
    <div class="zoom-controls">
      <button @click="zoomIn" aria-label="Zoom In">+</button>
      <span class="zoom-level">{{ zoomLevel }}%</span>
      <button @click="zoomOut" aria-label="Zoom Out">-</button>
    </div>
    <button @click="fitToScreen" aria-label="Fit to Screen">Fit to Screen</button>
    <button @click="resetZoom" aria-label="Reset Zoom">Reset</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ZoomTool',
  setup() {
    const zoomLevel = ref(100);

    const zoomIn = () => {
      if (zoomLevel.value < 500) zoomLevel.value += 10;
    };

    const zoomOut = () => {
      if (zoomLevel.value > 10) zoomLevel.value -= 10;
    };

    const fitToScreen = () => {
      zoomLevel.value = 100;
    };

    const resetZoom = () => {
      zoomLevel.value = 100;
    };

    return {
      zoomLevel,
      zoomIn,
      zoomOut,
      fitToScreen,
      resetZoom,
    };
  },
});
</script>

<style scoped>
.zoom-tool {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.zoom-controls {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

button {
  cursor: pointer;
  padding: 8px 16px;
  border: none;
  background-color: var(--button-bg);
  color: var(--button-text-color);
  transition: background-color 0.3s;
}

.zoom-level {
  margin: 0 10px;
  font-weight: bold;
  color: var(--zoom-text-color);
}
</style>