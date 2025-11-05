<template>
  <div class="ruler-and-guides">
    <div class="ruler" ref="horizontalRuler" aria-label="Horizontal Ruler"></div>
    <div class="ruler" ref="verticalRuler" aria-label="Vertical Ruler"></div>
    <div class="guides">
      <div
        v-for="(guide, index) in guides"
        :key="index"
        :style="{ left: guide.x + 'px', top: guide.y + 'px' }"
        class="guide"
        aria-label="Guide"
        @mousedown="startMovingGuide(index)"
      ></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted } from 'vue';

export default defineComponent({
  name: 'RulerAndGuides',
  setup() {
    const zoomLevel = ref(100);
    const guides = reactive<{ x: number; y: number }[]>([]);

    const startMovingGuide = (index: number) => {
      // Logic to start moving guide
      console.log(index)
      
    };

    const addGuide = (x: number, y: number) => {
      guides.push({ x, y });
    };

    const removeGuide = (index: number) => {
      guides.splice(index, 1);
    };

    onMounted(() => {
      // Initial setup or event listeners
    });

    return {
      zoomLevel,
      guides,
      startMovingGuide,
      addGuide,
      removeGuide,
    };
  },
});
</script>

<style scoped>
.ruler-and-guides {
  position: relative;
  width: 100%;
  height: 100%;
}

.ruler {
  position: absolute;
  background-color: var(--ruler-bg);
}

.guides {
  position: relative;
  width: 100%;
  height: 100%;
}

.guide {
  position: absolute;
  width: 1px;
  height: 100%;
  background-color: var(--guide-color);
  cursor: pointer;
}
</style>