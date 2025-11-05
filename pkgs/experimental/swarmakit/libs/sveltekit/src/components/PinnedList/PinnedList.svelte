<script lang="ts">
  type ListItem = {
    id: number;
    text: string;
    pinned: boolean;
  };

  export let items: ListItem[] = [];
  export let selectedItem: number | null = null;

  const togglePin = (id: number) => {
    items = items.map(item => item.id === id ? { ...item, pinned: !item.pinned } : item);
  };

  const selectItem = (id: number) => {
    selectedItem = id;
  };
</script>

<ul class="pinned-list" role="list">
  {#each items as item (item.id)}
    <li
      class="list-item {item.pinned ? 'pinned' : ''} {selectedItem === item.id ? 'selected' : ''}"
      on:click={() => selectItem(item.id)}
      on:keydown={(e)=>{if(e.key === 'Enter' || e.key === ' '){selectItem(item.id)}}}
      aria-selected={selectedItem === item.id}
      tabindex ="0"
      role="tab"
    >
      <span class="item-text">{item.text}</span>
      <button
        class="pin-button"
        on:click|stopPropagation={() => togglePin(item.id)}
        aria-label={item.pinned ? 'Unpin item' : 'Pin item'}
      >
        {item.pinned ? '📌' : '📍'}
      </button>
    </li>
  {/each}
</ul>

<style lang="css">
  @import './PinnedList.css';
</style>