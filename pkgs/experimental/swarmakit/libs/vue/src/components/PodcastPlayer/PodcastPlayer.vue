<template>
  <div class="podcast-player" role="region" aria-label="Podcast Player">
    <div class="player-controls">
      <button @click="togglePlayPause" aria-label="Play/Pause" class="control-btn">
        {{ isPlaying ? 'Pause' : 'Play' }}
      </button>
      <button @click="downloadEpisode" aria-label="Download Episode" class="control-btn">
        {{ isDownloading ? 'Downloading...' : 'Download' }}
      </button>
    </div>
    <div class="episode-list" v-if="showEpisodeList">
      <ul>
        <li v-for="(episode, index) in episodes" :key="index" @click="playEpisode(index)">
          {{ episode.title }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Episode {
  title: string;
  url: string;
}

export default defineComponent({
  name: 'PodcastPlayer',
  props: {
    episodes: {
      type: Array as () => Episode[],
      required: true,
    },
  },
  setup() {
    const isPlaying = ref(false);
    const currentEpisodeIndex = ref<number | null>(null);
    const isDownloading = ref(false);
    const showEpisodeList = ref(true);

    const togglePlayPause = () => {
      if (currentEpisodeIndex.value !== null) {
        isPlaying.value = !isPlaying.value;
      }
    };

    const playEpisode = (index: number) => {
      currentEpisodeIndex.value = index;
      isPlaying.value = true;
    };

    const downloadEpisode = () => {
      if (currentEpisodeIndex.value !== null) {
        isDownloading.value = true;
        setTimeout(() => {
          isDownloading.value = false;
        }, 3000);
      }
    };

    return {
      isPlaying,
      currentEpisodeIndex,
      isDownloading,
      showEpisodeList,
      togglePlayPause,
      playEpisode,
      downloadEpisode,
    };
  },
});
</script>

<style scoped lang="css">
.podcast-player {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  background-color: var(--player-bg-color);
}

.player-controls {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.control-btn {
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  margin: 0 0.5rem;
  cursor: pointer;
}

.episode-list ul {
  list-style: none;
  padding: 0;
}

.episode-list li {
  padding: 0.5rem;
  cursor: pointer;
  background-color: var(--episode-bg-color);
  margin-bottom: 0.25rem;
}
</style>