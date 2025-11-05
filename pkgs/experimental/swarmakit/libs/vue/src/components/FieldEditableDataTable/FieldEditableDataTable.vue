<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';

interface TableData {
  [key: string]: string;
}

export default defineComponent({
  name: 'FieldEditableDataTable',
  setup() {
    const data = reactive<TableData[]>([
      { id: '1', name: 'John Doe', description: 'A short note' },
      { id: '2', name: 'Jane Smith', description: 'Another note' },
    ]);

    const editingField = ref<{ rowId: string; field: string } | null>(null);
    const fieldValues = reactive<{ [key: string]: string }>({});
    const error = ref<string | null>(null);

    const editField = (rowId: string, field: string) => {
      editingField.value = { rowId, field };
      fieldValues[field] = data.find((row) => row.id === rowId)?.[field] || '';
    };

    const saveField = () => {
      if (!editingField.value) return;

      const { rowId, field } = editingField.value;
      const row = data.find((row) => row.id === rowId);

      if (!row) {
        error.value = 'Row not found';
        return;
      }

      row[field] = fieldValues[field];
      error.value = null;
      editingField.value = null;
    };

    const discardChanges = () => {
      editingField.value = null;
      error.value = null;
    };

    return {
      data,
      editingField,
      fieldValues,
      error,
      editField,
      saveField,
      discardChanges,
    };
  },
});
</script>

<template>
  <div class="field-editable-data-table" role="table">
    <div role="row" v-for="(row) in data" :key="row.id" class="table-row">
      <div role="cell" class="table-cell" v-for="(value, key) in row" :key="key">
        <template v-if="editingField && editingField.rowId === row.id && editingField.field === key">
          <textarea v-if="key === 'description'" v-model="fieldValues[key]" aria-label="Edit description"></textarea>
          <input v-else type="text" v-model="fieldValues[key]" aria-label="Edit field" />
          <button @click="saveField">Save</button>
          <button @click="discardChanges">Cancel</button>
        </template>
        <template v-else>
          <span @click="editField(row.id, key.toString())" class="editable-field">{{ value }}</span>
        </template>
      </div>
    </div>
    <div v-if="error" class="error-message" aria-live="assertive">{{ error }}</div>
  </div>
</template>

<style scoped lang="css">
.field-editable-data-table {
  width: 100%;
  border-collapse: collapse;
}

.table-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.table-cell {
  display: flex;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid var(--table-border);
}

.editable-field {
  cursor: pointer;
  padding: 4px;
  transition: background-color 0.3s ease;
}

.editable-field:hover {
  background-color: var(--field-hover-bg);
}

textarea,
input[type="text"] {
  width: 100%;
  padding: 4px;
  margin-right: 8px;
}

button {
  padding: 4px 8px;
  margin-left: 4px;
}

.error-message {
  color: var(--error-color);
  margin-top: 12px;
}
</style>