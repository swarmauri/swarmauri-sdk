<template>
  <div class="poker-chips" :class="stateClass">
    <div
      v-for="chip in chips"
      :key="chip.id"
      class="chip"
      :style="{ backgroundColor: chip.color }"
      :aria-label="`Chip denomination: ${chip.denomination}`"
    >
      {{ chip.denomination }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface Chip {
  id: number;
  color: string;
  denomination: number;
}

export default defineComponent({
  name: 'PokerChips',
  props: {
    chips: {
      type: Array as () => Chip[],
      default: () => [],
    },
    state: {
      type: String,
      default: 'stacked',
      validator: (value: string) => ['stacked', 'moving', 'betPlaced', 'allIn'].includes(value),
    },
  },
  computed: {
    stateClass() {
      return this.state;
    },
  },
});
</script>

<style scoped lang="css">
.poker-chips {
  display: flex;
  flex-wrap: wrap;
  transition: all var(--transition-duration);
}

.chip {
  width: var(--chip-size);
  height: var(--chip-size);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--chip-shadow);
  margin: var(--chip-margin);
}

.stacked .chip {
  transition: transform var(--transition-duration);
}

.moving .chip {
  animation: move var(--move-duration) ease-in-out infinite alternate;
}

.betPlaced .chip {
  animation: bet var(--bet-duration) ease-in-out;
}

.allIn .chip {
  animation: shake var(--shake-duration) ease-in-out;
}

@keyframes move {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-10px);
  }
}

@keyframes bet {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(20px);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(-5px);
  }
}
</style>