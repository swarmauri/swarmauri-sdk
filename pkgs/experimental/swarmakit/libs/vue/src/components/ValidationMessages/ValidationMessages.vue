<template>
  <div :class="['validation-message', type]" role="alert" aria-live="assertive">
    <slot />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ValidationMessages',
  props: {
    type: {
      type: String as () => 'success' | 'error' | 'warning',
      default: 'success',
      validator: (value: string) => ['success', 'error', 'warning'].includes(value),
    },
  },
});
</script>

<style scoped>
@import './ValidationMessages.css';
</style>