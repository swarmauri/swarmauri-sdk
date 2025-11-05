<template>
  <span :class="badgeClass" role="status" aria-live="polite">
    <slot></slot>
  </span>
</template>

<script lang="ts">
import { defineComponent, PropType, computed } from 'vue';

export default defineComponent({
  name: 'Badge',
  props: {
    type: {
      type: String as PropType<'default' | 'notification' | 'status-indicator'>,
      default: 'default',
    },
  },
  setup(props) {
    const badgeClass = computed(() => `badge ${props.type}`);

    return { badgeClass };
  },
});
</script>

<style scoped lang="css">
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25em 0.5em;
  border-radius: var(--badge-border-radius, 0.25em);
  font-size: var(--badge-font-size, 0.875rem);
  font-weight: var(--badge-font-weight, 600);
}

.default {
  background-color: var(--default-background, #e0e0e0);
  color: var(--default-text, #606060);
}

.notification {
  background-color: var(--notification-background, #007bff);
  color: var(--notification-text, #ffffff);
}

.status-indicator {
  background-color: var(--status-background, #28a745);
  color: var(--status-text, #ffffff);
}
</style>