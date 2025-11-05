<template>
  <div class="deck" role="list" aria-label="Deck of Cards">
    <div 
      v-for="(card, index) in cards" 
      :key="card.id" 
      class="card" 
      :style="{ zIndex: index, transform: `translateY(${index * overlap}px)` }" 
      role="listitem"
      aria-label="Card"
      draggable="true"
      @dragstart="onDragStart(index)"
      @dragover.prevent
      @drop="onDrop(index)"
    >
      <slot :card="card"></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'DeckOfCards',
  props: {
    cards: {
      type: Array as () => Array<{ id: number }>,
      required: true,
    },
    overlap: {
      type: Number,
      default: 10,
    },
  },
  setup(props) {
    const draggedCardIndex = ref<number | null>(null);

    const onDragStart = (index: number) => {
      draggedCardIndex.value = index;
    };

    const onDrop = (index: number) => {
      if (draggedCardIndex.value !== null && draggedCardIndex.value !== index) {
        const [draggedCard] = props.cards.splice(draggedCardIndex.value, 1);
        props.cards.splice(index, 0, draggedCard);
      }
      draggedCardIndex.value = null;
    };

    return { onDragStart, onDrop };
  },
});
</script>

<style scoped lang="css">
.deck {
  display: flex;
  flex-direction: column;
  position: relative;
  width: var(--deck-width, 300px);
  height: var(--deck-height, 400px);
}

.card {
  position: absolute;
  width: 100%;
  height: var(--card-height, 100%);
  transition: transform 0.3s ease;
  box-shadow: var(--card-shadow, 0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>