<template>
  <div
    class="notification-bar"
    :class="type"
    role="alert"
    :aria-live="type === 'error' ? 'assertive' : 'polite'"
  >
    <span class="notification-message">{{ message }}</span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'SystemAlertGlobalNotificationBar',
  props: {
    type: {
      type: String,
      required: true,
      validator: (value: string) => ['success', 'error', 'warning', 'info'].includes(value),
    },
    message: {
      type: String,
      required: true,
    },
  },
});
</script>

<style scoped lang="css">
.notification-bar {
  padding: var(--notification-padding, 16px);
  border-radius: var(--notification-border-radius, 4px);
  margin: var(--notification-margin, 8px 0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-bar.success {
  background-color: var(--notification-success-bg, #d4edda);
  color: var(--notification-success-color, #155724);
}

.notification-bar.error {
  background-color: var(--notification-error-bg, #f8d7da);
  color: var(--notification-error-color, #721c24);
}

.notification-bar.warning {
  background-color: var(--notification-warning-bg, #fff3cd);
  color: var(--notification-warning-color, #856404);
}

.notification-bar.info {
  background-color: var(--notification-info-bg, #d1ecf1);
  color: var(--notification-info-color, #0c5460);
}

.notification-message {
  font-size: var(--notification-font-size, 14px);
}
</style>