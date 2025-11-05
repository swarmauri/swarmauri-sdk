<template>
  <div class="poker-hand" :aria-label="'Poker Hand'" :data-folded="folded">
    <div v-for="card in cards" :key="card.id" class="card" :data-revealed="revealed">
      <span v-if="revealed" class="card-value">{{ card.value }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface Card {
  id: number;
  value: string;
}

export default defineComponent({
  name: 'PokerHand',
  props: {
    cards: {
      type: Array as PropType<Card[]>,
      required: true,
    },
    revealed: {
      type: Boolean,
      default: false,
    },
    folded: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.poker-hand {
  display: flex;
  gap: var(--card-gap);
  transition: opacity 0.3s;
}
.poker-hand[data-folded='true'] {
  opacity: 0.5;
}
.card {
  width: var(--card-width);
  height: var(--card-height);
  background-color: var(--card-back-color);
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: var(--card-border-radius);
  transition: transform 0.3s, background-color 0.3s;
}
.card[data-revealed='true'] {
  background-color: var(--card-front-color);
  transform: rotateY(180deg);
}
.card-value {
  font-size: var(--card-value-font-size);
  color: var(--card-value-color);
}
</style>