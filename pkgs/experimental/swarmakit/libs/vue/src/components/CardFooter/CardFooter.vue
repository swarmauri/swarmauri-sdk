<template>
  <footer class="card-footer" :style="{ justifyContent: alignment }">
    <slot></slot>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'CardFooter',
  props: {
    alignment: {
      type: String as () => 'flex-start' | 'center' | 'flex-end',
      default: 'flex-start',
    },
  },
});
</script>

<style scoped lang="css">
.card-footer {
  padding: var(--spacing-md);
  background-color: var(--color-background);
  display: flex;
  gap: var(--spacing-sm);
  border-top: 1px solid var(--color-border);
}

.card-footer button,
.card-footer a {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius);
  text-decoration: none;
  cursor: pointer;
}

.card-footer button:hover,
.card-footer a:hover {
  background-color: var(--color-primary-hover);
}
</style>