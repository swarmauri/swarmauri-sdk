<template>
  <div role="group" aria-labelledby="poll-question" class="poll">
    <p id="poll-question">{{ question }}</p>
    <div v-for="option in options" :key="option" class="option">
      <input
        type="radio"
        :id="option"
        :value="option"
        v-model="selectedOption"
        :disabled="isDisabled"
        @change="handleChange"
        :aria-checked="selectedOption === option"
      />
      <label :for="option">{{ option }}</label>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SingleChoicePoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    options: {
      type: Array as () => string[],
      required: true,
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
  emits: ['update:selectedOption'],
  setup(_, { emit }) {
    const selectedOption = ref<string | null>(null);

    const handleChange = () => {
      emit('update:selectedOption', selectedOption.value);
    };

    return {
      selectedOption,
      handleChange,
    };
  },
});
</script>

<style scoped lang="css">
.poll {
  margin: 16px;
}

.option {
  margin-bottom: 8px;
}

input[type="radio"] {
  accent-color: var(--primary-color);
}
</style>