<template>
  <button
    class="dark-mode-toggle"
    :aria-pressed="isDarkMode"
    @click="toggleMode"
  >
    <span v-if="isDarkMode" aria-hidden="true">🌙</span>
    <span v-else aria-hidden="true">☀️</span>
    <span class="sr-only">{{ isDarkMode ? 'Switch to light mode' : 'Switch to dark mode' }}</span>
  </button>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'DarkModeToggle',
  setup() {
    const isDarkMode = ref(false);

    const toggleMode = () => {
      isDarkMode.value = !isDarkMode.value;
      document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : 'light');
    };

    return { isDarkMode, toggleMode };
  },
});
</script>

<style scoped lang="css">
.dark-mode-toggle {
  background-color: var(--toggle-bg-color, #f0f0f0);
  border: none;
  border-radius: var(--toggle-radius, 50%);
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.dark-mode-toggle:focus {
  outline: 2px solid var(--toggle-focus-color, #000);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>