<script context="module" lang="ts">
  export type TableColumn = {
    key: string;
    label: string;
    sortable?: boolean;
  };

  export type TableRow = {
    [key: string]: string | number | boolean;
  };
</script>


<script lang="ts">
  import { writable } from 'svelte/store';

  export let columns: TableColumn[] = [];
  export let rows: TableRow[] = [];

  const selectedRow = writable<TableRow | null>(null);
  let filterText = '';
  let sortKey = '';
  let sortOrder: 'asc' | 'desc' = 'asc';

  function sortRows(key: string) {
    if (sortKey === key) {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      sortKey = key;
      sortOrder = 'asc';
    }
    rows = [...rows].sort((a, b) => {
      if (a[key] < b[key]) return sortOrder === 'asc' ? -1 : 1;
      if (a[key] > b[key]) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

  function filterRows() {
    return rows.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(filterText.toLowerCase())
      )
    );
  }

  function selectRow(row: TableRow) {
    selectedRow.set(row);
  }
</script>

<div class="filter">
  <input
    type="text"
    placeholder="Filter..."
    bind:value={filterText}
    on:input={() => filterRows()}
    aria-label="Filter rows"
  />
</div>
<table class="sortable-table">
  <thead>
    <tr>
      {#each columns as column}
        <th
          on:click={() => column.sortable && sortRows(column.key)}
          on:keydown={(e) => e.key === "Enter" && column.sortable && sortRows(column.key)}
          tabindex="0"
          aria-sort={sortKey === column.key ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
          role="columnheader"
          class:sortable={column.sortable}
        >
          {column.label} {#if column.sortable && sortKey === column.key}{sortOrder === 'asc' ? '↑' : '↓'}{/if}
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each filterRows() as row (row.id)}
      <tr
        on:click={() => selectRow(row)}
        on:keydown={(e) => e.key === "Enter" && selectRow(row)}
        tabindex="0"
      >
        {#each columns as column}
          <td role="cell">{row[column.key]}</td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<style lang="css">
  @import './SortableTable.css';
</style>