<script lang="ts">
  export let items: { id: number; label: string; checked?: boolean; partiallyChecked?: boolean; disabled?: boolean }[] = [];

  const toggleCheck = (item: { id: number; label: string; checked?: boolean; partiallyChecked?: boolean; disabled?: boolean }) => {
    if (!item.disabled) {
      if (item.partiallyChecked) {
        item.partiallyChecked = false;
        item.checked = true;
      } else {
        item.checked = !item.checked;
      }
    }
  };
</script>

<ul class="checklist">
  {#each items as item (item.id)}
    <li 
      class="checklist-item {item.checked ? 'checked' : ''} {item.partiallyChecked ? 'partially-checked' : ''} {item.disabled ? 'disabled' : ''}"
    >
      <input 
        type="checkbox" 
        bind:checked={item.checked} 
        on:change={() => toggleCheck(item)} 
        disabled={item.disabled}
        aria-checked={item.partiallyChecked ? 'mixed' : item.checked}
        id={`checkbox-${item.id}`}
      />
      <label for={`checkbox-${item.id}`}>{item.label}</label>
    </li>
  {/each}
</ul>

<style lang="css">
  @import './CheckList.css';
</style>