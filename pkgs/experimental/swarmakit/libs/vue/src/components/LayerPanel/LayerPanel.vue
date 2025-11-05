<template>
  <div class="layer-panel">
    <h2>Layers</h2>
    <ul>
      <li v-for="(layer, index) in layers" :key="layer.id" :class="{ active: index === activeLayerIndex }">
        <input type="text" v-model="layer.name" @blur="renameLayer(index, layer.name)" aria-label="Layer Name">
        <input type="range" v-model="layer.opacity" min="0" max="1" step="0.01" aria-label="Layer Opacity">
        <button @click="toggleVisibility(index)" aria-label="Toggle Visibility">{{ layer.visible ? 'Hide' : 'Show' }}</button>
        <button @click="removeLayer(index)" aria-label="Remove Layer">Remove</button>
      </li>
    </ul>
    <button @click="addLayer" aria-label="Add Layer">Add Layer</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Layer {
  id: number;
  name: string;
  opacity: number;
  visible: boolean;
}

export default defineComponent({
  name: 'LayerPanel',
  setup() {
    const layers = ref<Layer[]>([
      { id: 1, name: 'Layer 1', opacity: 1, visible: true },
    ]);
    const activeLayerIndex = ref(0);

    const addLayer = () => {
      layers.value.push({
        id: Date.now(),
        name: `Layer ${layers.value.length + 1}`,
        opacity: 1,
        visible: true,
      });
    };

    const removeLayer = (index: number) => {
      if (layers.value.length > 1) {
        layers.value.splice(index, 1);
        if (activeLayerIndex.value >= layers.value.length) {
          activeLayerIndex.value = layers.value.length - 1;
        }
      }
    };

    const renameLayer = (index: number, newName: string) => {
      layers.value[index].name = newName;
    };

    const toggleVisibility = (index: number) => {
      layers.value[index].visible = !layers.value[index].visible;
    };

    return {
      layers,
      activeLayerIndex,
      addLayer,
      removeLayer,
      renameLayer,
      toggleVisibility,
    };
  },
});
</script>

<style scoped>
.layer-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.active {
  border: 2px solid var(--layer-panel-active-border);
}

ul {
  list-style: none;
  padding: 0;
}

li {
  display: flex;
  align-items: center;
  gap: 5px;
}

button {
  cursor: pointer;
}
</style>