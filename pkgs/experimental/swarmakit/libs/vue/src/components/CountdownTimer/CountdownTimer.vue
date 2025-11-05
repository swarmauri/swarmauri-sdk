<template>
  <div class="countdown-timer" role="timer" :aria-live="isCompleted ? 'off' : 'assertive'">
    <span :class="timerState">{{ formattedTime }}</span>
    <button @click="togglePause" aria-label="Pause or resume countdown">
      {{ isPaused ? 'Resume' : 'Pause' }}
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue';

export default defineComponent({
  name: 'CountdownTimer',
  props: {
    duration: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const timeLeft = ref(props.duration);
    const isPaused = ref(false);
    const intervalId = ref<number | null>(null);

    const formattedTime = computed(() => {
      const minutes = Math.floor(timeLeft.value / 60).toString().padStart(2, '0');
      const seconds = (timeLeft.value % 60).toString().padStart(2, '0');
      return `${minutes}:${seconds}`;
    });

    const timerState = computed(() => {
      if (timeLeft.value <= 0) return 'completed';
      return isPaused.value ? 'paused' : 'running';
    });

    const isCompleted = computed(() => timeLeft.value <= 0);

    const togglePause = () => {
      if (isCompleted.value) return;
      isPaused.value = !isPaused.value;
      if (!isPaused.value) startTimer();
    };

    const startTimer = () => {
      if (intervalId.value !== null) clearInterval(intervalId.value);
      intervalId.value = window.setInterval(() => {
        if (!isPaused.value && timeLeft.value > 0) {
          timeLeft.value -= 1;
        }
      }, 1000);
    };

    onMounted(() => {
      startTimer();
    });

    onUnmounted(() => {
      if (intervalId.value !== null) clearInterval(intervalId.value);
    });

    return { formattedTime, timerState, isPaused, togglePause, isCompleted };
  },
});
</script>

<style scoped lang="css">
.countdown-timer {
  display: flex;
  align-items: center;
  font-size: var(--timer-font-size, 24px);
  color: var(--timer-text-color, #000);
}

.running {
  color: var(--running-color, #007bff);
}

.paused {
  color: var(--paused-color, #ff9900);
}

.completed {
  color: var(--completed-color, #28a745);
}

button {
  margin-left: 10px;
  padding: var(--button-padding, 5px 10px);
  background-color: var(--button-bg-color, #f0f0f0);
  border: none;
  border-radius: var(--button-border-radius, 5px);
  cursor: pointer;
}
</style>