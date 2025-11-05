<script lang="ts">
  export let images: string[] = [];
  export let activeIndex: number = 0;

  const nextImage = () => {
    activeIndex = (activeIndex + 1) % images.length;
  };

  const prevImage = () => {
    activeIndex = (activeIndex - 1 + images.length) % images.length;
  };

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'ArrowRight') {
      nextImage();
    } else if (event.key === 'ArrowLeft') {
      prevImage();
    }
  };
</script>

<div class="image-slider" role="menu" aria-label="Image Slider" tabindex="0" on:keydown={handleKeydown}>
  {#if images.length > 0}
    <img src={images[activeIndex]} alt={`Image ${activeIndex + 1}`} class="slider-image" />
    <div class="controls">
      <button on:click={prevImage} aria-label="Previous Image">&lt;</button>
      <button on:click={nextImage} aria-label="Next Image">&gt;</button>
    </div>
  {/if}
</div>

<style lang="css">
  @import './ImageSlider.css';
</style>