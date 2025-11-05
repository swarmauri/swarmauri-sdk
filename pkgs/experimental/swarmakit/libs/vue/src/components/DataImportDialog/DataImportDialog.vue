<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'DataImportDialog',
  setup() {
    const file = ref<File | null>(null);
    const importing = ref(false);
    const success = ref(false);
    const error = ref<string | null>(null);

    const onFileChange = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files) {
        file.value = target.files[0];
      }
    };

    const importData = async () => {
      if (!file.value) {
        error.value = 'No file selected';
        return;
      }

      importing.value = true;
      error.value = null;

      try {
        // Simulate data import
        await new Promise((resolve) => setTimeout(resolve, 2000));
        success.value = true;
      } catch (e) {
        error.value = 'Import failed';
      } finally {
        importing.value = false;
      }
    };

    return {
      file,
      importing,
      success,
      error,
      onFileChange,
      importData,
    };
  },
});
</script>

<template>
  <div class="data-import-dialog" role="dialog" aria-labelledby="dialog-title">
    <h2 id="dialog-title">Import Data</h2>
    <input type="file" @change="onFileChange" accept=".csv, .xls, .xlsx" aria-label="File upload" />
    <button @click="importData" :disabled="importing || !file">
      Import
    </button>
    <div v-if="importing" class="progress-indicator" aria-live="polite">
      Importing...
    </div>
    <div v-if="success" class="success-message" aria-live="polite">
      Import successful!
    </div>
    <div v-if="error" class="error-message" aria-live="assertive">
      {{ error }}
    </div>
  </div>
</template>

<style scoped lang="css">
.data-import-dialog {
  padding: 16px;
  background-color: var(--dialog-bg);
}

input[type="file"] {
  margin-bottom: 12px;
}

button {
  padding: 8px 16px;
  background-color: var(--button-bg);
  color: var(--button-color);
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:disabled {
  background-color: var(--button-disabled-bg);
  cursor: not-allowed;
}

.progress-indicator,
.success-message,
.error-message {
  margin-top: 12px;
}
</style>