<template>
  <div class="image-slider" @mouseenter="setHover(true)" @mouseleave="setHover(false)">
    <div class="slider-images">
      <div
        v-for="(image, index) in images"
        :key="index"
        class="slider-image"
        :class="{ active: index === activeIndex, hover: isHovering }"
        :style="{ backgroundImage: 'url(' + image + ')' }"
      ></div>
    </div>
    <button class="prev-btn" @click="prevImage" aria-label="Previous image">‹</button>
    <button class="next-btn" @click="nextImage" aria-label="Next image">›</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ImageSlider',
  props: {
    images: {
      type: Array as () => string[],
      required: true,
    },
  },
  setup(props) {
    const activeIndex = ref(0);
    const isHovering = ref(false);

    const setHover = (hoverState: boolean) => {
      isHovering.value = hoverState;
    };

    const prevImage = () => {
      activeIndex.value = (activeIndex.value - 1 + props.images.length) % props.images.length;
    };

    const nextImage = () => {
      activeIndex.value = (activeIndex.value + 1) % props.images.length;
    };

    return {
      activeIndex,
      isHovering,
      setHover,
      prevImage,
      nextImage,
    };
  },
});
</script>

<style scoped lang="css">
.image-slider {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: hidden;
  background-color: var(--slider-bg-color);
}

.slider-images {
  display: flex;
  transition: transform 0.5s ease;
}

.slider-image {
  flex: 0 0 100%;
  background-size: cover;
  background-position: center;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.slider-image.active {
  opacity: 1;
}

.slider-image.hover {
  filter: brightness(0.8);
}

.prev-btn, .next-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 2rem;
}

.prev-btn {
  left: 10px;
}

.next-btn {
  right: 10px;
}
</style>