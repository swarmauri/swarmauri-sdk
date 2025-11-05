<template>
  <div
    class="flip-card"
    @click="toggleFlip"
    :aria-disabled="disabled"
    :class="{ flipped, disabled }"
  >
    <div class="flip-card-inner" :style="{ transform: flipped ? 'rotateY(180deg)' : 'none' }">
      <div class="flip-card-front" role="region" aria-label="Front Content">
        <slot name="front"></slot>
      </div>
      <div class="flip-card-back" role="region" aria-label="Back Content">
        <slot name="back"></slot>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'FlipCard',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const flipped = ref(false);

    const toggleFlip = () => {
      if (!props.disabled) {
        flipped.value = !flipped.value;
      }
    };

    return {
      flipped,
      toggleFlip,
    };
  },
});
</script>

<style scoped lang="css">
.flip-card {
  width: var(--flip-card-width, 300px);
  height: var(--flip-card-height, 200px);
  perspective: 1000px;
  border-radius: var(--flip-card-border-radius, 10px);
  transition: transform 0.6s;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  border-radius: inherit;
}

.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--flip-card-bg-color, #f0f0f0);
}

.flip-card-back {
  transform: rotateY(180deg);
}

.flip-card.disabled {
  cursor: not-allowed;
}

.flip-card:not(.disabled):hover {
  cursor: pointer;
}
</style>