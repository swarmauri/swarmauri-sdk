<template>
  <div class="bet-slider" :aria-label="'Bet Slider'">
    <input
      type="range"
      :min="min"
      :max="max"
      :step="step"
      v-model="bet"
      :disabled="disabled"
      @input="updateBet"
      class="slider"
    />
    <input
      type="number"
      :min="min"
      :max="max"
      v-model.number="bet"
      :disabled="disabled"
      class="bet-input"
      @change="updateBet"
    />
    <div v-if="bet >= max" class="feedback">Max Bet Reached</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'BetSlider',
  props: {
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
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
  setup(props) {
    const bet = ref(props.min);

    const updateBet = () => {
      if (bet.value > props.max) {
        bet.value = props.max;
      }
    };

    watch(bet, updateBet);

    return {
      bet,
      updateBet,
    };
  },
});
</script>

<style scoped lang="css">
.bet-slider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--slider-gap);
}
.slider {
  width: 100%;
  margin: var(--slider-margin);
}
.bet-input {
  width: var(--input-width);
  padding: var(--input-padding);
  font-size: var(--input-font-size);
}
.feedback {
  color: var(--feedback-color);
  font-size: var(--feedback-font-size);
}
</style>