<template>
  <div class="poker-table" :style="{ backgroundColor: tableColor }">
    <div class="seats" v-for="seat in seats" :key="seat.id">
      <div class="player" :class="{ 'player-active': seat.active }">{{ seat.name }}</div>
    </div>
    <div class="community-cards">
      <div class="card" v-for="card in communityCards" :key="card.id">{{ card.suit }}{{ card.rank }}</div>
    </div>
    <div class="dealer-button" role="button" aria-label="Dealer button"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface Seat {
  id: number;
  name: string;
  active: boolean;
}

interface Card {
  id: number;
  suit: string;
  rank: string;
}

export default defineComponent({
  name: 'PokerTable',
  props: {
    seats: {
      type: Array as () => Seat[],
      default: () => [],
    },
    communityCards: {
      type: Array as () => Card[],
      default: () => [],
    },
    tableColor: {
      type: String,
      default: 'var(--table-green)',
    },
  },
});
</script>

<style scoped lang="css">
.poker-table {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: var(--border-radius);
  box-shadow: var(--table-shadow);
  padding: var(--table-padding);
  transition: background-color var(--transition-duration);
}

.seats {
  display: flex;
  justify-content: space-around;
  width: 100%;
  margin-bottom: var(--seat-margin-bottom);
}

.player {
  background-color: var(--player-bg);
  padding: var(--player-padding);
  border-radius: var(--border-radius);
  transition: all var(--transition-duration);
}

.player-active {
  background-color: var(--player-active-bg);
}

.community-cards {
  display: flex;
  justify-content: center;
  margin-top: var(--community-cards-margin-top);
}

.card {
  margin: 0 var(--card-margin);
  padding: var(--card-padding);
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--card-shadow);
}

.dealer-button {
  width: var(--dealer-button-size);
  height: var(--dealer-button-size);
  background-color: var(--dealer-button-bg);
  border-radius: 50%;
  margin-top: var(--dealer-button-margin-top);
  transition: background-color var(--transition-duration);
}
</style>