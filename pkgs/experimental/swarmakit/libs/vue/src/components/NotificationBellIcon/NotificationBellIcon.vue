<template>
  <div class="notification-bell" role="button" aria-label="Notification Bell">
    <svg
      class="bell-icon"
      :class="{ 'has-notifications': hasNotifications, 'dismissed': dismissed }"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M12 2C10.34 2 9 3.34 9 5v1.07C6.83 6.57 5 8.64 5 11v5h14v-5c0-2.36-1.83-4.43-4-4.93V5c0-1.66-1.34-3-3-3zm-1 19c0 .55.45 1 1 1s1-.45 1-1h-2z"/>
    </svg>
    <span v-if="hasNotifications" class="notification-dot" aria-label="New Notifications"></span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'NotificationBellIcon',
  props: {
    hasNotifications: {
      type: Boolean,
      required: true,
    },
    dismissed: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.notification-bell {
  position: relative;
  width: var(--bell-icon-size, 24px);
  height: var(--bell-icon-size, 24px);
  cursor: pointer;
}

.bell-icon {
  fill: var(--bell-icon-color, #000);
}

.has-notifications {
  fill: var(--bell-icon-notification-color, #ff0000);
}

.dismissed {
  fill: var(--bell-icon-dismissed-color, #ccc);
}

.notification-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: var(--notification-dot-size, 8px);
  height: var(--notification-dot-size, 8px);
  background-color: var(--notification-dot-color, #ff0000);
  border-radius: 50%;
}
</style>