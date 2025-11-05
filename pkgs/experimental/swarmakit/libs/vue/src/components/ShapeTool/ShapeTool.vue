<template>
  <div class="shape-tool" :class="{ active: isActive }">
    <button @click="toggleActive" :aria-pressed="isActive" class="shape-button">Shape Tool</button>
    <div v-if="isActive" class="shape-settings">
      <label for="shape">Shape</label>
      <select id="shape" v-model="selectedShape" aria-label="Select Shape">
        <option value="rectangle">Rectangle</option>
        <option value="circle">Circle</option>
        <option value="ellipse">Ellipse</option>
        <option value="line">Line</option>
      </select>

      <label for="size">Size</label>
      <input id="size" type="range" v-model="size" min="1" max="100" aria-valuemin="1" aria-valuemax="100" aria-valuenow="size">

      <label for="fillColor">Fill Color</label>
      <input id="fillColor" type="color" v-model="fillColor" aria-label="Fill Color">

      <label for="borderColor">Border Color</label>
      <input id="borderColor" type="color" v-model="borderColor" aria-label="Border Color">

      <label for="thickness">Thickness</label>
      <input id="thickness" type="range" v-model="thickness" min="1" max="10" aria-valuemin="1" aria-valuemax="10" aria-valuenow="thickness">
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ShapeTool',
  setup() {
    const isActive = ref(false);
    const selectedShape = ref('rectangle');
    const size = ref(50);
    const fillColor = ref('#000000');
    const borderColor = ref('#ffffff');
    const thickness = ref(1);

    const toggleActive = () => {
      isActive.value = !isActive.value;
    };

    return {
      isActive,
      selectedShape,
      size,
      fillColor,
      borderColor,
      thickness,
      toggleActive,
    };
  },
});
</script>

<style scoped>
.shape-tool {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shape-tool.active .shape-button {
  border: 2px solid var(--shape-tool-active-border);
}

.shape-settings {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.shape-button {
  cursor: pointer;
}
</style>