<script>
  export let tile = {};

  $: props = tile?.props ?? {};
  $: columns = Array.isArray(props.columns) ? props.columns : [];
  $: rows = Array.isArray(props.rows) ? props.rows : [];
</script>

<div class="table-card">
  <h3 class="table-card__title">{props.label ?? "Details"}</h3>
  <table class="table-card__table">
    <thead>
      <tr>
        {#each columns as column (column.key ?? column.name)}
          <th>{column.name ?? column.key}</th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each rows as row, rowIndex}
        <tr>
          {#each columns as column (column.key ?? column.name)}
            <td>{row?.[column.key] ?? "—"}</td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
