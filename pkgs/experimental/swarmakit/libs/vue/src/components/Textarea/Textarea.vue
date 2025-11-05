<template>
  <div class="textarea-container">
    <textarea 
      :placeholder="placeholder" 
      :disabled="disabled"
      aria-label="Textarea input"
      v-model="text"
      @input="onInput"
    ></textarea>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Textarea',
  props: {
    placeholder: {
      type: String,
      default: 'Enter text...',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['input'],
  setup(_, { emit }) {
    const text = ref('');

    const onInput = () => {
      emit('input', text.value);
    };

    return {
      text,
      onInput,
    };
  },
});
</script>

<style scoped>
@import './Textarea.css';
</style>