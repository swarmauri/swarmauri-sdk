<template>
  <div class="cardbased-list" role="list">
    <div
      v-for="(card, index) in cards"
      :key="index"
      class="card"
      :class="{ hovered: hoveredIndex === index, selected: selectedIndex === index, disabled: card.disabled }"
      @mouseenter="hoveredIndex = index"
      @mouseleave="hoveredIndex = null"
      @click="selectCard(index)"
      :aria-disabled="card.disabled ? 'true' : 'false'"
    >
      <div class="card-content">
        <h3>{{ card.title }}</h3>
        <p>{{ card.description }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Card {
  title: string;
  description: string;
  disabled?: boolean;
}

export default defineComponent({
  name: 'CardbasedList',
  props: {
    cards: {
      type: Array as () => Card[],
      required: true,
    },
  },
  setup(props) {
    const hoveredIndex = ref<number | null>(null);
    const selectedIndex = ref<number | null>(null);

    const selectCard = (index: number) => {
      if (props.cards[index].disabled) {
        selectedIndex.value = index;
      }
    };

    return { hoveredIndex, selectedIndex, selectCard };
  },
});
</script>

<style scoped lang="css">
.cardbased-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--card-gap, 10px);
}

.card {
  background-color: var(--card-bg, #fff);
  border: var(--card-border, 1px solid #ddd);
  padding: var(--card-padding, 15px);
  transition: transform 0.3s ease, background-color 0.3s ease;
  cursor: pointer;
}

.card.hovered {
  background-color: var(--card-hover-bg, #f0f0f0);
}

.card.selected {
  border-color: var(--card-selected-border-color, #007bff);
}

.card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card-content h3 {
  margin: 0;
  font-size: var(--card-title-font-size, 16px);
}

.card-content p {
  margin: 5px 0 0;
  font-size: var(--card-description-font-size, 14px);
}
</style>