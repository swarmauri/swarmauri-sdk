<template>
  <div class="video-container" role="region" aria-label="Video Player">
    <video
      ref="videoElement"
      :src="videoSrc"
      @play="onPlay"
      @pause="onPause"
      controls
      class="video-element"
    ></video>
    <div class="status" aria-live="polite">
      <span v-if="isUploading" class="status-text">Uploading...</span>
      <span v-if="isPaused" class="status-text">Paused</span>
      <span v-if="isCompleted" class="status-text">Completed</span>
      <span v-if="isError" class="status-text">Error</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Video',
  props: {
    videoSrc: {
      type: String,
      required: true,
    },
    initialState: {
      type: String as () => 'uploading' | 'paused' | 'completed' | 'error',
      default: 'paused',
    },
  },
  setup(props) {
    const isUploading = ref(props.initialState === 'uploading');
    const isPaused = ref(props.initialState === 'paused');
    const isCompleted = ref(props.initialState === 'completed');
    const isError = ref(props.initialState === 'error');
    const videoElement = ref<HTMLVideoElement | null>(null);

    const onPlay = () => {
      isPaused.value = false;
    };

    const onPause = () => {
      isPaused.value = true;
    };

    return {
      isUploading,
      isPaused,
      isCompleted,
      isError,
      videoElement,
      onPlay,
      onPause,
    };
  },
});
</script>

<style scoped lang="css">
.video-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--video-bg-color);
}

.video-element {
  width: 100%;
  display: block;
}

.status {
  text-align: center;
  margin-top: 1rem;
}

.status-text {
  color: var(--status-text-color);
}
</style>