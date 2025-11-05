<template>
  <div class="audio-player" role="region" aria-label="Audio player">
    <audio ref="audioElement" :src="src" @loadeddata="onLoadedData"></audio>
    <button @click="togglePlay" class="control-button" aria-label="Play/Pause">
      {{ isPlaying ? 'Pause' : 'Play' }}
    </button>
    <button @click="toggleMute" class="control-button" aria-label="Mute/Unmute">
      {{ isMuted ? 'Unmute' : 'Mute' }}
    </button>
    <input
      type="range"
      class="volume-control"
      min="0"
      max="1"
      step="0.1"
      v-model="volume"
      @input="changeVolume"
      aria-label="Volume control"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'AudioPlayer',
  props: {
    src: {
      type: String,
      required: true,
    },
  },
  setup() {
    const audioElement = ref<HTMLAudioElement | null>(null);
    const isPlaying = ref(false);
    const isMuted = ref(false);
    const volume = ref(1);

    const togglePlay = () => {
      const audio = audioElement.value;
      if (audio) {
        if (isPlaying.value) {
          audio.pause();
        } else {
          audio.play();
        }
        isPlaying.value = !isPlaying.value;
      }
    };

    const toggleMute = () => {
      const audio = audioElement.value;
      if (audio) {
        audio.muted = !audio.muted;
        isMuted.value = audio.muted;
      }
    };

    const changeVolume = () => {
      const audio = audioElement.value;
      if (audio) {
        audio.volume = volume.value;
      }
    };

    const onLoadedData = () => {
      const audio = audioElement.value;
      if (audio) {
        volume.value = audio.volume;
      }
    };

    return { isPlaying, isMuted, volume, togglePlay, toggleMute, changeVolume, onLoadedData };
  },
});
</script>

<style scoped lang="css">
.audio-player {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: var(--player-bg-color);
  border-radius: 5px;
}

.control-button {
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 3px;
}

.volume-control {
  width: 100px;
}
</style>
