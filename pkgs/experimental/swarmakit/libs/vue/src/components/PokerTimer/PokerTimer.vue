<template>
  <div class="poker-timer" :aria-label="'Poker Timer'">
    <div :class="['timer-display', { 'time-running-out': timeRunningOut }]">
      {{ formattedTime }}
    </div>
    <button @click="togglePause" class="timer-button">
      {{ isPaused ? 'Resume' : 'Pause' }}
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue';

export default defineComponent({
  name: 'PokerTimer',
  props: {
    initialTime: {
      type: Number,
      default: 30,
    },
  },
  setup(props) {
    const timeLeft = ref(props.initialTime);
    const isPaused = ref(false);

    const formattedTime = computed(() => {
      const minutes = Math.floor(timeLeft.value / 60);
      const seconds = timeLeft.value % 60;
      return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    });

    const timeRunningOut = computed(() => timeLeft.value <= 10);

    const tick = () => {
      if (!isPaused.value && timeLeft.value > 0) {
        timeLeft.value -= 1;
      }
    };

    const togglePause = () => {
      isPaused.value = !isPaused.value;
    };

    let intervalId: ReturnType<typeof setInterval>;
    onMounted(() => {
      intervalId = setInterval(tick, 1000);
    });

    onUnmounted(() => {
      clearInterval(intervalId);
    });

    return {
      timeLeft,
      formattedTime,
      timeRunningOut,
      isPaused,
      togglePause,
    };
  },
});
</script>

<style scoped lang="css">
.poker-timer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--timer-gap);
}
.timer-display {
  font-size: var(--timer-font-size);
  color: var(--timer-color);
}
.time-running-out {
  color: var(--timer-warning-color);
}
.timer-button {
  padding: var(--button-padding);
  font-size: var(--button-font-size);
}
</style>