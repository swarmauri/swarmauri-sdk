<template>
  <span :class="badgeClass" role="status" aria-live="polite">
    <span v-if="count > 99" class="overflow">99+</span>
    <span v-else>{{ count }}</span>
  </span>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'; // Removed the unused PropType import

export default defineComponent({
  name: 'BadgeWithCounts',
  props: {
    count: {
      type: Number,
      default: 0,
    },
  },
  setup(props) {
    const badgeClass = computed(() => `badge ${props.count > 0 ? 'active' : 'zero'}`);

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
  background-color: var(--badge-background, #e0e0e0);
  color: var(--badge-text, #606060);
}

.zero {
  background-color: var(--zero-background, #e0e0e0);
  color: var(--zero-text, #606060);
}

.active {
  background-color: var(--active-background, #007bff);
  color: var(--active-text, #ffffff);
}

.overflow {
  font-size: var(--overflow-font-size, 0.75rem);
  color: var(--overflow-text, #ff0000);
}
</style>
