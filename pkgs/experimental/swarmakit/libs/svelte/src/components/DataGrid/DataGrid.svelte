<script lang="ts">
  import { onMount } from 'svelte';

  export let columns: { id: string; label: string }[] = [];
  export let rows: { [key: string]: string | number }[] = [];
  export let pageSize: number = 10;
  export let searchQuery: string = '';
  export let resizable: boolean = false;
  
  let currentPage: number = 0;
  let filteredRows = rows;

  const filterRows = () => {
    filteredRows = rows.filter(row =>
      Object.values(row).some(value => value.toString().toLowerCase().includes(searchQuery.toLowerCase()))
    );
  };

  const nextPage = () => {
    if ((currentPage + 1) * pageSize < filteredRows.length) {
      currentPage += 1;
    }
  };

  const previousPage = () => {
    if (currentPage > 0) {
      currentPage -= 1;
    }
  };

  onMount(filterRows);
</script>

<div class="data-grid">
  {#if searchQuery}
    <input type="text" bind:value={searchQuery} on:input={filterRows} placeholder="Search..." />
  {/if}

  <table class:resizable={resizable}>
    <thead>
      <tr>
        {#each columns as column}
          <th>{column.label}</th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each filteredRows.slice(currentPage * pageSize, (currentPage + 1) * pageSize) as row}
        <tr>
          {#each columns as column}
            <td>{row[column.id]}</td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>

  {#if pageSize < rows.length}
    <div class="pagination">
      <button on:click={previousPage} disabled={currentPage === 0}>Previous</button>
      <button on:click={nextPage} disabled={(currentPage + 1) * pageSize >= filteredRows.length}>Next</button>
    </div>
  {/if}
</div>

<style lang="css">
  @import './DataGrid.css';
</style>