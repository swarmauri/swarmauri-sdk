<template>
  <div
    class="chat-bubble"
    :class="{ read, unread, hover: isHovered, active }"
    role="alert"
    aria-live="polite"
    @mouseover="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <slot></slot>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ChatBubble',
  props: {
    read: {
      type: Boolean,
      default: false,
    },
    unread: {
      type: Boolean,
      default: false,
    },
    active: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const isHovered = ref(false);
    return { isHovered };
  },
});
</script>

<style scoped lang="css">
.chat-bubble {
  padding: var(--chat-bubble-padding, 10px);
  border-radius: var(--chat-bubble-radius, 8px);
  background-color: var(--chat-bubble-bg-color, #f1f1f1);
  color: var(--chat-bubble-text-color, #333);
  transition: background-color 0.3s;
}

.chat-bubble.read {
  background-color: var(--chat-bubble-read-bg-color, #e0e0e0);
}

.chat-bubble.unread {
  background-color: var(--chat-bubble-unread-bg-color, #cce5ff);
}

.chat-bubble.hover {
  background-color: var(--chat-bubble-hover-bg-color, #b3d9ff);
}

.chat-bubble.active {
  background-color: var(--chat-bubble-active-bg-color, #99ccff);
}
</style>