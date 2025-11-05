<script lang="ts">
  import { onMount } from 'svelte';

  export let src: string = '';
  export let isPlaying: boolean = false;
  export const isLoading: boolean = false;
  export let currentTime: number = 0;
  export let duration: number = 0;

  let canvasElement: HTMLCanvasElement;
  let audioElement: HTMLAudioElement;
  let audioContext: AudioContext;
  let analyser: AnalyserNode;
  let dataArray: Uint8Array;
  let animationFrameId: number;

  const drawWaveform = () => {
    if (!analyser || !canvasElement) return;

    const canvasCtx = canvasElement.getContext('2d');
    if (!canvasCtx) return;

    const bufferLength = analyser.frequencyBinCount;
    dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = 'rgba(255, 255, 255, 1)';
    canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgba(0, 0, 0, 1)';
    canvasCtx.beginPath();

    const sliceWidth = canvasElement.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvasElement.height) / 2;

      if (i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvasElement.width, canvasElement.height / 2);
    canvasCtx.stroke();

    animationFrameId = requestAnimationFrame(drawWaveform);
  };

  const initializeAudio = () => {
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaElementSource(audioElement);
    source.connect(analyser);
    analyser.connect(audioContext.destination);

    analyser.fftSize = 2048;
    drawWaveform();
  };

  const togglePlay = () => {
    if (isPlaying) {
      audioElement.pause();
    } else {
      audioElement.play();
    }
    isPlaying = !isPlaying;
  };

  onMount(() => {
    initializeAudio();
    return () => cancelAnimationFrame(animationFrameId);
  });
</script>

<div class="audio-waveform-display" role="region" aria-label="Audio Waveform Display">
  <audio bind:this={audioElement} src={src} on:loadedmetadata={() => duration = audioElement.duration} on:timeupdate={() => currentTime = audioElement.currentTime}></audio>
  <canvas bind:this={canvasElement} width="600" height="100" aria-label="Waveform"></canvas>
  <button on:click={togglePlay} on:keydown={(e) => e.key === 'Enter' && togglePlay()} aria-label={isPlaying ? 'Pause' : 'Play'}>
    {#if isPlaying}Pause{:else}Play{/if}
  </button>
</div>

<style lang="css">
  @import './AudioWaveformDisplay.css';
</style>