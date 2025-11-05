<template>
  <div
    class="progress-bar-container"
    :class="{ disabled }"
    role="progressbar"
    :aria-valuenow="progress"
    aria-valuemin="0"
    aria-valuemax="100"
    :aria-label="`Progress: ${progress}%`"
  >
    <div class="progress-bar" :style="{ width: progress + '%' }"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ProgressBar',
  props: {
    progress: {
      type: Number,
      required: true,
      validator: (value: number) => value >= 0 && value <= 100,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.progress-bar-container {
  width: 100%;
  height: var(--progress-bar-height, 20px);
  background-color: var(--progress-bar-bg-color, #e0e0e0);
  border-radius: var(--progress-bar-radius, 10px);
  overflow: hidden;
  transition: background-color 0.3s;
}

.progress-bar {
  height: 100%;
  background-color: var(--progress-bar-color, #76c7c0);
  transition: width 0.3s;
}

.progress-bar-container:hover .progress-bar {
  background-color: var(--progress-bar-hover-color, #5baaa8);
}

.progress-bar-container.disabled {
  background-color: var(--progress-bar-disabled-bg-color, #c0c0c0);
}

.progress-bar-container.disabled .progress-bar {
  background-color: var(--progress-bar-disabled-color, #a0a0a0);
}
</style>