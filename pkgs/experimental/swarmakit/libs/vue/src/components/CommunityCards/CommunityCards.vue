<template>
  <div class="community-cards" role="group" aria-label="Community Cards">
    <svg
      v-for="card in cards"
      :key="card.id"
      :class="'card ' + card.state"
      viewBox="0 0 100 150"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect width="100" height="150" rx="10" ry="10" class="card-background"/>
      <text v-if="card.state === 'revealed'" x="50" y="75" text-anchor="middle" class="card-text">{{ card.label }}</text>
    </svg>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface Card {
  id: number;
  state: 'dealt' | 'revealed' | 'empty' | 'full';
  label: string;
}

export default defineComponent({
  name: 'CommunityCards',
  props: {
    cards: {
      type: Array as PropType<Card[]>,
      required: true,
    },
  },
});
</script>

<style scoped lang="css">
@media (max-width: 600px) {
  .community-cards {
    display: flex;
    justify-content: space-around;
  }
}

@media (min-width: 601px) and (max-width: 768px) {
  .community-cards {
    display: flex;
    justify-content: space-between;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .community-cards {
    display: flex;
    justify-content: space-evenly;
  }
}

@media (min-width: 1025px) {
  .community-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: var(--card-gap, 10px);
  }
}

.card {
  transition: transform 0.3s ease-in-out;
}

.card.dealt {
  transform: rotateY(180deg);
}

.card.revealed {
  transform: rotateY(0deg);
}

.card-background {
  fill: var(--card-background-color, #ffffff);
  stroke: var(--card-border-color, #000000);
  stroke-width: 2;
}

.card-text {
  fill: var(--card-text-color, #000000);
  font-size: var(--card-text-size, 24px);
}
</style>