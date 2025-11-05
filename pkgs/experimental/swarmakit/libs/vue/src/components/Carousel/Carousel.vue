<template>
  <div class="carousel" role="region" aria-label="Image carousel">
    <div class="carousel-inner" @mouseenter="pause" @mouseleave="autoPlay">
      <div
        v-for="(slide, index) in slides"
        :key="index"
        class="carousel-item"
        :class="{ active: index === currentIndex }"
        :aria-hidden="index !== currentIndex"
      >
        <img :src="slide.src" :alt="slide.alt" />
      </div>
    </div>
    <button class="carousel-control prev" @click="prevSlide" aria-label="Previous slide">‹</button>
    <button class="carousel-control next" @click="nextSlide" aria-label="Next slide">›</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue';

export default defineComponent({
  name: 'Carousel',
  props: {
    slides: {
      type: Array as () => { src: string; alt: string }[],
      required: true,
    },
    interval: {
      type: Number,
      default: 3000,
    },
  },
  setup(props) {
    const currentIndex = ref(0);
    let intervalId: number | null = null;

    const nextSlide = () => {
      currentIndex.value = (currentIndex.value + 1) % props.slides.length;
    };

    const prevSlide = () => {
      currentIndex.value = (currentIndex.value - 1 + props.slides.length) % props.slides.length;
    };

    const autoPlay = () => {
      intervalId = window.setInterval(nextSlide, props.interval);
    };

    const pause = () => {
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
      }
    };

    onMounted(autoPlay);
    onUnmounted(pause);

    return {
      currentIndex,
      nextSlide,
      prevSlide,
      autoPlay,
      pause,
    };
  },
});
</script>

<style scoped lang="css">
.carousel {
  position: relative;
  overflow: hidden;
  width: 100%;
  background-color: var(--carousel-bg-color);
}

.carousel-inner {
  display: flex;
  transition: transform 0.5s ease;
}

.carousel-item {
  min-width: 100%;
  transition: opacity 0.5s ease;
  opacity: 0;
  position: absolute;
  top: 0;
  left: 0;
}

.carousel-item.active {
  opacity: 1;
  position: relative;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: var(--control-bg-color);
  color: var(--control-text-color);
  border: none;
  font-size: 2rem;
  cursor: pointer;
  padding: 0.5rem;
}

.carousel-control.prev {
  left: 10px;
}

.carousel-control.next {
  right: 10px;
}
</style>