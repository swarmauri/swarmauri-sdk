<template>
  <div
    class="notification"
    :class="notificationType"
    role="alert"
    v-if="!localIsDismissed"
  >
    <span>{{ message }}</span>
    <button class="close-btn" @click="dismiss" aria-label="Dismiss notification">✖</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType } from 'vue';

export default defineComponent({
  name: 'Notification',
  props: {
    notificationType: {
      type: String as PropType<'success' | 'error' | 'warning'>,
      default: 'success',
    },
    message: {
      type: String,
      default: 'This is a notification message.',
    },
    isDismissed: {
      type: Boolean,
      default: false,
    }
  },
  setup(props) {
    const localIsDismissed = ref(props.isDismissed);

    const dismiss = () => {
      localIsDismissed.value = true;
    };

    return { localIsDismissed, dismiss };
  },
});
</script>

<style scoped lang="css">
.notification {
  padding: 15px;
  border-radius: 5px;
  margin: 10px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification.success {
  background-color: var(--notification-success-bg, #d4edda);
  color: var(--notification-success-color, #155724);
}

.notification.error {
  background-color: var(--notification-error-bg, #f8d7da);
  color: var(--notification-error-color, #721c24);
}

.notification.warning {
  background-color: var(--notification-warning-bg, #fff3cd);
  color: var(--notification-warning-color, #856404);
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
}
</style>