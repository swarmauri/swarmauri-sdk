<template>
  <div class="winning-hand-display" :aria-label="'Winning Hand Display'" :class="{ hidden: isHidden }">
    <div class="cards">
      <div v-for="(card, index) in communityCards" :key="'community-' + index" class="card community-card">
        {{ card }}
      </div>
      <div v-for="(card, index) in playerCards" :key="'player-' + index" class="card player-card" :class="{ winner: winningCards.includes(card) }">
        {{ card }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'WinningHandDisplay',
  props: {
    communityCards: {
      type: Array as PropType<string[]>,
      default: () => [],
    },
    playerCards: {
      type: Array as PropType<string[]>,
      default: () => [],
    },
    winningCards: {
      type: Array as PropType<string[]>,
      default: () => [],
    },
    isHidden: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.winning-hand-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--card-gap);
  transition: opacity 0.3s;
}
.hidden {
  opacity: 0;
  pointer-events: none;
}
.cards {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--card-gap);
}
.card {
  padding: var(--card-padding);
  border: var(--card-border);
  border-radius: var(--card-border-radius);
  background-color: var(--card-bg-color);
}
.community-card {
  background-color: var(--community-card-bg-color);
}
.winner {
  border-color: var(--winner-border-color);
}
</style>