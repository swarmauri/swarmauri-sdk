<template>
  <div class="slider-container" :class="{ disabled: isDisabled }">
    <input
      type="range"
      :min="min"
      :max="max"
      :value="value"
      :step="step"
      :disabled="isDisabled"
      @input="updateValue"
      aria-label="Slider"
    />
    <span class="slider-value" v-if="showValue">{{ value }}</span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Slider',
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
    isDisabled: {
      type: Boolean,
      default: false,
    },
    showValue: {
      type: Boolean,
      default: false,
    },
  },
  setup(_, { emit }) {
    const updateValue = (event: Event) => {
      const newValue = (event.target as HTMLInputElement).valueAsNumber;
      emit('update:value', newValue);
    };

    return { updateValue };
  },
});
</script>

<style scoped lang="css">
.slider-container {
  display: flex;
  align-items: center;
  padding: var(--slider-padding, 8px);
  margin: var(--slider-margin, 8px 0);
}

.slider-container input[type="range"] {
  flex: 1;
  margin-right: var(--slider-input-margin-right, 8px);
  accent-color: var(--slider-accent-color, #007bff);
}

.slider-container.disabled input[type="range"] {
  cursor: not-allowed;
  opacity: 0.5;
}

.slider-value {
  font-size: var(--slider-value-font-size, 14px);
  color: var(--slider-value-color, #333);
}
</style>