<script lang="ts">
  export let items: { id: number; text: string; action: () => void; disabled?: boolean }[] = [];
  export let loading: boolean = false;

  const handleAction = (item: { id: number; text: string; action: () => void; disabled?: boolean }) => {
    if (!item.disabled) {
      item.action();
    }
  };
</script>

<div class="actionable-list">
  {#if loading}
    <div class="loading">Loading...</div>
  {:else}
    <ul>
      {#each items as item (item.id)}
        <li class:disabled={item.disabled}>
          <button 
            on:click={() => handleAction(item)} 
            disabled={item.disabled} 
            aria-disabled={item.disabled}
          >
            {item.text}
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style lang="css">
  @import './ActionableList.css';
</style>