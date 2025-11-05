<template>
  <div
    class="playing-card"
    :class="{ 'is-flipped': flipped, 'is-disabled': disabled }"
    @click="handleClick"
    role="button"
    :aria-pressed="flipped"
    :aria-disabled="disabled"
    tabindex="0"
  >
    <div class="card-face card-front" v-if="!flipped">
      <slot name="back">Back Design</slot>
    </div>
    <div class="card-face card-back" v-else>
      <slot name="front">Ace of Spades</slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'PlayingCard',
  props: {
    flipped: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:flipped'],
  setup(props, { emit }) {
    const handleClick = () => {
      if (!props.disabled) {
        emit('update:flipped', !props.flipped);
      }
    };

    return { handleClick };
  }
});
</script>

<style scoped lang="css">
.playing-card {
  --card-width: 100px;
  --card-height: 140px;
  --border-radius: 10px;
  --transition-duration: 0.6s;
  width: var(--card-width);
  height: var(--card-height);
  perspective: 1000px;
  cursor: pointer;
  transition: transform var(--transition-duration);
  outline: none;
}

.playing-card.is-disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.card-face {
  width: 100%;
  height: 100%;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  backface-visibility: hidden;
  position: absolute;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-front {
  background: var(--card-back-pattern, #ccc);
}

.card-back {
  background: var(--card-front-pattern, white);
  transform: rotateY(180deg);
}

.playing-card.is-flipped .card-back {
  transform: rotateY(0);
}

.playing-card.is-flipped .card-front {
  transform: rotateY(180deg);
}

.playing-card:hover:not(.is-disabled) {
  transform: scale(1.05);
}

@media (max-width: 320px) {
  .playing-card {
    --card-width: 80px;
    --card-height: 112px;
  }
}

@media (min-width: 321px) and (max-width: 480px) {
  .playing-card {
    --card-width: 90px;
    --card-height: 126px;
  }
}

@media (min-width: 481px) and (max-width: 768px) {
  .playing-card {
    --card-width: 110px;
    --card-height: 154px;
  }
}

@media (min-width: 769px) {
  .playing-card {
    --card-width: 120px;
    --card-height: 168px;
  }
}
</style>