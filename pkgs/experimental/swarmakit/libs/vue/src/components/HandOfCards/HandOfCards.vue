<template>
  <div class="hand" :class="{ full: isFull, maxLimit: maxLimitReached }">
    <div
      v-for="(card) in hand"
      :key="card.id"
      class="card"
      :class="{ selected: selectedCards.includes(card.id) }"
      @click="toggleSelect(card.id)"
    >
      <slot name="card" :card="card"></slot>
    </div>
    <div v-if="maxLimitReached" class="limit-notification">Max card limit reached</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

interface Card {
  id: number;
  content: string;
}

export default defineComponent({
  name: 'HandOfCards',
  props: {
    cards: {
      type: Array as () => Card[],
      required: true,
    },
    maxCards: {
      type: Number,
      default: 5,
    },
  },
  setup(props) {
    const hand = ref<Card[]>([...props.cards]);
    const selectedCards = ref<number[]>([]);

    const toggleSelect = (cardId: number) => {
      if (selectedCards.value.includes(cardId)) {
        selectedCards.value = selectedCards.value.filter(id => id !== cardId);
      } else if (selectedCards.value.length < props.maxCards) {
        selectedCards.value.push(cardId);
      }
    };

    const isFull = computed(() => hand.value.length >= props.maxCards);
    const maxLimitReached = computed(() => selectedCards.value.length >= props.maxCards);

    return {
      hand,
      selectedCards,
      isFull,
      maxLimitReached,
      toggleSelect,
    };
  },
});
</script>

<style scoped lang="css">
.hand {
  display: flex;
  flex-direction: row;
  gap: var(--hand-card-gap, 10px);
  padding: var(--hand-padding, 10px);
  background-color: var(--hand-bg-color, #f0f0f0);
  border-radius: var(--hand-border-radius, 5px);
}

.card {
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: var(--card-shadow, 0 4px 8px rgba(0, 0, 0, 0.1));
  border-radius: var(--card-border-radius, 5px);
}

.card.selected {
  transform: scale(1.1);
  box-shadow: var(--card-selected-shadow, 0 6px 12px rgba(0, 0, 0, 0.2));
}

.hand.full {
  background-color: var(--hand-full-bg-color, #d4edda);
}

.limit-notification {
  color: var(--limit-notification-color, #ff6f61);
  font-size: var(--limit-notification-font-size, 14px);
  margin-left: var(--limit-notification-margin-left, 10px);
}
</style>