<template>
  <div class="focus-indicator" :class="{ focused: isFocused }" tabindex="0" @focus="handleFocus" @blur="handleBlur">
    <span>{{ label }}</span>
  </div>
</template>

<script lang="ts">
import { defineComponent,ref } from 'vue';

export default defineComponent({
  name: 'VisualCueForAccessibilityFocusIndicator',
  props: {
    label: {
      type: String,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const isFocused = ref(props.isFocused);
    const handleFocus = () => {
      isFocused.value = true;
    };

    const handleBlur = () => {
      isFocused.value = false;
    };

    return { handleFocus, handleBlur };
  },
});
</script>

<style scoped lang="css">
.focus-indicator {
  padding: var(--focus-indicator-padding, 8px);
  border-radius: var(--focus-indicator-border-radius, 4px);
  margin-bottom: var(--focus-indicator-margin-bottom, 8px);
  transition: box-shadow 0.3s ease;
  outline: none;
}

.focus-indicator.focused {
  box-shadow: var(--focus-indicator-focused-shadow, 0 0 0 3px #007bff);
  background-color: var(--focus-indicator-focused-bg, #f0f8ff);
}

.focus-indicator:not(.focused) {
  background-color: var(--focus-indicator-unfocused-bg, #ffffff);
}
</style>