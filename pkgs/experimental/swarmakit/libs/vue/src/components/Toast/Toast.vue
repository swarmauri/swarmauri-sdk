<template>
  <div
    class="toast"
    :class="type"
    role="alert"
    aria-live="assertive"
    aria-atomic="true"
  >
    <span>{{ message }}</span>
    <button class="close-btn" @click="dismiss" aria-label="Dismiss">
      &times;
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Toast',
  props: {
    message: {
      type: String,
      required: true,
    },
    type: {
      type: String as () => 'success' | 'error' | 'warning' | 'info',
      required: true,
    },
  },
  setup() {
    const isVisible = ref(true);

    const dismiss = () => {
      isVisible.value = false;
    };

    return { dismiss, isVisible };
  },
});
</script>

<style scoped lang="css">
.toast {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--toast-padding, 16px);
  border-radius: var(--toast-border-radius, 4px);
  margin-bottom: var(--toast-margin-bottom, 16px);
  transition: opacity 0.3s ease;
}

.toast.success {
  background-color: var(--toast-success-bg, #d4edda);
  color: var(--toast-success-color, #155724);
}

.toast.error {
  background-color: var(--toast-error-bg, #f8d7da);
  color: var(--toast-error-color, #721c24);
}

.toast.warning {
  background-color: var(--toast-warning-bg, #fff3cd);
  color: var(--toast-warning-color, #856404);
}

.toast.info {
  background-color: var(--toast-info-bg, #d1ecf1);
  color: var(--toast-info-color, #0c5460);
}

.close-btn {
  background: none;
  border: none;
  font-size: var(--close-btn-font-size, 16px);
  cursor: pointer;
  color: inherit;
}
</style>