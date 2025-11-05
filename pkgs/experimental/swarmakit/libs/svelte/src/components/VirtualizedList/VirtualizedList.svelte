<script lang="ts">
  import { onMount } from 'svelte';

  export let items: string[] = [];
  export let isLoading: boolean = false;
  export let hasMore: boolean = true;
  export let loadMore: () => void;

  let observer: IntersectionObserver;

  onMount(() => {
    const lastItem = document.querySelector('.list-end');
    if (lastItem) {
      observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting && hasMore && !isLoading) {
            loadMore();
          }
        });
      });
      observer.observe(lastItem);
    }

    return () => {
      if (observer) {
        observer.disconnect();
      }
    };
  });
</script>

<ul class="virtualized-list" role="list">
  {#each items as item}
    <li class="list-item" role="listitem">{item}</li>
  {/each}
  <li class="list-end" aria-hidden="true"></li>
  {#if isLoading}
    <li role="alert">Loading...</li>
  {/if}
  {#if !hasMore && !isLoading}
    <li role="status">End of List</li>
  {/if}
</ul>

<style lang="css">
  @import './VirtualizedList.css';
</style>