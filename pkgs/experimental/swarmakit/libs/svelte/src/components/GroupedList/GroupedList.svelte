<script lang="ts">
  import { writable } from 'svelte/store';

  interface Group {
    title: string;
    items: string[];
    expanded?: boolean;
  }

  export let groups: Group[] = [];
  let selectedItem: string | null = null;

  const toggleGroup = (group: Group) => {
    group.expanded = !group.expanded;
  };

  const selectItem = (item: string) => {
    selectedItem = item;
  };
</script>

<div class="grouped-list">
  {#each groups as group (group.title)}
    <div class="group">
      <button on:click={() => toggleGroup(group)} aria-expanded={group.expanded} aria-controls={group.title}>
        {group.title}
      </button>
      {#if group.expanded}
        <ul id={group.title}>
          {#each group.items as item (item)}
            <li 
              class:selected={selectedItem === item} 
              on:click={() => selectItem(item)} 
              on:keydown={(e)=>{if(e.key === 'Enter' || e.key === ' '){selectItem(item)}}}
              on:mouseover={() => selectItem(item)}
              on:focus= {()=> selectItem(item)}
              role='menuitem'>
              {item}
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  {/each}
</div>

<style lang="css">
  @import './GroupedList.css';
</style>