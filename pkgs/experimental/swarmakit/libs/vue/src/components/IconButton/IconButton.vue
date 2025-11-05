<template>
  <button
    :class="['icon-button', buttonState, { disabled }]"
    :aria-disabled="disabled"
    :disabled="disabled"
    @mouseover="isHover = true"
    @mouseleave="isHover = false"
    @mousedown="isActive = true"
    @mouseup="isActive = false"
  >
    <slot></slot>
  </button>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'IconButton',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const isHover = ref(false);
    const isActive = ref(false);

    const buttonState = computed(() => {
      if (props.disabled) return 'disabled';
      if (isActive.value) return 'active';
      if (isHover.value) return 'hover';
      return '';
    });

    return {
      isHover,
      isActive,
      buttonState,
    };
  },
});
</script>

<style scoped>
@import './IconButton.css';
</style>