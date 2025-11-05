<script lang="ts">
  type Step = {
    label: string;
    status: 'active' | 'completed' | 'inactive';
  };

  export let steps: Step[] = [];
  export let ariaLabel: string = 'Loading Bars with Steps';
</script>

<div class="loading-bars-with-steps" role="progressbar" aria-label={ariaLabel}>
  {#each steps as { label, status }}
    <div class={`step ${status}`}>
      <div class="step-label">{label}</div>
      <div class="loading-bar"></div>
    </div>
  {/each}
</div>

<style lang="css">
  @import './LoadingBarsWithSteps.css';
</style>