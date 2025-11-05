<script lang="ts">
  export let items: { id: string; label: string; selected: boolean }[] = [];
  export let disabled: boolean = false;

  const toggleSelect = (id: string) => {
    if (!disabled) {
      items = items.map(item => 
        item.id === id ? { ...item, selected: !item.selected } : item
      );
    }
  };
</script>

<div class="multiselect-list">
  {#each items as { id, label, selected } (id)}
    <div
      class={`list-item ${selected ? 'selected' : ''}`}
      on:click={() => toggleSelect(id)}
      aria-selected={selected}
      aria-disabled={disabled}
      tabindex={disabled ? -1 : 0}
      on:keydown={(e)=>{if (e.key === 'Enter' || e.key === ' '){toggleSelect(id)}}}
      role = "tab"
    >
      {label}
    </div>
  {/each}
</div>

<style lang="css">
  @import './MultiselectList.css';
</style>