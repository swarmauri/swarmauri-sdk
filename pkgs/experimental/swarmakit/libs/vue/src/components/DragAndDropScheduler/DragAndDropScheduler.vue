<template>
  <div class="scheduler" role="application" aria-label="Drag and Drop Scheduler">
    <div class="time-slot" v-for="slot in timeSlots" :key="slot" aria-label="Time Slot">
      <div
        v-for="event in events"
        :key="event.id"
        :class="['event', { dragging: event.isDragging }]"
        :style="{ top: event.position + 'px', height: event.duration + 'px' }"
        draggable="true"
        @dragstart="onDragStart(event)"
        @dragend="onDragEnd(event)"
      >
        {{ event.title }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType, ref } from 'vue';

interface Event {
  id: number;
  title: string;
  position: number;
  duration: number;
  isDragging: boolean;
}

export default defineComponent({
  name: 'DragAndDropScheduler',
  props: {
    events: {
      type: Array as PropType<Event[]>,
      requried:true,
      default:[
        { id: 1, title: 'Default Meeting', position: 0, duration: 60, isDragging: false }
      ],
    }
  },
  setup() {
    const timeSlots = Array.from({ length: 24 }, (_, i) => i);
    const events = ref<Event[]>([
      { id: 1, title: 'Meeting', position: 0, duration: 60, isDragging: false },
      // More events...
    ]);

    const onDragStart = (event: Event) => {
      event.isDragging = true;
    };

    const onDragEnd = (event: Event) => {
      event.isDragging = false;
    };

    return {
      timeSlots,
      events,
      onDragStart,
      onDragEnd
    };
  }
});
</script>

<style scoped>
@import './DragAndDropScheduler.css';
</style>