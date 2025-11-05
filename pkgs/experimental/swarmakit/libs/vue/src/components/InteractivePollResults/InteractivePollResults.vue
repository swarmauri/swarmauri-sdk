<template>
  <div class="poll-results" role="region" aria-live="polite">
    <h2>{{ title }}</h2>
    <ul>
      <li v-for="option in options" :key="option.id" :aria-label="`${option.text}: ${option.percentage}%`">
        <span class="option-text">{{ option.text }}</span>
        <div class="progress-bar" :style="{ '--progress': `${option.percentage}%` }">
          <span class="percentage">{{ option.percentage }}%</span>
        </div>
      </li>
    </ul>
    <div v-if="state === 'completed'" class="poll-status">Poll Completed</div>
    <div v-if="state === 'closed'" class="poll-status">Poll Closed</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface PollOption {
  id: number;
  text: string;
  percentage: number;
}

export default defineComponent({
  name: 'InteractivePollResults',
  props: {
    title: {
      type: String,
      required: true,
    },
    options: {
      type: Array as PropType<PollOption[]>,
      required: true,
    },
    state: {
      type: String as PropType<'live' | 'completed' | 'closed'>,
      required: true,
    },
  },
});
</script>

<style scoped lang="css">
.poll-results {
  font-size: var(--poll-font-size, 16px);
  color: var(--poll-text-color, #000);
}

.option-text {
  margin-right: 10px;
}

.progress-bar {
  display: inline-block;
  width: calc(var(--progress) + 2px);
  height: var(--progress-bar-height, 20px);
  background-color: var(--progress-bar-color, #007bff);
  position: relative;
  overflow: hidden;
}

.percentage {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--percentage-text-color, #fff);
}

.poll-status {
  margin-top: 10px;
  font-weight: bold;
  color: var(--status-text-color, #ff0000);
}
</style>