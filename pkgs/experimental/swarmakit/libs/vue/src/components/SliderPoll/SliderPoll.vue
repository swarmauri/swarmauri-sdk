<template>
  <div class="slider-poll">
    <label :for="id" class="slider-label">{{ question }}</label>
    <input
      type="range"
      :id="id"
      :min="min"
      :max="max"
      :value="initialValue"
      :disabled="isDisabled"
      @input="updateValue"
      class="slider"
      aria-valuemin="min"
      aria-valuemax="max"
      :aria-valuenow="selectedValue"
      aria-label="Value slider"
    />
    <div v-if="showResults" class="results">
      <p>Selected Value: {{ selectedValue }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SliderPoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    min: {
      type: Number,
      default: 1,
    },
    max: {
      type: Number,
      default: 100,
    },
    initialValue: {
      type: Number,
      default: 50,
    },
    isDisabled: {
      type: Boolean,
      default: false,
    },
    showResults: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const selectedValue = ref(props.initialValue);
    const id = ref(`slider-${Math.random().toString(36).substr(2, 9)}`);

    const updateValue = (event: Event) => {
      if (!props.isDisabled) {
        const target = event.target as HTMLInputElement;
        selectedValue.value = Number(target.value);
      }
    };

    return {
      selectedValue,
      updateValue,
      id,
    };
  },
});
</script>

<style scoped>
.slider-poll {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 16px;
}

.slider-label {
  font-size: 1rem;
  margin-bottom: 8px;
}

.slider {
  width: 100%;
  max-width: 300px;
  margin: 10px 0;
}

.slider:disabled {
  opacity: 0.5;
}

.results {
  font-size: 0.9rem;
  color: var(--primary-color);
}
</style>