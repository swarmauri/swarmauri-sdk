<template>
  <div class="loading-bars" role="progressbar" aria-valuemin="0" :aria-valuenow="currentStep" :aria-valuemax="steps.length">
    <ul>
      <li v-for="(step, index) in steps" :key="step.id" :class="getStepClass(index)">
        <div class="step-bar" :style="{ '--progress': `${getProgress(index)}%` }"></div>
        <span class="step-label">{{ step.label }}</span>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface Step {
  id: number;
  label: string;
}

export default defineComponent({
  name: 'LoadingBarsWithSteps',
  props: {
    steps: {
      type: Array as PropType<Step[]>,
      required: true,
    },
    currentStep: {
      type: Number,
      required: true,
    },
  },
  methods: {
    getStepClass(index: number) {
      if (index < this.currentStep) return 'completed';
      if (index === this.currentStep) return 'active';
      return 'inactive';
    },
    getProgress(index: number) {
      if (index < this.currentStep) return 100;
      if (index === this.currentStep) return 50;
      return 0;
    },
  },
});
</script>

<style scoped lang="css">
.loading-bars {
  display: flex;
  font-size: var(--loading-font-size, 14px);
}

ul {
  display: flex;
  list-style: none;
  padding: 0;
}

li {
  flex: 1;
  margin-right: 10px;
  position: relative;
}

.step-bar {
  height: var(--step-bar-height, 5px);
  background-color: var(--step-bar-bg, #ccc);
  width: var(--progress);
  transition: width 0.3s ease;
}

.active .step-bar {
  background-color: var(--active-step-bar-color, #007bff);
}

.completed .step-bar {
  background-color: var(--completed-step-bar-color, #28a745);
}

.step-label {
  margin-top: 5px;
  text-align: center;
  display: block;
}
</style>