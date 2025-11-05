<template>
  <div class="range-slider-container">
    <label 
      :class="['range-label', labelPosition]" 
      :aria-label="`Range slider at ${value}`" 
      :aria-disabled="disabled"
    >
      <span v-if="labelPosition === 'left' || labelPosition === 'center'">{{ label }}</span>
      <input 
        type="range" 
        :min="min" 
        :max="max" 
        :step="step" 
        :value="value" 
        :disabled="disabled" 
        @input="onInput" 
        @focus="onFocus" 
        @blur="onBlur" 
      />
      <span v-if="labelPosition === 'right'">{{ label }}</span>
    </label>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'RangeSlider',
  props: {
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
    },
    value: {
      type: Number,
      default: 50,
    },
    step: {
      type: Number,
      default: 1,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: '',
    },
    labelPosition: {
      type: String as PropType<'left' | 'center' | 'right'>,
      default: 'right',
    },
  },
  emits: ['update:value'],
  methods: {
    onInput(event: Event) {
      this.$emit('update:value', Number((event.target as HTMLInputElement).value));
    },
    onFocus() {
      this.$el.classList.add('focused');
    },
    onBlur() {
      this.$el.classList.remove('focused');
    },
  },
});
</script>

<style scoped>
@import './RangeSlider.css';
</style>