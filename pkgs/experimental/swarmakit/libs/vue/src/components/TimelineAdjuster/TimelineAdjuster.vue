<template>
  <div class="timeline-adjuster" role="region" aria-label="Timeline Adjuster">
    <div class="zoom-controls">
      <button @click="zoomIn" aria-label="Zoom in">+</button>
      <button @click="zoomOut" aria-label="Zoom out">-</button>
    </div>
    
    <div class="timeline-container" @mousedown="startDrag" @mouseup="stopDrag" @mouseleave="stopDrag" @mousemove="drag">
      <div class="timeline" :style="{ transform: `translateX(${timelineOffset}px)` }">
        <div v-for="hour in hours" :key="hour" class="time-slot">{{ hour }}:00</div>
      </div>
    </div>

    <div class="navigation">
      <button @click="goToToday" aria-label="Go to today">Today</button>
      <button @click="goToNextDay" aria-label="Go to next day">Next Day</button>
      <button @click="goToPreviousDay" aria-label="Go to previous day">Previous Day</button>
    </div>

    <div v-if="feedbackMessage" class="feedback">{{ feedbackMessage }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'TimelineAdjuster',
  props:{
    feedbackMessage: {
      type:String,
      default: '',
    }
  },
  setup(props) {
    const zoomLevel = ref(1);
    const timelineOffset = ref(0);
    const feedbackMessage = ref(props.feedbackMessage);
    const isDragging = ref(false);
    const startDragX = ref(0);
    const hours = Array.from({ length: 24 }, (_, i) => i);

    const zoomIn = () => {
      if (zoomLevel.value < 3) {
        zoomLevel.value += 1;
        feedbackMessage.value = `Zoom level: ${zoomLevel.value}`;
      }
    };

    const zoomOut = () => {
      if (zoomLevel.value > 1) {
        zoomLevel.value -= 1;
        feedbackMessage.value = `Zoom level: ${zoomLevel.value}`;
      }
    };

    const startDrag = (event: MouseEvent) => {
      isDragging.value = true;
      startDragX.value = event.clientX;
    };

    const stopDrag = () => {
      isDragging.value = false;
    };

    const drag = (event: MouseEvent) => {
      if (isDragging.value) {
        timelineOffset.value += event.clientX - startDragX.value;
        startDragX.value = event.clientX;
      }
    };

    const goToToday = () => {
      feedbackMessage.value = 'Navigated to today';
    };

    const goToNextDay = () => {
      feedbackMessage.value = 'Navigated to next day';
    };

    const goToPreviousDay = () => {
      feedbackMessage.value = 'Navigated to previous day';
    };

    return {
      zoomLevel,
      timelineOffset,
      feedbackMessage,
      zoomIn,
      zoomOut,
      startDrag,
      stopDrag,
      drag,
      goToToday,
      goToNextDay,
      goToPreviousDay,
      hours
    };
  }
});
</script>

<style scoped>
@import './TimelineAdjuster.css';
</style>