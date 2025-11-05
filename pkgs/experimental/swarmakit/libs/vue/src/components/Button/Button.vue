<template>
  <button
    :class="['button', buttonType, { disabled }]"
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
  name: 'Button',
  props: {
    type: {
      type: String as () => 'primary' | 'secondary',
      default: 'primary',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const isHover = ref(false);
    const isActive = ref(false);

    const buttonType = computed(() => {
      if (props.disabled) return 'disabled';
      if (isActive.value) return 'active';
      if (isHover.value) return 'hover';
      return props.type;
    });

    return {
      isHover,
      isActive,
      buttonType,
    };
  },
});
</script>

<style scoped>
@import './Button.css';
</style>