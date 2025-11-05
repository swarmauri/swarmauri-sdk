<template>
  <div class="color-picker" :class="{ active: isActive }">
    <button @click="toggleActive" :aria-pressed="isActive" class="color-button">Color Picker</button>
    <div v-if="isActive" class="color-settings">
      <input type="color" v-model="selectedColor" aria-label="Select Color">

      <label for="hexCode">Hex Code</label>
      <input id="hexCode" type="text" v-model="hexCode" @input="updateColorFromHex" aria-live="polite">

      <label for="brightness">Brightness</label>
      <input id="brightness" type="range" v-model="brightness" min="0" max="100" aria-valuemin="0" aria-valuemax="100" aria-valuenow="brightness">

      <label for="opacity">Opacity</label>
      <input id="opacity" type="range" v-model="opacity" min="0" max="1" step="0.01" aria-valuemin="0" aria-valuemax="1" aria-valuenow="opacity">

      <div class="color-history" aria-label="Color History">
        <span v-for="color in colorHistory" :key="color" :style="{ backgroundColor: color }" class="color-swatch" @click="selectColorFromHistory(color)"></span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'ColorPicker',
  setup() {
    const isActive = ref(false);
    const selectedColor = ref('#000000');
    const hexCode = ref(selectedColor.value);
    const brightness = ref(50);
    const opacity = ref(1);
    const colorHistory = ref<string[]>([]);

    const toggleActive = () => {
      isActive.value = !isActive.value;
    };

    const updateColorFromHex = () => {
      if (/^#[0-9A-F]{6}$/i.test(hexCode.value)) {
        selectedColor.value = hexCode.value;
        addToHistory(hexCode.value);
      }
    };

    const addToHistory = (color: string) => {
      if (!colorHistory.value.includes(color)) {
        colorHistory.value.push(color);
        if (colorHistory.value.length > 5) colorHistory.value.shift();
      }
    };

    const selectColorFromHistory = (color: string) => {
      selectedColor.value = color;
      hexCode.value = color;
    };

    watch(selectedColor, (newValue) => {
      hexCode.value = newValue;
      addToHistory(newValue);
    });

    return {
      isActive,
      selectedColor,
      hexCode,
      brightness,
      opacity,
      colorHistory,
      toggleActive,
      updateColorFromHex,
      selectColorFromHistory,
    };
  },
});
</script>

<style scoped>
.color-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.color-picker.active .color-button {
  border: 2px solid var(--color-picker-active-border);
}

.color-settings {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.color-button {
  cursor: pointer;
}

.color-history {
  display: flex;
  gap: 5px;
}

.color-swatch {
  width: 20px;
  height: 20px;
  cursor: pointer;
}
</style>