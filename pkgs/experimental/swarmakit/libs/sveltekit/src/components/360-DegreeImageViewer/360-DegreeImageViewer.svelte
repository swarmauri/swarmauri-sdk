<script lang="ts">
  import { onMount } from 'svelte';

  export let imageUrls: string[] = [];
  export let isLoading: boolean = false;
  export let isRotating: boolean = false;
  export let isZoomed: boolean = false;

  let currentIndex = 0;
  let interval: ReturnType<typeof setInterval>;
  let zoomLevel = 1;

  const startRotation = () => {
    if (isRotating && imageUrls.length > 0) {
      interval = setInterval(() => {
        currentIndex = (currentIndex + 1) % imageUrls.length;
      }, 100);
    }
  };

  const stopRotation = () => {
    clearInterval(interval);
  };

  const toggleZoom = () => {
    isZoomed = !isZoomed;
    zoomLevel = isZoomed ? 2 : 1;
  };

  onMount(() => {
    startRotation();
    return () => stopRotation();
  });
</script>

<div role="button" class="viewer-container" aria-label="360 Degree Image Viewer" tabindex="0" on:click={toggleZoom} on:keydown={(e) => e.key === 'Enter' && toggleZoom()}>
  {#if isLoading}
    <div class="loading" role="status" aria-live="polite">Loading...</div>
  {:else}
    <img src={imageUrls[currentIndex]} alt="360-degree view" style="transform: scale({zoomLevel});" />
  {/if}
</div>

<style lang="css">
  @import './360-DegreeImageViewer.css';
</style>