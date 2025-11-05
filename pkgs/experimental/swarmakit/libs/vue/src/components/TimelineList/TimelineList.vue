<template>
  <ul class="timeline-list" role="list">
    <li
      v-for="(item, index) in items"
      :key="item.id"
      :class="{
        active: index === activeIndex,
        completed: item.completed,
        inactive: !item.completed && index !== activeIndex
      }"
      role="listitem"
    >
      <div class="timeline-content">
        <span class="timeline-label">{{ item.label }}</span>
      </div>
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface TimelineItem {
  id: number;
  label: string;
  completed?: boolean;
}

export default defineComponent({
  name: 'TimelineList',
  props: {
    items: {
      type: Array as PropType<TimelineItem[]>,
      required: true,
    },
    activeIndex: {
      type: Number,
      default: 0,
    },
  },
});
</script>

<style scoped lang="css">
.timeline-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.timeline-list li {
  padding: 10px;
  border-left: var(--timeline-border);
  position: relative;
  cursor: pointer;
}

.timeline-list li::before {
  content: '';
  position: absolute;
  top: 0;
  left: -6px;
  width: 12px;
  height: 12px;
  background-color: var(--timeline-dot-bg);
  border-radius: 50%;
  transition: background-color 0.3s;
}

.timeline-list li.active::before {
  background-color: var(--timeline-active-dot-bg);
}

.timeline-list li.completed::before {
  background-color: var(--timeline-completed-dot-bg);
}

.timeline-list li:hover::before {
  background-color: var(--timeline-hover-dot-bg);
}

.timeline-list li.inactive::before {
  background-color: var(--timeline-inactive-dot-bg);
}
</style>