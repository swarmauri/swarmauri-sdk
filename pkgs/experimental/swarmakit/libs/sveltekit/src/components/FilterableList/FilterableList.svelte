<script lang="ts">
  import { writable } from 'svelte/store';

  export let items: string[] = [];
  let filterText = writable<string>('');
  let filteredItems = writable<string[]>(items);

  const applyFilter = () => {
    filteredItems.set(items.filter(item => item.toLowerCase().includes($filterText.toLowerCase())));
  };

  const clearFilter = () => {
    filterText.set('');
    filteredItems.set(items);
  };

  $: applyFilter(); // Reapply filter whenever filterText or items changes
</script>

<div class="filterable-list">
  <input 
    type="text" 
    bind:value={$filterText} 
    placeholder="Filter items..." 
    aria-label="Filter items"
    on:input={applyFilter}
  />
  <button on:click={clearFilter} aria-label="Clear filter">Clear</button>
  <ul>
    {#if $filteredItems.length > 0}
      {#each $filteredItems as item (item)}
        <li>{item}</li>
      {/each}
    {:else}
      <li class="no-results">No results found</li>
    {/if}
  </ul>
</div>

<style lang="css">
  @import './FilterableList.css';
</style>