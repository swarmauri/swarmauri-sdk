<script lang="ts">
  export let progress: number = 0;
  export let disabled: boolean = false;
  export let ariaLabel: string = 'Progress Bar';
</script>

<div class="progress-bar-container" aria-disabled={disabled}>
  <div class="progress-bar" role="progressbar" aria-label={ariaLabel} aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100" style="width: {progress}%"></div>
</div>

<style lang="css">
  @import './ProgressBar.css';
</style>