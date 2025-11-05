<script lang="ts">
  export let steps: Array<{ label: string, status: 'completed' | 'active' | 'disabled' }> = [];
  export let ariaLabel: string = 'Stepper Indicator';
</script>

<nav aria-label={ariaLabel} class="stepper">
  {#each steps as { label, status }, index (label)}
    <div class="step" data-status={status} aria-current={status === 'active' ? 'step' : undefined}>
      <div class="step-circle"></div>
      <span class="step-label">{label}</span>
    </div>
    {#if index < steps.length - 1}
      <div class="step-separator"></div>
    {/if}
  {/each}
</nav>

<style lang="css">
  @import './Stepper.css';
</style>