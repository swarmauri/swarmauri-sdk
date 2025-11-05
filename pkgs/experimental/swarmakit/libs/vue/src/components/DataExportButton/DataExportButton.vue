<script lang="ts">
import { defineComponent, ref } from 'vue';

type ExportFormat = 'csv' | 'excel' | 'pdf';

export default defineComponent({
  name: 'DataExportButton',
  props: {
    availableFormats: {
      type: Array as () => ExportFormat[],
      default: () => ['csv', 'excel', 'pdf'],
    },
    dataAvailable: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const isExporting = ref(false);

    const startExport = async (format: ExportFormat) => {
      if (!props.dataAvailable || isExporting.value) return;
      console.log(format);
      
      isExporting.value = true;
      try {
        // Simulate data export process
        await new Promise(resolve => setTimeout(resolve, 2000));
      } finally {
        isExporting.value = false;
      }
    };

    return {
      isExporting,
      startExport,
    };
  },
});
</script>

<template>
  <div class="data-export-button">
    <button 
      v-for="format in availableFormats" 
      :key="format" 
      @click="startExport(format)" 
      :disabled="!dataAvailable || isExporting"
    >
      Export as {{ format.toUpperCase() }}
    </button>
    <div v-if="isExporting" class="loading-indicator">Exporting...</div>
  </div>
</template>

<style scoped lang="css">
.data-export-button {
  --button-bg: #28a745;
  --button-color: #ffffff;
  --button-disabled-bg: #d6d6d6;
  --button-disabled-color: #8a8a8a;
  --loading-color: #007bff;
}

button {
  background-color: var(--button-bg);
  color: var(--button-color);
  border: none;
  padding: 10px 20px;
  margin: 5px;
  cursor: pointer;
}

button:disabled {
  background-color: var(--button-disabled-bg);
  color: var(--button-disabled-color);
  cursor: not-allowed;
}

.loading-indicator {
  color: var(--loading-color);
  margin-top: 10px;
}
</style>