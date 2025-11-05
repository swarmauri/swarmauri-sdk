<script lang="ts">
  export let src: string = '';
  export let title: string = '';
  export let allowFullscreen: boolean = false;

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      toggleFullscreen();
    }
  };

  const toggleFullscreen = () => {
    if (allowFullscreen && iframeElement.requestFullscreen) {
      iframeElement.requestFullscreen();
    }
  };

  let iframeElement: HTMLIFrameElement;
</script>

<div class="embedded-media-iframe" role="region" aria-label={title}>
  <iframe
    bind:this={iframeElement}
    src={src}
    title={title}
    allowfullscreen={allowFullscreen}
    aria-label="Embedded Media"
  ></iframe>
  {#if allowFullscreen}
    <div role="button" tabindex="0" on:click={toggleFullscreen} on:keydown={handleKeydown} aria-label="Toggle Fullscreen">
      Toggle Fullscreen
    </div>
  {/if}
</div>

<style lang="css">
  @import './EmbeddedMediaIframe.css';
</style>