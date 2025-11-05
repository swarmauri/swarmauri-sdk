<script lang="ts">
  export let tabs: { label: string, content: string, disabled?: boolean }[] = [];
  export let activeIndex = 0;

  function setActive(index: number) {
    if (!tabs[index]?.disabled) {
      activeIndex = index;
    }
  }
</script>

<div class="tabs">
  <div class="tab-list" role="tablist">
    {#each tabs as { label, disabled }, index}
      <button
        role="tab"
        class="tab-button"
        aria-selected={activeIndex === index}
        aria-disabled={disabled}
        on:click={() => setActive(index)}
        on:keydown={(event) => event.key === 'Enter' && setActive(index)}
        tabindex={disabled ? -1 : activeIndex === index ? 0 : -1}
      >
        {label}
      </button>
    {/each}
  </div>
  <div class="tab-content" role="tabpanel">
    {#if tabs.length > 0}
      {tabs[activeIndex]?.content}
    {/if}
  </div>
</div>

<style lang="css">
  @import './Tabs.css';
</style>