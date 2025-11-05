<script lang="ts">
  import { writable } from 'svelte/store';

  export let items: { id: string; label: string; content: string }[] = [];
  
  let expandedItemId = writable<string | null>(null);
  let selectedItemId = writable<string | null>(null);

  const toggleExpand = (id: string) => {
    expandedItemId.update(current => (current === id ? null : id));
  };

  const selectItem = (id: string) => {
    selectedItemId.set(id);
  };
</script>

<ul class="expandable-list">
  {#each items as item (item.id)}
    <li class="list-item" aria-expanded={item.id === $expandedItemId} on:click={() => toggleExpand(item.id)} role='menuitem' on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { toggleExpand(item.id); }}}
      tabindex="0">
      <div 
        class="item-label"
        class:expanded={item.id === $expandedItemId}
        class:selected={item.id === $selectedItemId}
        on:click={() => selectItem(item.id)}
        on:keydown ={(e)=>{if(e.key === 'Enter' || e.key === ' '){selectItem(item.id)}}}
        role='menuitem'
        tabindex="0"
      >
        {item.label}
      </div>
      {#if item.id === $expandedItemId}
        <div class="item-content">{item.content}</div>
      {/if}
    </li>
  {/each}
</ul>

<style lang="css">
  @import './ExpandableList.css';
</style>