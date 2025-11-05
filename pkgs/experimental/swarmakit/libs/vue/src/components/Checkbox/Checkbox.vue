<template>
  <div class="checkbox-container">
    <input 
      type="checkbox" 
      :checked="checked" 
      :disabled="disabled" 
      @change="$emit('update:checked', ($event.target as HTMLInputElement).checked)" 
      :aria-checked="checked" 
      :aria-disabled="disabled"
    />
    <label :class="{ 'checkbox--disabled': disabled }">
      <slot />
    </label>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Checkbox',
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
});
</script>

<style scoped lang="css">
@import './Checkbox.css';
</style>
