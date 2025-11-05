<script lang="ts">
  import { onMount } from 'svelte';
  
  export let duration: number = 60;
  export let autoStart: boolean = false;
  export let ariaLabel: string = 'Countdown Timer';

  let timeLeft: number = duration;
  let interval: NodeJS.Timeout | null = null;

  const start = () => {
    if (!interval) {
      interval = setInterval(() => {
        if (timeLeft > 0) {
          timeLeft -= 1;
        } else {
          clearInterval(interval!);
          interval = null;
        }
      }, 1000);
    }
  };

  const pause = () => {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
  };

  const reset = () => {
    timeLeft = duration;
    pause();
  };

  onMount(() => {
    if (autoStart) {
      start();
    }
  });
</script>

<div class="countdown-timer" role="timer" aria-label={ariaLabel}>
  <div class="time-display">{timeLeft}s</div>
  <button on:click={start} aria-label="Start Timer">Start</button>
  <button on:click={pause} aria-label="Pause Timer">Pause</button>
  <button on:click={reset} aria-label="Reset Timer">Reset</button>
</div>

<style lang="css">
  @import './CountdownTimer.css';
</style>