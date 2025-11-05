<script lang="ts">
  import { onMount } from 'svelte';

  export let src: string = '';
  export let isPlaying: boolean = false;
  export let isMuted: boolean = false;
  export let volume: number = 1;

  let audioElement: HTMLAudioElement;

  const togglePlay = () => {
    if (isPlaying) {
      audioElement.pause();
    } else {
      audioElement.play();
    }
    isPlaying = !isPlaying;
  };

  const toggleMute = () => {
    audioElement.muted = isMuted = !isMuted;
  };

  const handleVolumeChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    volume = parseFloat(target.value);
    audioElement.volume = volume;
  };

  onMount(() => {
    audioElement.volume = volume;
  });
</script>

<div class="audio-player" role="region" aria-label="Audio Player">
  <audio bind:this={audioElement} src={src}></audio>
  <button on:click={togglePlay} on:keydown={(e) => e.key === 'Enter' && togglePlay()} aria-label={isPlaying ? 'Pause' : 'Play'}>
    {#if isPlaying}Pause{:else}Play{/if}
  </button>
  <button on:click={toggleMute} on:keydown={(e) => e.key === 'Enter' && toggleMute()} aria-label={isMuted ? 'Unmute' : 'Mute'}>
    {#if isMuted}Unmute{:else}Mute{/if}
  </button>
  <input type="range" min="0" max="1" step="0.01" value={volume} on:input={handleVolumeChange} aria-label="Volume Control" />
</div>

<style lang="css">
  @import './AudioPlayer.css';
</style>