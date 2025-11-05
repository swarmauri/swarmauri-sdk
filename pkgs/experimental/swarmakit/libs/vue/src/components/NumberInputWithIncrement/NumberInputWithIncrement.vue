<template>
  <div class="number-input-container">
    <button 
      class="decrement-button" 
      @click="decrement" 
      :disabled="disabled" 
      aria-label="Decrement"
    >
      -
    </button>
    <input 
      type="number" 
      v-model="currentValue" 
      :disabled="disabled" 
      aria-label="Number Input"
    />
    <button 
      class="increment-button" 
      @click="increment" 
      :disabled="disabled" 
      aria-label="Increment"
    >
      +
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref} from 'vue';

export default defineComponent({
  name: 'NumberInputWithIncrement',
  props: {
    modelValue: {
      type: Number,
      default: 0,
    },
    step: {
      type: Number,
      default: 1,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const currentValue = ref(props.modelValue);

    const increment = () => {
      currentValue.value += props.step;
      emit('update:modelValue', currentValue.value);
    };

    const decrement = () => {
      currentValue.value -= props.step;
      emit('update:modelValue', currentValue.value);
    };

    return { currentValue, increment, decrement };
  },
});
</script>

<style scoped lang="css">
@import './NumberInputWithIncrement.css';
</style>