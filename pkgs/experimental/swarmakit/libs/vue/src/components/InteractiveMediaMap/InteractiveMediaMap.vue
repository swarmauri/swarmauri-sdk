<template>
  <div class="interactive-media-map" role="application" aria-label="Interactive Media Map">
    <div class="map-container">
      <img :src="mapSrc" alt="Map" @load="loading = false" />
      <div
        v-for="(marker, index) in markers"
        :key="index"
        class="map-marker"
        :style="{ top: marker.y + '%', left: marker.x + '%' }"
        @click="selectMarker(index)"
        :aria-label="'Marker ' + (index + 1)"
        role="button"
      ></div>
    </div>
    <button @click="zoomIn" aria-label="Zoom in" class="zoom-btn">+</button>
    <button @click="zoomOut" aria-label="Zoom out" class="zoom-btn">-</button>
    <div v-if="selectedMarker !== null" class="marker-info">
      <p>{{ markers[selectedMarker].info }}</p>
      <button @click="deselectMarker" aria-label="Close marker info">Close</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'InteractiveMediaMap',
  props: {
    mapSrc: {
      type: String,
      required: true,
    },
    markers: {
      type: Array as () => Array<{ x: number; y: number; info: string }>,
      default: () => [],
    },
  },
  setup() {
    const selectedMarker = ref<number | null>(null);
    const loading = ref(true);

    const selectMarker = (index: number) => {
      selectedMarker.value = index;
    };

    const deselectMarker = () => {
      selectedMarker.value = null;
    };

    const zoomIn = () => {
      // Implement zoom in functionality
    };

    const zoomOut = () => {
      // Implement zoom out functionality
    };

    return {
      selectedMarker,
      loading,
      selectMarker,
      deselectMarker,
      zoomIn,
      zoomOut,
    };
  },
});
</script>

<style scoped lang="css">
.interactive-media-map {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--map-bg-color);
}

.map-container {
  position: relative;
  overflow: hidden;
}

.map-marker {
  position: absolute;
  width: 20px;
  height: 20px;
  background-color: var(--marker-bg-color);
  border-radius: 50%;
  cursor: pointer;
  transform: translate(-50%, -50%);
  transition: background-color 0.3s ease;
}

.map-marker:hover {
  background-color: var(--marker-hover-bg-color);
}

.zoom-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1.5rem;
  margin-left: 5px;
}

.marker-info {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--info-bg-color);
  color: var(--info-text-color);
  padding: 1rem;
  border-radius: 5px;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem;
  color: var(--loading-text-color);
}
</style>