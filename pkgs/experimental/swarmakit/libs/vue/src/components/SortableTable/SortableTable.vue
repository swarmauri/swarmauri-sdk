<template>
  <div class="sortable-table">
    <input 
      type="text" 
      v-model="filterText" 
      class="filter-input" 
      placeholder="Filter table..."
      aria-label="Filter table"
    />
    <table>
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" @click="sortBy(column.key)">
            {{ column.label }}
            <span :class="getSortDirection(column.key)"></span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="row in filteredAndSortedData" 
          :key="row.id" 
          :class="{ selected: row.id === selectedRow }" 
          @click="selectRow(row.id)"
        >
          <td v-for="column in columns" :key="column.key">{{ row[column.key] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

interface TableColumn {
  key: string;
  label: string;
}

interface TableRow {
  id: number;
  [key: string]: any;
}

export default defineComponent({
  name: 'SortableTable',
  props: {
    columns: {
      type: Array as () => TableColumn[],
      required: true,
    },
    data: {
      type: Array as () => TableRow[],
      required: true,
    },
  },
  setup(props) {
    const sortKey = ref<string | null>(null);
    const sortDirection = ref<1 | -1 | number>(1);
    const filterText = ref<string>("");
    const selectedRow = ref<number | null>(null);

    const sortBy = (key: string) => {
      if (sortKey.value === key) {
        sortDirection.value = -sortDirection.value;
      } else {
        sortKey.value = key;
        sortDirection.value = 1;
      }
    };

    const selectRow = (id: number) => {
      selectedRow.value = selectedRow.value === id ? null : id;
    };

    const getSortDirection = (key: string) => {
      if (sortKey.value === key) {
        return sortDirection.value === 1 ? 'asc' : 'desc';
      }
      return '';
    };

    const filteredAndSortedData = computed(() => {
      let filteredData = props.data.filter(row => 
        Object.values(row).some(val => val.toString().toLowerCase().includes(filterText.value.toLowerCase()))
      );

      if (sortKey.value) {
        filteredData.sort((a, b) => {
          const aValue = a[sortKey.value!];
          const bValue = b[sortKey.value!];
          if (aValue < bValue) return -1 * sortDirection.value;
          if (aValue > bValue) return 1 * sortDirection.value;
          return 0;
        });
      }

      return filteredData;
    });

    return { sortBy, selectRow, getSortDirection, filteredAndSortedData, filterText, selectedRow };
  },
});
</script>

<style scoped lang="css">
.sortable-table {
  --table-border: 1px solid #ccc;
  --selected-row-bg: #f0f8ff;
  --table-row-hover-bg: #f5f5f5;
  --sort-icon-color: #007bff;
  --filter-input-border: 1px solid #ddd;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 8px 12px;
  border: var(--table-border);
  text-align: left;
  cursor: pointer;
}

th {
  position: relative;
}

th span {
  position: absolute;
  right: 10px;
  color: var(--sort-icon-color);
}

th span.asc::after {
  content: '▲';
}

th span.desc::after {
  content: '▼';
}

tr:hover {
  background-color: var(--table-row-hover-bg);
}

tr.selected {
  background-color: var(--selected-row-bg);
}

.filter-input {
  margin-bottom: 10px;
  padding: 6px;
  border: var(--filter-input-border);
  width: 100%;
  box-sizing: border-box;
}
</style>