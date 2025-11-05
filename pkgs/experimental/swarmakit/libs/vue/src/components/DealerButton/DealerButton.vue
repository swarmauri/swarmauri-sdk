<template>
  <div class="dealer-button" :class="stateClass" aria-label="Dealer Button">
    D
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'DealerButton',
  props: {
    state: {
      type: String,
      default: 'default',
      validator: (value: string) => ['default', 'moving', 'hovered'].includes(value),
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
.dealer-button {
  width: var(--button-size);
  height: var(--button-size);
  border-radius: 50%;
  background: var(--button-background);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--button-shadow);
  transition: transform var(--transition-duration), background var(--transition-duration);
}

.dealer-button:hover {
  background: var(--button-hover-background);
}

.default {
  animation: none;
}

.moving {
  animation: move var(--move-duration) ease-in-out infinite alternate;
}

.hovered {
  background: var(--button-hover-background);
}

@keyframes move {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-10px);
  }
}
</style>