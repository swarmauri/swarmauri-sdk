<script lang="ts">
  export let progress: number = 0;
  export let state: 'complete' | 'incomplete' | 'in-progress' | 'paused' | 'active' = 'in-progress';
  export let ariaLabel: string = 'Progress Circle';
  
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (progress / 100) * circumference;
</script>

<svg
  class="progress-circle"
  width="100"
  height="100"
  aria-label={ariaLabel}
  role="progressbar"
  aria-valuenow={progress}
  aria-valuemin="0"
  aria-valuemax="100"
>
  <circle cx="50" cy="50" r="45" class="background" />
  <circle
    cx="50"
    cy="50"
    r="45"
    class="progress"
    stroke-dasharray="{circumference}"
    stroke-dashoffset="{offset}"
  />
</svg>

<style lang="css">
  @import './ProgressCircle.css';
</style>