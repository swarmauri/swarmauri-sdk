<script lang="ts">
  export let totalItems: number = 0;
  export let itemsPerPage: number = 10;
  export let currentPage: number = 1;

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const setPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
    }
  };
</script>

<nav class="pagination" aria-label="Pagination Navigation">
  <button
    class="page-button"
    on:click={() => setPage(currentPage - 1)}
    aria-disabled={currentPage === 1}
    disabled={currentPage === 1}
  >
    Previous
  </button>
  {#each Array(totalPages) as _, index}
    <button
      class="page-button {currentPage === index + 1 ? 'active' : ''}"
      on:click={() => setPage(index + 1)}
      aria-current={currentPage === index + 1 ? 'page' : undefined}
    >
      {index + 1}
    </button>
  {/each}
  <button
    class="page-button"
    on:click={() => setPage(currentPage + 1)}
    aria-disabled={currentPage === totalPages}
    disabled={currentPage === totalPages}
  >
    Next
  </button>
</nav>

<style lang="css">
  @import './Pagination.css';
</style>