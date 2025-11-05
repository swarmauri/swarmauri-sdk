<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let items: { id: number; label: string; actionTriggered?: boolean }[] = [];
  export let visible: boolean = true;
  
  const dispatch = createEventDispatcher();

  const triggerAction = (item: { id: number; label: string; actionTriggered?: boolean }) => {
    item.actionTriggered = true;
    dispatch('action', { item });
  };

  const dismiss = () => {
    visible = false;
    dispatch('dismiss');
  };
</script>

{#if visible}
  <ul class="contextual-list">
    {#each items as item (item.id)}
      <li class="list-item {item.actionTriggered ? 'action-triggered' : ''}">
        {item.label}
        <button on:click={() => triggerAction(item)}>Trigger Action</button>
      </li>
    {/each}
    <li>
      <button on:click={dismiss}>Dismiss</button>
    </li>
  </ul>
{/if}

<style lang="css">
  @import './ContextualList.css';
</style>