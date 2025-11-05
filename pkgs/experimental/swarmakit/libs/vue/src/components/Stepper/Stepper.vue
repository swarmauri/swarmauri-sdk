<template>
  <nav class="stepper" aria-label="Progress steps">
    <ol>
      <li
        v-for="(step, index) in steps"
        :key="index"
        :class="['step', step.status]"
        :aria-current="step.status === 'active' ? 'step' : undefined"
      >
        <span class="step-label">{{ step.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface Step {
  label: string;
  status: 'completed' | 'active' | 'disabled';
}

export default defineComponent({
  name: 'Stepper',
  props: {
    steps: {
      type: Array as () => Step[],
      required: true,
    },
  },
});
</script>

<style scoped lang="css">
.stepper {
  display: flex;
  justify-content: space-between;
  list-style: none;
  padding: 0;
}

.step {
  display: flex;
  align-items: center;
  padding: var(--step-padding, 8px 16px);
  transition: background-color 0.3s;
}

.step.completed {
  background-color: var(--step-completed-bg, #4caf50);
  color: var(--step-completed-color, #fff);
}

.step.active {
  background-color: var(--step-active-bg, #2196f3);
  color: var(--step-active-color, #fff);
}

.step.disabled {
  background-color: var(--step-disabled-bg, #e0e0e0);
  color: var(--step-disabled-color, #757575);
}

.step-label {
  margin-left: var(--step-label-margin, 8px);
}
</style>