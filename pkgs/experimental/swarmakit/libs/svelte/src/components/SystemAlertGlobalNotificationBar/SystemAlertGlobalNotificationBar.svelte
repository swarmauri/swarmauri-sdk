<script lang="ts">
  export let message: string;
  export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
  export let ariaLabel: string = 'System Alert Notification Bar';
</script>

<div class="notification-bar" data-type={type} role="alert" aria-label={ariaLabel}>
  <span class="notification-message">{message}</span>
</div>

<style lang="css">
  @import './SystemAlertGlobalNotificationBar.css';
</style>