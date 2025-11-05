<template>
  <div class="pot" :aria-label="'Poker Pot'" :class="{ won: isWon }">
    <div class="chips" :class="{ empty: totalChips === 0 }">
      <transition-group name="chip-move" tag="div" class="chip-stack">
        <div v-for="(chip, index) in chips" :key="index" class="chip">{{ chip }}</div>
      </transition-group>
    </div>
    <div class="total">Total: {{ totalChips }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'Pot',
  props: {
    chips: {
      type: Array as PropType<number[]>,
      default: () => [],
    },
    totalChips: {
      type: Number,
      default: 0,
    },
    isWon: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.pot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--pot-gap);
  transition: background-color 0.3s;
}
.won {
  background-color: var(--pot-won-bg-color);
}
.chips {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--chip-gap);
}
.empty {
  opacity: 0.5;
}
.chip-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.chip {
  padding: var(--chip-padding);
  border: var(--chip-border);
  border-radius: var(--chip-border-radius);
  background-color: var(--chip-bg-color);
}
.total {
  font-weight: bold;
}
.chip-move-enter-active, .chip-move-leave-active {
  transition: transform 0.5s;
}
.chip-move-enter, .chip-move-leave-to {
  transform: translateY(-20px);
}
</style>