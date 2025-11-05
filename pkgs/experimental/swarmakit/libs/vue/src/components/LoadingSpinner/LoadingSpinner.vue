<template>
  <div v-if="active" class="spinner" role="status" aria-live="polite" aria-label="Loading">
    <span class="visually-hidden">Loading...</span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LoadingSpinner',
  props: {
    active: {
      type: Boolean,
      required: true,
    },
  },
});
</script>

<style scoped lang="css">
.spinner {
  border: var(--spinner-border-width, 4px) solid var(--spinner-border-color, #f3f3f3);
  border-top: var(--spinner-border-width, 4px) solid var(--spinner-active-color, #3498db);
  border-radius: 50%;
  width: var(--spinner-size, 40px);
  height: var(--spinner-size, 40px);
  animation: spin 2s linear infinite;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  border: 0;
  padding: 0;
  clip: rect(0, 0, 0, 0);
  overflow: hidden;
  white-space: nowrap;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>