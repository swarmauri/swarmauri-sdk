<script lang="ts">
  import { onMount } from 'svelte';

  export let items: string[] = [];
  export let loadMore: () => Promise<string[]>;
  export let isLoading: boolean = false;
  export let isEndOfList: boolean = false;

  const handleLoadMore = async () => {
    if (!isLoading && !isEndOfList) {
      isLoading = true;
      const newItems = await loadMore();
      items = [...items, ...newItems];
      isEndOfList = newItems.length === 0;
      isLoading = false;
    }
  };
</script>

<div class="list-container">
  <ul>
    {#each items as item (item)}
      <li>{item}</li>
    {/each}
  </ul>
  {#if !isEndOfList}
    <button on:click={handleLoadMore} disabled={isLoading} aria-busy={isLoading}>
      {#if isLoading}
        Loading...
      {:else}
        Load More
      {/if}
    </button>
  {:else}
    <p class="end-message">End of List</p>
  {/if}
</div>

<style lang="css">
  @import './LoadmorebuttoninList.css';
</style>