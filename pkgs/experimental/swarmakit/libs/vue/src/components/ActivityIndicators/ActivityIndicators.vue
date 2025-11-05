<template>
  <div :class="['activity-indicator', type]" role="status" aria-live="polite">
    <span v-if="type === 'loading'" class="spinner"></span>
    <span v-else>{{ message }}</span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ActivityIndicators',
  props: {
    type: {
      type: String as () => 'loading' | 'success' | 'error',
      default: 'loading',
      validator: (value: string) => ['loading', 'success', 'error'].includes(value),
    },
    message: {
      type: String,
      default: 'Loading...',
    },
  },
});
</script>

<style scoped>
@import './ActivityIndicators.css';
</style>