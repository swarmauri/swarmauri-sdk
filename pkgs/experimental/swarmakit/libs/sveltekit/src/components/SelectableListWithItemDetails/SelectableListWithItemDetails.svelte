<script lang="ts">
  type ListItem = {
    id: number;
    text: string;
    details: string;
  };

  export let items: ListItem[] = [];
  export let selectedItemId: number | null = null;
  export let detailsOpen: boolean = false;

  const toggleSelection = (itemId: number) => {
    selectedItemId = selectedItemId === itemId ? null : itemId;
    detailsOpen = selectedItemId === itemId;
  };

  const toggleDetails = () => {
    detailsOpen = !detailsOpen;
  };
</script>

<div class="selectable-list" role="list">
  {#each items as item (item.id)}
    <div
      class="list-item {selectedItemId === item.id ? 'selected' : ''}"
      on:click={() => toggleSelection(item.id)}
      on:keydown={(e)=>{if(e.key === 'Enter' || e.key === ' '){toggleSelection(item.id)}}}
      role="menuitem"
      aria-current={selectedItemId === item.id}
      tabindex="0"
    >
      {item.text}
      {#if selectedItemId === item.id && detailsOpen}
        <div class="item-details">{item.details}</div>
      {/if}
    </div>
  {/each}
</div>

<style lang="css">
  @import './SelectableListWithItemDetails.css';
</style>