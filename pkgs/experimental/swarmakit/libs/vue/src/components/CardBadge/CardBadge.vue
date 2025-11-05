<template>
  <span :class="['card-badge', statusClass]" @mouseover="isHovered = true" @mouseleave="isHovered = false">
    {{ content }}
  </span>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from 'vue';

export default defineComponent({
  name: 'CardBadge',
  props: {
    content: {
      type: [String, Number],
      required: true,
    },
    status: {
      type: String as () => 'default' | 'active' | 'inactive',
      default: 'default',
    },
  },
  setup(props) {
    const isHovered = ref(false);
    const statusClass = computed(() => {
      return {
        default: 'badge-default',
        active: 'badge-active',
        inactive: 'badge-inactive',
        hovered: isHovered.value ? 'badge-hovered' : '',
      }[props.status];
    });

    return { statusClass, isHovered };
  },
});
</script>

<style scoped lang="css">
.card-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
  transition: background-color 0.3s;
}

.badge-default {
  background-color: var(--color-gray-light);
  color: var(--color-text-dark);
}

.badge-active {
  background-color: var(--color-success);
  color: var(--color-text-light);
}

.badge-inactive {
  background-color: var(--color-warning);
  color: var(--color-text-dark);
}

.badge-hovered {
  background-color: var(--color-primary-hover);
}
</style>