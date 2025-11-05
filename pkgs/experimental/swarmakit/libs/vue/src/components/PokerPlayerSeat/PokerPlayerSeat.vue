<template>
  <div class="poker-player-seat" :class="{ 'active-player': isActive, 'folded-player': isFolded }">
    <div class="avatar" aria-label="Player Avatar"></div>
    <div class="player-info">
      <span class="player-name">{{ playerName }}</span>
      <span class="player-chips">{{ playerChips }} chips</span>
    </div>
    <div class="player-cards">
      <div class="card" v-for="card in playerCards" :key="card.id">{{ card.suit }}{{ card.rank }}</div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface Card {
  id: number;
  suit: string;
  rank: string;
}

export default defineComponent({
  name: 'PokerPlayerSeat',
  props: {
    playerName: {
      type: String,
      default: 'Player',
    },
    playerChips: {
      type: Number,
      default: 0,
    },
    playerCards: {
      type: Array as () => Card[],
      default: () => [],
    },
    isActive: {
      type: Boolean,
      default: false,
    },
    isFolded: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.poker-player-seat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--seat-padding);
  border-radius: var(--border-radius);
  box-shadow: var(--seat-shadow);
  background-color: var(--seat-bg);
  transition: all var(--transition-duration);
}

.active-player {
  box-shadow: 0 0 10px var(--active-glow);
}

.folded-player {
  opacity: 0.6;
}

.avatar {
  width: var(--avatar-size);
  height: var(--avatar-size);
  background-color: var(--avatar-bg);
  border-radius: 50%;
  margin-bottom: var(--avatar-margin-bottom);
}

.player-info {
  text-align: center;
  margin-bottom: var(--info-margin-bottom);
}

.player-name {
  font-weight: bold;
}

.player-cards {
  display: flex;
  justify-content: center;
}

.card {
  margin: 0 var(--card-margin);
  padding: var(--card-padding);
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--card-shadow);
}
</style>