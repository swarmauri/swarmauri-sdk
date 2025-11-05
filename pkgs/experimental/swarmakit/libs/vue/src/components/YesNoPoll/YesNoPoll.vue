<template>
  <div class="yes-no-poll" role="radiogroup" aria-labelledby="poll-question">
    <p id="poll-question">{{ question }}</p>
    <div class="options">
      <button
        :aria-checked="selectedOption === 'yes'"
        :disabled="isDisabled"
        @click="selectOption('yes')"
        class="option"
        :class="{ selected: selectedOption === 'yes' }"
        role="radio"
      >
        Yes
      </button>
      <button
        :aria-checked="selectedOption === 'no'"
        :disabled="isDisabled"
        @click="selectOption('no')"
        class="option"
        :class="{ selected: selectedOption === 'no' }"
        role="radio"
      >
        No
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'YesNoPoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    initialSelection: {
      type: String as () => 'yes' | 'no' | null,
      default: null,
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
    const selectedOption = ref(props.initialSelection);

    const selectOption = (option: 'yes' | 'no') => {
      if (!props.isDisabled) {
        selectedOption.value = option;
      }
    };

    return {
      selectedOption,
      selectOption,
    };
  },
});
</script>

<style scoped>
.yes-no-poll {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 16px;
}

.options {
  display: flex;
}

.option {
  font-size: 1.5rem;
  background: none;
  border: 1px solid var(--secondary-color);
  border-radius: 4px;
  cursor: pointer;
  margin: 0 5px;
  padding: 8px 16px;
  color: var(--secondary-color);
}

.option.selected {
  background-color: var(--primary-color);
  color: white;
}

.option:focus {
  outline: 2px solid var(--primary-color);
}
</style>