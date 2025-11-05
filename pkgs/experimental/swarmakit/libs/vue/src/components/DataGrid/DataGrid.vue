<template>
  <div class="data-grid" role="grid">
    <div class="search-bar" v-if="searchEnabled">
      <input type="text" v-model="searchQuery" placeholder="Search..." aria-label="Search Data Grid" />
    </div>
    <table>
      <thead>
        <tr>
          <th v-for="(header, index) in headers" :key="index" :style="{ width: resizable ? 'auto' : 'initial' }">
            {{ header }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in filteredData" :key="rowIndex">
          <td v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</td>
        </tr>
      </tbody>
    </table>
    <div class="pagination" v-if="paginationEnabled">
      <button @click="prevPage" :disabled="page === 1" aria-label="Previous Page">Previous</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="page === totalPages" aria-label="Next Page">Next</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'DataGrid',
  props: {
    headers: {
      type: Array as () => string[],
      required: true,
    },
    data: {
      type: Array as () => Array<Array<string>>,
      required: true,
    },
    paginationEnabled: {
      type: Boolean,
      default: false,
    },
    searchEnabled: {
      type: Boolean,
      default: false,
    },
    resizable: {
      type: Boolean,
      default: false,
    },
    itemsPerPage: {
      type: Number,
      default: 10,
    },
  },
  setup(props) {
    const page = ref(1);
    const searchQuery = ref('');

    const filteredData = computed(() => {
      let filtered = props.data;
      if (props.searchEnabled && searchQuery.value) {
        filtered = filtered.filter(row =>
          row.some(cell => cell.toLowerCase().includes(searchQuery.value.toLowerCase()))
        );
      }
      if (props.paginationEnabled) {
        const start = (page.value - 1) * props.itemsPerPage;
        return filtered.slice(start, start + props.itemsPerPage);
      }
      return filtered;
    });

    const totalPages = computed(() => Math.ceil(props.data.length / props.itemsPerPage));

    const prevPage = () => {
      if (page.value > 1) page.value -= 1;
    };

    const nextPage = () => {
      if (page.value < totalPages.value) page.value += 1;
    };

    return { page, searchQuery, filteredData, totalPages, prevPage, nextPage };
  },
});
</script>

<style scoped lang="css">
.data-grid {
  overflow-x: auto;
}

.search-bar {
  margin-bottom: var(--search-bar-margin-bottom, 10px);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: var(--cell-padding, 10px);
  border: var(--cell-border, 1px solid #ccc);
  text-align: left;
}

.pagination {
  display: flex;
  justify-content: space-between;
  margin-top: var(--pagination-margin-top, 10px);
}
</style>