<script lang="ts">
  export let items: { id: string; label: string; selected: boolean }[] = [];
  export let disabled: boolean = false;

  const handleSelect = (id: string) => {
    if (!disabled) {
      items = items.map(item =>
        item.id === id ? { ...item, selected: !item.selected } : item
      );
    }
  };
</script>

<ol class="numbered-list">
  {#each items as { id, label, selected } (id)}
    <li
      class={`list-item ${selected ? 'selected' : ''}`}
      on:click={() => handleSelect(id)}
      aria-selected={selected}
      aria-disabled={disabled}
      tabindex={disabled ? -1 : 0}
      on:keydown={(e)=>{if(e.key === 'Enter' || e.key === ' '){handleSelect(id)}}}
      role="tab"
    >
      {label}
    </li>
  {/each}
</ol>

<style lang="css">
  @import './NumberedList.css';
</style>