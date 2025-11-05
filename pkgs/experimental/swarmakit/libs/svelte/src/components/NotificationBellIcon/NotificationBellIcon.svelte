<script lang="ts">
  export let hasNotifications: boolean = false;
  export let dismissed: boolean = false;
  export let ariaLabel: string = 'Notification Bell Icon';
</script>

<div class="notification-bell" role="button" aria-label={ariaLabel} aria-pressed={hasNotifications && !dismissed}>
  <svg class="bell-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12 24c1.104 0 2-.896 2-2h-4c0 1.104.896 2 2 2zm6-6v-5c0-3.075-1.51-5.737-4.406-6.32-.1-.02-.194-.03-.294-.03-.1 0-.194.01-.294.03C7.51 7.263 6 9.925 6 13v5l-2 2v1h16v-1l-2-2zm-2.09-2.416l-1.41-1.414C14.631 14.19 15 13.12 15 12c0-2.21-1.79-4-4-4s-4 1.79-4 4c0 1.12.369 2.19 1 3.17l-1.41 1.414C6.63 15.81 6 13.97 6 12c0-3.314 2.686-6 6-6s6 2.686 6 6c0 1.97-.63 3.81-1.09 5.584z"/>
  </svg>
  {#if hasNotifications && !dismissed}
    <span class="notification-dot" aria-hidden="true"></span>
  {/if}
</div>

<style lang="css">
  @import './NotificationBellIcon.css';
</style>