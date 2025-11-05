<template>
  <div class="status-dots" role="status" :aria-label="ariaLabel">
    <span :class="['dot', status]" :style="{ backgroundColor: statusColor }"></span>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';

export default defineComponent({
  name: 'StatusDots',
  props: {
    status: {
      type: String,
      default: 'offline',
      validator: (value: string) => ['online', 'offline', 'busy', 'idle'].includes(value),
    },
  },
  setup(props) {
    const statusColor = computed(() => {
      switch (props.status) {
        case 'online':
          return 'var(--status-online-color, #4caf50)';
        case 'offline':
          return 'var(--status-offline-color, #f44336)';
        case 'busy':
          return 'var(--status-busy-color, #ff9800)';
        case 'idle':
          return 'var(--status-idle-color, #ffeb3b)';
        default:
          return 'var(--status-offline-color, #f44336)';
      }
    });

    const ariaLabel = computed(() => {
      switch (props.status) {
        case 'online':
          return 'User is online';
        case 'offline':
          return 'User is offline';
        case 'busy':
          return 'User is busy';
        case 'idle':
          return 'User is idle';
        default:
          return 'User status unknown';
      }
    });

    return {
      statusColor,
      ariaLabel,
    };
  },
});
</script>

<style scoped lang="css">
.status-dots {
  display: inline-flex;
  align-items: center;
}

.dot {
  width: var(--status-dot-size, 12px);
  height: var(--status-dot-size, 12px);
  border-radius: 50%;
  transition: background-color 0.3s;
}
</style>