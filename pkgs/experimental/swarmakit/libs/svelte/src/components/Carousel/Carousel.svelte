<script lang="ts">
  import { onMount } from 'svelte';
  import { writable,get } from 'svelte/store';

  export let images: string[] = [];
  export let autoPlay: boolean = false;
  export let autoPlayInterval: number = 3000;

  let currentIndex = 0;
  let intervalId: NodeJS.Timeout;
  const isHovered = writable(false);

  const nextSlide = () => {
    currentIndex = (currentIndex + 1) % images.length;
  };

  const prevSlide = () => {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
  };

  const startAutoPlay = () => {
    if (autoPlay && images.length > 1) {
      intervalId = setInterval(() => {
        if (!get(isHovered)) {
          nextSlide();
        }
      }, autoPlayInterval);
    }
  };

  const stopAutoPlay = () => {
    clearInterval(intervalId);
  };

  onMount(() => {
    startAutoPlay();
    return () => stopAutoPlay();
  });
</script>

<div class="carousel" role="region" aria-label="Image Carousel" on:mouseenter={() => isHovered.set(true)} on:mouseleave={() => isHovered.set(false)}>
  <button on:click={prevSlide} on:keydown={(e) => e.key === 'Enter' && prevSlide()} aria-label="Previous slide">&#10094;</button>
  
  {#each images as image, index}
    <img src={image} alt={`Slide ${index + 1}`} class:selected={index === currentIndex} />
  {/each}
  
  <button on:click={nextSlide} on:keydown={(e) => e.key === 'Enter' && nextSlide()} aria-label="Next slide">&#10095;</button>
</div>

<style lang="css">
  @import './Carousel.css';
</style>