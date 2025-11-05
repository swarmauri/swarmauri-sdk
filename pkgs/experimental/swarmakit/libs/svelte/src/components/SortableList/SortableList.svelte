<script lang="ts">
  import { onMount } from 'svelte';

  export let items: string[] = [];
  export let disabled = false;

  let draggingIndex: number | null = null;
  let dragOverIndex: number | null = null;

  onMount(() => {
    if (disabled) {
      document.querySelectorAll('.sortable-item').forEach((item) => {
        item.setAttribute('draggable', 'false');
      });
    }
  });

  function handleDragStart(event: DragEvent, index: number) {
    if (disabled) return;
    draggingIndex = index;
    event.dataTransfer?.setData('text/plain', String(index));
  }

  function handleDragOver(event: DragEvent, index: number) {
    event.preventDefault();
    if (disabled || index === draggingIndex) return;
    dragOverIndex = index;
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    if (disabled || draggingIndex === null || dragOverIndex === null) return;
    const item = items.splice(draggingIndex, 1)[0];
    items.splice(dragOverIndex, 0, item);
    draggingIndex = null;
    dragOverIndex = null;
  }
</script>

<ul class="sortable-list">
  {#each items as item, index}
    <li
      class="sortable-item"
      draggable={!disabled}
      on:dragstart={(event) => handleDragStart(event, index)}
      on:dragover={(event) => handleDragOver(event, index)}
      on:drop={handleDrop}
      tabindex="0"
      role="menuitem"
      aria-grabbed={draggingIndex === index ? 'true' : 'false'}
      aria-disabled={disabled}
    >
      {item}
    </li>
  {/each}
</ul>

<style lang="css">
  @import './SortableList.css';
</style>