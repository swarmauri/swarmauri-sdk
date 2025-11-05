<template>
  <div class="video-player-advanced" role="region" aria-label="Advanced Video Player">
    <video
      ref="videoElement"
      :src="videoSrc"
      @play="onPlay"
      @pause="onPause"
      @waiting="onBuffering"
      @fullscreenchange="onFullscreenChange"
      @enterpictureinpicture="onEnterPiP"
      @leavepictureinpicture="onLeavePiP"
      controls
      class="video-element"
    >
      <track kind="subtitles" v-if="subtitlesSrc" :src="subtitlesSrc" default>
    </video>
    <div class="controls">
      <button @click="togglePlayPause" aria-label="Play/Pause" class="control-btn">
        {{ isPlaying ? 'Pause' : 'Play' }}
      </button>
      <button @click="toggleFullscreen" aria-label="Fullscreen" class="control-btn">
        {{ isFullscreen ? 'Exit Fullscreen' : 'Fullscreen' }}
      </button>
      <button @click="toggleSubtitles" aria-label="Subtitles" class="control-btn">
        {{ areSubtitlesOn ? 'Subtitles Off' : 'Subtitles On' }}
      </button>
      <button @click="togglePiP" aria-label="Picture in Picture" class="control-btn">
        {{ isPiP ? 'Exit PiP' : 'PiP Mode' }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';

export default defineComponent({
  name: 'VideoPlayerAdvanced',
  props: {
    videoSrc: {
      type: String,
      required: true,
    },
    subtitlesSrc: {
      type: String,
      required: false,
    },
  },
  setup() {
    const isPlaying = ref(false);
    const isFullscreen = ref(false);
    const areSubtitlesOn = ref(true);
    const isPiP = ref(false);
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

    const toggleSubtitles = () => {
      if (videoElement.value) {
        const tracks = videoElement.value.textTracks;
        for (let i = 0; i < tracks.length; i++) {
          tracks[i].mode = areSubtitlesOn.value ? 'disabled' : 'showing';
        }
        areSubtitlesOn.value = !areSubtitlesOn.value;
      }
    };

    const togglePiP = async () => {
      if (videoElement.value) {
        try {
          if (isPiP.value) {
            await document.exitPictureInPicture();
          } else {
            await videoElement.value.requestPictureInPicture();
          }
        } catch (error) {
          console.error('Failed to toggle PiP.', error);
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

    const onEnterPiP = () => {
      isPiP.value = true;
    };

    const onLeavePiP = () => {
      isPiP.value = false;
    };

    return {
      isPlaying,
      isFullscreen,
      areSubtitlesOn,
      isPiP,
      videoElement,
      togglePlayPause,
      toggleFullscreen,
      toggleSubtitles,
      togglePiP,
      onPlay,
      onPause,
      onBuffering,
      onFullscreenChange,
      onEnterPiP,
      onLeavePiP,
    };
  },
});
</script>

<style scoped lang="css">
.video-player-advanced {
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