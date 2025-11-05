<template>
  <div role="group" aria-labelledby="poll-question" class="poll">
    <p id="poll-question">{{ question }}</p>
    <div v-for="option in options" :key="option" class="option">
      <input
        type="checkbox"
        :id="option"
        :value="option"
        v-model="selectedOptions"
        :disabled="isDisabled"
        @change="handleChange"
        :aria-checked="selectedOptions.includes(option)"
      />
      <label :for="option">{{ option }}</label>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'MultipleChoicePoll',
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
  emits: ['update:selectedOptions'],
  setup(_, { emit }) {
    const selectedOptions = ref<string[]>([]);
    
    const handleChange = () => {
      emit('update:selectedOptions', selectedOptions.value);
    };

    return {
      selectedOptions,
      handleChange,
    };
  },
});
</script>

<style scoped>
.poll {
  margin: 16px;
}

.option {
  margin-bottom: 8px;
}

input[type="checkbox"] {
  accent-color: var(--primary-color);
}
</style>