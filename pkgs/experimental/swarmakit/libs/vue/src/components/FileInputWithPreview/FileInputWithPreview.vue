<template>
  <div class="file-input-container">
    <input 
      type="file" 
      :disabled="disabled" 
      @change="handleFileUpload" 
      aria-label="Upload File"
      :aria-disabled="disabled"
    />
    <div v-if="preview" class="preview-container">
      <img :src="preview" alt="File Preview" class="preview-image"/>
    </div>
    <div v-if="error" class="error-message" role="alert">
      {{ error }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'FileInputWithPreview',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const preview = ref<string | null>(null);
    const error = ref<string | null>(null);

    const handleFileUpload = (event: Event) => {
      const input = event.target as HTMLInputElement;
      const file = input.files ? input.files[0] : null;

      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          preview.value = reader.result as string;
          error.value = null;
        };
        reader.onerror = () => {
          error.value = 'Error loading file.';
          preview.value = null;
        };
        reader.readAsDataURL(file);
      }
    };

    return { preview, error, handleFileUpload };
  },
});
</script>

<style scoped lang="css">
@import './FileInputWithPreview.css';
</style>