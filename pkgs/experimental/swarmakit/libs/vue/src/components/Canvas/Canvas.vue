<template>
  <div class="canvas-container" @mousedown="startDrawing" @mouseup="stopDrawing" @mousemove="draw" @touchstart="startDrawing" @touchend="stopDrawing" @touchmove="draw">
    <canvas ref="canvas" :width="canvasWidth" :height="canvasHeight" aria-label="Interactive Drawing Canvas"></canvas>
    <div class="controls">
      <button @click="clearCanvas" aria-label="Clear Canvas">Clear</button>
      <label for="brushSize">Brush Size</label>
      <input id="brushSize" type="range" v-model="brushSize" min="1" max="10" aria-valuemin="1" aria-valuemax="10" aria-valuenow="brushSize">
      <label for="brushColor">Brush Color</label>
      <input id="brushColor" type="color" v-model="brushColor">
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';

export default defineComponent({
  name: 'Canvas',
  setup() {
    const canvas = ref<HTMLCanvasElement | null>(null);
    const canvasWidth = ref(window.innerWidth);
    const canvasHeight = ref(window.innerHeight);
    const brushSize = ref(5);
    const brushColor = ref('#000000');
    let isDrawing = false;

    const startDrawing = (event: MouseEvent | TouchEvent) => {
      isDrawing = true;
      draw(event);
    };

    const stopDrawing = () => {
      isDrawing = false;
      const ctx = canvas.value?.getContext('2d');
      if (ctx) {
        ctx.beginPath();
      }
    };

    const draw = (event: MouseEvent | TouchEvent) => {
      if (!isDrawing || !canvas.value) return;
      const ctx = canvas.value.getContext('2d');
      if (!ctx) return;
      
      const rect = canvas.value.getBoundingClientRect();
      const x = 'touches' in event ? event.touches[0].clientX - rect.left : event.clientX - rect.left;
      const y = 'touches' in event ? event.touches[0].clientY - rect.top : event.clientY - rect.top;
      
      ctx.lineWidth = brushSize.value;
      ctx.lineCap = 'round';
      ctx.strokeStyle = brushColor.value;
      ctx.lineTo(x, y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x, y);
    };

    const clearCanvas = () => {
      const ctx = canvas.value?.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value);
      }
    };

    onMounted(() => {
      window.addEventListener('resize', () => {
        canvasWidth.value = window.innerWidth;
        canvasHeight.value = window.innerHeight;
      });
    });

    return {
      canvas,
      canvasWidth,
      canvasHeight,
      brushSize,
      brushColor,
      startDrawing,
      stopDrawing,
      draw,
      clearCanvas
    };
  }
});
</script>

<style scoped>
.canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
}

canvas {
  width: 100%;
  height: 100%;
  border: 1px solid var(--canvas-border-color);
}

.controls {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  gap: 10px;
}
</style>