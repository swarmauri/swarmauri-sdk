<template>
  <div class="upload" :class="status">
    <span>{{ message }}</span>
    <progress v-if="progressVisible" :value="progress" max="100"></progress>
    <button v-if="showCancelButton" @click="cancelUpload" class="cancel-btn" aria-label="Cancel Upload">
      Cancel
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Upload',
  props: {
    message: {
      type: String,
      required: true,
    },
    status: {
      type: String as () => 'uploading' | 'downloading' | 'completed' | 'paused' | 'failed',
      required: true,
    },
    progress: {
      type: Number,
      default: 0,
    },
  },
  setup(props) {
    const progressVisible = ref(props.status === 'uploading' || props.status === 'downloading');
    const showCancelButton = ref(props.status === 'uploading');

    const cancelUpload = () => {
      console.log('Upload cancelled.');
    };

    return { progressVisible, showCancelButton, cancelUpload };
  },
});
</script>

<style scoped lang="css">
.upload {
  padding: var(--upload-padding, 16px);
  border-radius: var(--upload-border-radius, 4px);
  margin-bottom: var(--upload-margin-bottom, 16px);
  display: flex;
  flex-direction: column;
  gap: var(--upload-gap, 8px);
}

.upload.uploading {
  background-color: var(--upload-uploading-bg, #e0f7fa);
  color: var(--upload-uploading-color, #00796b);
}

.upload.downloading {
  background-color: var(--upload-downloading-bg, #e3f2fd);
  color: var(--upload-downloading-color, #1976d2);
}

.upload.completed {
  background-color: var(--upload-completed-bg, #e8f5e9);
  color: var(--upload-completed-color, #388e3c);
}

.upload.paused {
  background-color: var(--upload-paused-bg, #fff3e0);
  color: var(--upload-paused-color, #f57c00);
}

.upload.failed {
  background-color: var(--upload-failed-bg, #ffebee);
  color: var(--upload-failed-color, #d32f2f);
}

.cancel-btn {
  background: none;
  border: none;
  font-size: var(--cancel-btn-font-size, 16px);
  cursor: pointer;
  color: inherit;
}
</style>