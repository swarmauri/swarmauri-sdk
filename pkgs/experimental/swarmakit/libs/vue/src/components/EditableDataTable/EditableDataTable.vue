<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

interface Column {
  key: string;
  label: string;
  editable?: boolean;
  multiline?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface Row {
  [key: string]: any;
}

export default defineComponent({
  name: 'EditableDataTable',
  props: {
    columns: {
      type: Array as () => Column[],
      required: true,
    },
    rows: {
      type: Array as () => Row[],
      required: true,
    },
    pagination: Boolean,
    itemsPerPage: {
      type: Number,
      default: 10,
    },
  },
  setup(props) {
    const currentPage = ref(1);
    const editingRow = ref<number | null>(null);
    const editedRows = ref<Row[]>([...props.rows]);

    const paginatedRows = computed(() => {
      if (!props.pagination) return editedRows.value;
      const start = (currentPage.value - 1) * props.itemsPerPage;
      const end = currentPage.value * props.itemsPerPage;
      return editedRows.value.slice(start, end);
    });

    const toggleEditRow = (index: number) => {
      editingRow.value = editingRow.value === index ? null : index;
    };

    const saveRow = (index: number) => {
      // Implement save logic
      toggleEditRow(index);
    };

    const deleteRow = (index: number) => {
      editedRows.value.splice(index, 1);
    };

    return {
      paginatedRows,
      currentPage,
      editingRow,
      toggleEditRow,
      saveRow,
      deleteRow,
      editedRows,
    };
  },
});
</script>

<template>
  <div class="editable-data-table">
    <table>
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" :style="{ width: column.width, textAlign: column.align }">
            {{ column.label }}
          </th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in paginatedRows" :key="row.id" :class="{ editing: editingRow === rowIndex }">
          <td v-for="column in columns" :key="column.key">
            <div v-if="editingRow === rowIndex && column.editable">
              <input v-if="!column.multiline" type="text" v-model="row[column.key]" />
              <textarea v-else v-model="row[column.key]"></textarea>
            </div>
            <div v-else>{{ row[column.key] }}</div>
          </td>
          <td>
            <button @click="toggleEditRow(rowIndex)" v-if="editingRow !== rowIndex">Edit</button>
            <button @click="saveRow(rowIndex)" v-if="editingRow === rowIndex">Save</button>
            <button @click="deleteRow(rowIndex)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="pagination" class="pagination-controls">
      <button @click="currentPage--" :disabled="currentPage === 1">Previous</button>
      <button @click="currentPage++" :disabled="currentPage * itemsPerPage >= editedRows.length">Next</button>
    </div>
  </div>
</template>

<style scoped lang="css">
.editable-data-table {
  --table-width: 100%;
  --table-border-color: #ddd;
  --table-header-bg: #f9f9f9;
  --table-header-text-color: #333;
  --table-row-hover-bg: #f1f1f1;
  --table-row-editing-bg: #e0f7fa;
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

tr.editing {
  background-color: var(--table-row-editing-bg);
}

.pagination-controls {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
}
</style>