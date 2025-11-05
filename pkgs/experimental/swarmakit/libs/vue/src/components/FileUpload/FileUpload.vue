<template>
  <div 
    class="file-upload-container" 
    :class="{ 'drag-over': isDragOver }" 
    @dragover.prevent="handleDragOver" 
    @dragleave.prevent="handleDragLeave" 
    @drop.prevent="handleDrop"
  >
    <input 
      type="file" 
      :multiple="multiple" 
      @change="handleFileSelect" 
      aria-label="Upload File(s)"
    />
    <div v-if="progress" class="progress-bar" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100">
      <div class="progress" :style="{ width: progress + '%' }"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'FileUpload',
  props: {
    multiple: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const isDragOver = ref(false);
    const progress = ref<number | null>(null);

    const handleFileSelect = (event: Event) => {
      const input = event.target as HTMLInputElement;
      const files = input.files;
      if (files) {
        // Process files
      }
    };

    const handleDragOver = () => {
      isDragOver.value = true;
    };

    const handleDragLeave = () => {
      isDragOver.value = false;
    };

    const handleDrop = (event: DragEvent) => {
      isDragOver.value = false;
      const files = event.dataTransfer?.files;
      if (files) {
        // Process files
      }
    };

    return { isDragOver, progress, handleFileSelect, handleDragOver, handleDragLeave, handleDrop };
  },
});
</script>

<style scoped lang="css">
@import './FileUpload.css';
</style>