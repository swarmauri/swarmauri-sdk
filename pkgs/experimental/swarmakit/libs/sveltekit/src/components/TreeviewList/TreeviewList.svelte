<script lang="ts">
  import TreeviewList from './TreeviewList.svelte';

  export let nodes: { label: string, children?: any[], expanded: boolean, selected: boolean }[] = [];

  function toggleNode(index: number) {
    nodes = nodes.map((node, i) => ({
      ...node,
      expanded: i === index ? !node.expanded : node.expanded
    }));
  }

  function selectNode(index: number) {
    nodes = nodes.map((node, i) => ({
      ...node,
      selected: i === index ? true : false
    }));
  }
</script>

<ul class="treeview" role="tree">
  {#each nodes as { label, children, expanded, selected }, index}
    <li class="tree-node">
      <div
        class="node-content"
        class:expanded={expanded}
        class:selected={selected}
        role="treeitem"
        aria-expanded={expanded} 
        tabindex="0" 
        aria-selected={selected}
        on:click={() => toggleNode(index)}
        on:keydown={(event) => event.key === 'Enter' && toggleNode(index)}
      >
        <span role="treeitem" aria-expanded={expanded} tabindex="0" aria-selected={selected} on:click={() => selectNode(index)} on:keydown={(event) => event.key === ' ' && selectNode(index)}>{label}</span>
      </div>
      {#if expanded && children}
        <ul role="group">
          {#each children as child}
            <TreeviewList nodes={[child]} />
          {/each}
        </ul>
      {/if}
    </li>
  {/each}
</ul>

<style lang="css">
  @import './TreeviewList.css';
</style>