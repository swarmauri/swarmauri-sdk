<template>
  <div class="toggle-switch">
    <input 
      type="checkbox" 
      :checked="checked" 
      :disabled="disabled" 
      @change="onToggle" 
      :aria-checked="checked"
      role="switch"
    />
    <span class="slider"></span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ToggleSwitch',
  props: {
    checked: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['change'],
  setup(_, { emit }) {
    const onToggle = (event: Event) => {
      emit('change', (event.target as HTMLInputElement).checked);
    };

    return {
      onToggle,
    };
  },
});
</script>

<style scoped>
@import './ToggleSwitch.css';
</style>