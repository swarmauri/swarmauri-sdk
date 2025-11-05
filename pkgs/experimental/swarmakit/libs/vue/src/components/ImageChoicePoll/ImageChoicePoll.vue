<template>
  <div class="image-choice-poll" role="group" aria-labelledby="image-choice-poll-label">
    <div id="image-choice-poll-label" class="poll-label">{{ question }}</div>
    <div class="options">
      <button
        v-for="(option, index) in options"
        :key="index"
        :class="['option', { selected: selectedOption === index, disabled: disabled }]"
        @click="selectOption(index)"
        :disabled="disabled"
        :aria-pressed="selectedOption === index"
        aria-label="Option"
      >
        <img :src="option.image" :alt="option.alt" class="option-image" />
      </button>
    </div>
    <div class="result-display" v-if="resultsVisible && selectedOption !== null">
      Selected: {{ options[selectedOption].alt }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Option {
  image: string;
  alt: string;
}

export default defineComponent({
  name: 'ImageChoicePoll',
  props: {
    question: {
      type: String,
      required: true
    },
    options: {
      type: Array as () => Option[],
      required: true
    },
    initialValue: {
      type: Number,
      default: null
    },
    resultsVisible: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const selectedOption = ref(props.initialValue);

    const selectOption = (index: number) => {
      if (!props.disabled) {
        selectedOption.value = index;
      }
    };

    return {
      selectedOption,
      selectOption
    };
  }
});
</script>

<style scoped lang="css">
.image-choice-poll {
  padding: 1rem;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 5px;
  max-width: 500px;
  margin: 0 auto;
}

.poll-label {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.option {
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.option.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.option-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 5px;
}

.selected .option-image {
  border: 2px solid var(--selected-border-color, #007bff);
}

.result-display {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>