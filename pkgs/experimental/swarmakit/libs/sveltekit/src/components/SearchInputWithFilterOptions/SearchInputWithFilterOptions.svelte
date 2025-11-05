<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let query: string = '';
  export let filters: string[] = [];
  export let activeFilters: string[] = [];
  export let disabled: boolean = false;

  const dispatch = createEventDispatcher();

  function updateQuery(event: Event) {
    query = (event.target as HTMLInputElement).value;
    dispatch('search', { query });
  }

  function toggleFilter(filter: string) {
    if (activeFilters.includes(filter)) {
      activeFilters = activeFilters.filter(f => f !== filter);
    } else {
      activeFilters = [...activeFilters, filter];
    }
    dispatch('filterChange', { activeFilters });
  }
</script>

<div class="search-input-container">
  <input
    type="text"
    class="search-input"
    placeholder="Search..."
    bind:value={query}
    on:input={updateQuery}
    disabled={disabled}
    aria-label="Search input"
  />
  <div class="filter-options">
    {#each filters as filter}
      <button
        type="button"
        class="filter-button {activeFilters.includes(filter) ? 'active' : ''}"
        on:click={() => toggleFilter(filter)}
        aria-pressed={activeFilters.includes(filter)}
        disabled={disabled}
      >
        {filter}
      </button>
    {/each}
  </div>
</div>

<style lang="css">
  @import './SearchInputWithFilterOptions.css';
</style>