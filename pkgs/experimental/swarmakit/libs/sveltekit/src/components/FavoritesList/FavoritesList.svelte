<script lang="ts">
  import { writable } from 'svelte/store';

  export let items: { id: string; label: string; isFavorite: boolean }[] = [];

  let selectedItemId = writable<string | null>(null);

  const toggleFavorite = (id: string) => {
    items = items.map(item => item.id === id ? { ...item, isFavorite: !item.isFavorite } : item);
  };

  const selectItem = (id: string) => {
    selectedItemId.set(id);
  };
</script>

<ul class="favorites-list">
  {#each items as item (item.id)}
    <li 
      class="list-item" 
      class:selected={item.id === $selectedItemId}
      on:click={() => selectItem(item.id)}
      on:keydown={(e)=>{if(e.key === 'Enter' || e.key === ' ') {selectItem(item.id)}}}
      role="menuitem"
      tabindex='0'
    >
      <span>{item.label}</span>
      <button 
        class="favorite-toggle" 
        aria-label="Toggle Favorite"
        on:click|stopPropagation={() => toggleFavorite(item.id)}
      >
        {item.isFavorite ? '★' : '☆'}
      </button>
    </li>
  {/each}
</ul>

<style lang="css">
  @import './FavoritesList.css';
</style>