<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface Row {
  [key: string]: any;
}

export default defineComponent({
  name: 'DataTable',
  props: {
    columns: {
      type: Array as () => Column[],
      required: true,
    },
    rows: {
      type: Array as () => Row[],
      required: true,
    },
    loading: Boolean,
    pagination: Boolean,
    itemsPerPage: {
      type: Number,
      default: 10,
    },
  },
  setup(props) {
    const currentPage = ref(1);

    const paginatedRows = computed(() => {
      if (!props.pagination) return props.rows;
      const start = (currentPage.value - 1) * props.itemsPerPage;
      const end = currentPage.value * props.itemsPerPage;
      return props.rows.slice(start, end);
    });

    const toggleSort = (columnKey: string) => {
      // Sorting logic
      console.log(columnKey);
    };

    return {
      paginatedRows,
      currentPage,
      toggleSort,
    };
  },
});
</script>

<template>
  <div class="data-table" :aria-busy="loading">
    <table>
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" :style="{ width: column.width, textAlign: column.align }">
            <button v-if="column.sortable" @click="toggleSort(column.key)">{{ column.label }}</button>
            <span v-else>{{ column.label }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in paginatedRows" :key="row.id">
          <td v-for="column in columns" :key="column.key">{{ row[column.key] }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="pagination" class="pagination-controls">
      <button @click="currentPage--" :disabled="currentPage === 1">Previous</button>
      <button @click="currentPage++" :disabled="currentPage * itemsPerPage >= rows.length">Next</button>
    </div>
  </div>
</template>

<style scoped lang="css">
.data-table {
  --table-width: 100%;
  --table-border-color: #ddd;
  --table-header-bg: #f9f9f9;
  --table-header-text-color: #333;
  --table-row-hover-bg: #f1f1f1;
}

table {
  width: var(--table-width);
  border-collapse: collapse;
}

th,
td {
  padding: 8px;
  border: 1px solid var(--table-border-color);
}

th {
  background-color: var(--table-header-bg);
  color: var(--table-header-text-color);
}

tr:hover {
  background-color: var(--table-row-hover-bg);
}

.pagination-controls {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
}
</style>