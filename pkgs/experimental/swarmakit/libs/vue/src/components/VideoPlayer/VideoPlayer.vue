<template>
  <div class="video-player" role="region" aria-label="Video Player">
    <video
      ref="videoElement"
      :src="videoSrc"
      @play="onPlay"
      @pause="onPause"
      @waiting="onBuffering"
      @fullscreenchange="onFullscreenChange"
      controls
      class="video-element"
    ></video>
    <div class="controls">
      <button @click="togglePlayPause" aria-label="Play/Pause" class="control-btn">
        {{ isPlaying ? 'Pause' : 'Play' }}
      </button>
      <button @click="toggleFullscreen" aria-label="Fullscreen" class="control-btn">
        {{ isFullscreen ? 'Exit Fullscreen' : 'Fullscreen' }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';

export default defineComponent({
  name: 'VideoPlayer',
  props: {
    videoSrc: {
      type: String,
      required: true,
    },
  },
  setup() {
    const isPlaying = ref(false);
    const isFullscreen = ref(false);
    const videoElement = ref<HTMLVideoElement | null>(null);

    onMounted(() => {
      if (videoElement.value) {
        videoElement.value.controls = false;
      }
    });

    const togglePlayPause = () => {
      if (videoElement.value) {
        if (videoElement.value.paused) {
          videoElement.value.play();
        } else {
          videoElement.value.pause();
        }
      }
    };

    const toggleFullscreen = () => {
      if (videoElement.value) {
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          videoElement.value.requestFullscreen();
        }
      }
    };

    const onPlay = () => {
      isPlaying.value = true;
    };

    const onPause = () => {
      isPlaying.value = false;
    };

    const onBuffering = () => {
      isPlaying.value = false;
    };

    const onFullscreenChange = () => {
      isFullscreen.value = !!document.fullscreenElement;
    };

    return {
      isPlaying,
      isFullscreen,
      videoElement,
      togglePlayPause,
      toggleFullscreen,
      onPlay,
      onPause,
      onBuffering,
      onFullscreenChange,
    };
  },
});
</script>

<style scoped lang="css">
.video-player {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--player-bg-color);
}

.video-element {
  width: 100%;
  display: block;
}

.controls {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.control-btn {
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  margin: 0 0.5rem;
  cursor: pointer;
}
</style>