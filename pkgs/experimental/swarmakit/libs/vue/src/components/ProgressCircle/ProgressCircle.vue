<template>
  <div
    class="progress-circle"
    role="progressbar"
    :aria-valuenow="progress"
    aria-valuemin="0"
    aria-valuemax="100"
    :aria-label="`Progress: ${progress}%`"
    :status="status"
  >
    <svg viewBox="0 0 36 36" class="circular-chart">
      <path
        class="circle-bg"
        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
      />
      <path
        class="circle"
        :stroke-dasharray="`${progress}, 100`"
        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
      />
    </svg>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ProgressCircle',
  props: {
    progress: {
      type: Number,
      required: true,
      validator: (value: number) => value >= 0 && value <= 100,
    },
    status: {
      type: String,
      required: false,
      default: 'active',
      validator: (value: string) => ['complete', 'incomplete', 'paused', 'active'].includes(value),
    },
  },
});
</script>

<style scoped lang="css">
.progress-circle {
  width: var(--progress-circle-size, 100px);
  height: var(--progress-circle-size, 100px);
}

.circular-chart {
  max-width: 100%;
  max-height: 100%;
}

.circle-bg {
  fill: none;
  stroke: var(--progress-circle-bg-color, #e0e0e0);
  stroke-width: 3.8;
}

.circle {
  fill: none;
  stroke-width: 2.8;
  stroke-linecap: round;
  transition: stroke-dasharray 0.3s;
}

.progress-circle[aria-valuenow="100"] .circle {
  stroke: var(--progress-circle-complete-color, #76c7c0);
}

.progress-circle[aria-valuenow="0"] .circle {
  stroke: var(--progress-circle-incomplete-color, #ff6f61);
}

.progress-circle[status="paused"] .circle {
  stroke: var(--progress-circle-paused-color, #f9a825);
}

.progress-circle[status="active"] .circle {
  stroke: var(--progress-circle-active-color, #76c7c0);
}
</style>
