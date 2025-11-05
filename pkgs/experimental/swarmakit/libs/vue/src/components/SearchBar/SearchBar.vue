<template>
  <div class="search-bar" :class="{ focused: isFocused, disabled: isDisabled }">
    <input
      type="text"
      :placeholder="placeholder"
      :disabled="isDisabled"
      @focus="handleFocus"
      @blur="handleBlur"
      aria-label="Search"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SearchBar',
  props: {
    placeholder: {
      type: String,
      default: 'Search...',
    },
    isFocused: {
      type: Boolean,
      default: false,
    },
    isDisabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const isFocused = ref(props.isFocused)
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
.search-bar {
  display: flex;
  align-items: center;
  padding: var(--search-bar-padding, 8px);
  border: var(--search-bar-border, 1px solid #ccc);
  border-radius: var(--search-bar-border-radius, 4px);
  background-color: var(--search-bar-bg, #fff);
  transition: border-color 0.3s ease;
}

.search-bar input {
  flex: 1;
  border: none;
  outline: none;
  padding: var(--search-bar-input-padding, 8px);
}

.search-bar.focused {
  border-color: var(--search-bar-focused-border-color, #007bff);
}

.search-bar.disabled {
  background-color: var(--search-bar-disabled-bg, #f0f0f0);
}
</style>