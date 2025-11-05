<template>
  <div class="radio-button-container">
    <label :class="{ disabled: disabled }">
      <input 
        type="radio" 
        :checked="checked" 
        :disabled="disabled" 
        @change="onChange" 
        :aria-checked="checked" 
        :aria-disabled="disabled"
      />
      <span class="radio-label"><slot></slot></span>
    </label>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'RadioButton',
  props: {
    checked: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    value: {
      type: String as PropType<string>,
      required: true,
    },
    name: {
      type: String as PropType<string>,
      required: true,
    },
  },
  emits: ['update:checked'],
  methods: {
    onChange(event: Event) {
      if (!this.disabled) {
        this.$emit('update:checked', (event.target as HTMLInputElement).checked);
      }
    },
  },
});
</script>

<style scoped lang="css">
@import './RadioButton.css';
</style>