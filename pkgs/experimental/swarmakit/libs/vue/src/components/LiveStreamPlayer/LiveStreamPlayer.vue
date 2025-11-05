<template>
  <div class="live-stream-player" role="region" aria-label="Live Stream Player">
    <video
      ref="videoElement"
      :src="streamSrc"
      @play="onPlay"
      @pause="onPause"
      @waiting="onBuffering"
      @volumechange="onVolumeChange"
      controls
    ></video>
    <div v-if="buffering" class="buffering-overlay">Buffering...</div>
    <button @click="toggleMute" aria-label="Toggle Mute" class="mute-btn">
      {{ muted ? 'Unmute' : 'Mute' }}
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'LiveStreamPlayer',
  props: {
    streamSrc: {
      type: String,
      required: true,
    },
  },
  setup() {
    const videoElement = ref<HTMLVideoElement | null>(null);
    const muted = ref(false);
    const buffering = ref(false);

    const toggleMute = () => {
      if (videoElement.value) {
        videoElement.value.muted = !videoElement.value.muted;
        muted.value = videoElement.value.muted;
      }
    };

    const onPlay = () => {
      buffering.value = false;
    };

    const onPause = () => {
      // Handle pause state
    };

    const onBuffering = () => {
      buffering.value = true;
    };

    const onVolumeChange = () => {
      if (videoElement.value) {
        muted.value = videoElement.value.muted;
      }
    };

    watch(muted, (newValue) => {
      if (videoElement.value) {
        videoElement.value.muted = newValue;
      }
    });

    return {
      videoElement,
      muted,
      buffering,
      toggleMute,
      onPlay,
      onPause,
      onBuffering,
      onVolumeChange,
    };
  },
});
</script>

<style scoped lang="css">
.live-stream-player {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--player-bg-color);
}

video {
  width: 100%;
  height: auto;
  background-color: var(--video-bg-color);
}

.buffering-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--buffering-text-color);
  font-size: 1.5rem;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 0.5rem;
  border-radius: 5px;
}

.mute-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
}
</style>