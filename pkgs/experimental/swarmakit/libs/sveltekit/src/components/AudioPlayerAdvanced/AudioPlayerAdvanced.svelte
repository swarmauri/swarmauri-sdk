<script lang="ts">
  import { onMount } from 'svelte';

  export let src: string = '';
  export let isPlaying: boolean = false;
  export let isMuted: boolean = false;
  export let volume: number = 1;
  export let playbackRate: number = 1;

  let audioElement: HTMLAudioElement;
  let duration:number = 0;

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

  const handlePlaybackRateChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    playbackRate = parseFloat(target.value);
    audioElement.playbackRate = playbackRate;
  };

  const handleSeek = (event: Event) => {
    const target = event.target as HTMLInputElement;
    audioElement.currentTime = parseFloat(target.value);
  };

  onMount(() => {
    audioElement.volume = volume;
    audioElement.playbackRate = playbackRate;
    audioElement.addEventListener('loadedmetadata', () => {
      duration = audioElement.duration;
    });
  });
</script>

<div class="audio-player-advanced" role="region" aria-label="Advanced Audio Player">
  <audio bind:this={audioElement} src={src}></audio>
  <button on:click={togglePlay} on:keydown={(e) => e.key === 'Enter' && togglePlay()} aria-label={isPlaying ? 'Pause' : 'Play'}>
    {#if isPlaying}Pause{:else}Play{/if}
  </button>
  <button on:click={toggleMute} on:keydown={(e) => e.key === 'Enter' && toggleMute()} aria-label={isMuted ? 'Unmute' : 'Mute'}>
    {#if isMuted}Unmute{:else}Mute{/if}
  </button>
  <input type="range" min="0" max="{duration}" step="0.1" on:input={handleSeek} aria-label="Seek Control" />
  <input type="range" min="0" max="1" step="0.01" value={volume} on:input={handleVolumeChange} aria-label="Volume Control" />
  <input type="range" min="0.5" max="2" step="0.1" value={playbackRate} on:input={handlePlaybackRateChange} aria-label="Speed Control" />
</div>

<style lang="css">
  @import './AudioPlayerAdvanced.css';
</style>