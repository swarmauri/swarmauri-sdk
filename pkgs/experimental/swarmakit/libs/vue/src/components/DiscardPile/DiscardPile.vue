<template>
  <div
    class="discard-pile"
    :class="{ empty: isEmpty, full: isFull, hovered: isHovered }"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
  >
    <div
      v-for="(card, index) in cards"
      :key="card.id"
      class="card"
      :style="{ top: `${index * overlapOffset}px`, left: `${index * overlapOffset}px` }"
    >
      <slot name="card" :card="card"></slot>
    </div>
    <div v-if="isEmpty" class="empty-notification">Pile is empty</div>
    <div v-if="isFull" class="full-notification">Pile is full</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

interface Card {
  id: number;
  content: string;
}

export default defineComponent({
  name: 'DiscardPile',
  props: {
    cards: {
      type: Array as () => Card[],
      required: true,
    },
    maxCards: {
      type: Number,
      default: 10,
    },
    overlapOffset: {
      type: Number,
      default: 5,
    },
  },
  setup(props) {
    const cards = ref<Card[]>([...props.cards]);
    const isHovered = ref(false);

    const isEmpty = computed(() => cards.value.length === 0);
    const isFull = computed(() => cards.value.length >= props.maxCards);

    const handleDragOver = () => {
      isHovered.value = true;
    };

    const handleDragLeave = () => {
      isHovered.value = false;
    };

    return {
      cards,
      isEmpty,
      isFull,
      isHovered,
      handleDragOver,
      handleDragLeave,
    };
  },
});
</script>

<style scoped lang="css">
.discard-pile {
  position: relative;
  width: var(--pile-width, 150px);
  height: var(--pile-height, 200px);
  border: var(--pile-border, 2px dashed #ccc);
  border-radius: var(--pile-border-radius, 5px);
  background-color: var(--pile-bg-color, #f9f9f9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  position: absolute;
  transition: transform 0.2s;
  border-radius: var(--card-border-radius, 5px);
  box-shadow: var(--card-shadow, 0 4px 8px rgba(0, 0, 0, 0.1));
}

.discard-pile.hovered {
  border-color: var(--pile-hover-border-color, #007bff);
  background-color: var(--pile-hover-bg-color, #e6f7ff);
}

.empty-notification,
.full-notification {
  position: absolute;
  color: var(--notification-color, #ff6f61);
  font-size: var(--notification-font-size, 14px);
}
</style>