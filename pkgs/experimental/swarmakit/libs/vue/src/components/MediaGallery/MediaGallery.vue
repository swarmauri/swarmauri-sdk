<template>
  <div class="media-gallery" role="region" aria-label="Media Gallery">
    <div class="thumbnail-view" v-if="viewMode === 'thumbnail'">
      <img v-for="(image, index) in images" :key="index" :src="image" alt="Thumbnail" @click="expandImage(index)" class="thumbnail" />
    </div>

    <div class="expanded-view" v-if="viewMode === 'expanded'">
      <button @click="previousImage" aria-label="Previous Image" class="nav-btn">◀</button>
      <img :src="images[currentIndex]" alt="Expanded View" class="expanded-image" @click="toggleZoom" />
      <button @click="nextImage" aria-label="Next Image" class="nav-btn">▶</button>
    </div>

    <div class="controls">
      <button @click="setViewMode('thumbnail')" aria-label="Thumbnail View" class="control-btn">Thumbnail</button>
      <button @click="setViewMode('expanded')" aria-label="Expanded View" class="control-btn">Expanded</button>
      <button @click="toggleSlideshow" aria-label="Toggle Slideshow" class="control-btn">
        {{ isSlideshow ? 'Stop Slideshow' : 'Start Slideshow' }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue';

export default defineComponent({
  name: 'MediaGallery',
  props: {
    images: {
      type: Array as () => string[],
      required: true,
    },
  },
  setup(props) {
    const viewMode = ref<'thumbnail' | 'expanded'>('thumbnail');
    const currentIndex = ref(0);
    const isSlideshow = ref(false);
    let slideshowInterval: number | undefined;

    const setViewMode = (mode: 'thumbnail' | 'expanded') => {
      viewMode.value = mode;
    };

    const expandImage = (index: number) => {
      currentIndex.value = index;
      setViewMode('expanded');
    };

    const nextImage = () => {
      currentIndex.value = (currentIndex.value + 1) % props.images.length;
    };

    const previousImage = () => {
      currentIndex.value = (currentIndex.value - 1 + props.images.length) % props.images.length;
    };

    const toggleSlideshow = () => {
      if (isSlideshow.value) {
        stopSlideshow();
      } else {
        startSlideshow();
      }
    };

    const startSlideshow = () => {
      isSlideshow.value = true;
      slideshowInterval = window.setInterval(nextImage, 3000);
    };

    const stopSlideshow = () => {
      isSlideshow.value = false;
      clearInterval(slideshowInterval);
    };

    const toggleZoom = () => {
      // Implement zoom in/out functionality
    };

    onMounted(() => {
      // Any setup needed on mount
    });

    onBeforeUnmount(() => {
      stopSlideshow();
    });

    return {
      viewMode,
      currentIndex,
      isSlideshow,
      setViewMode,
      expandImage,
      nextImage,
      previousImage,
      toggleSlideshow,
      toggleZoom,
    };
  },
});
</script>

<style scoped lang="css">
.media-gallery {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  background-color: var(--gallery-bg-color);
}

.thumbnail-view {
  display: flex;
  flex-wrap: wrap;
}

.thumbnail {
  width: 100px;
  height: 100px;
  margin: 5px;
  cursor: pointer;
}

.expanded-view {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expanded-image {
  max-width: 100%;
  max-height: 80vh;
  cursor: pointer;
}

.nav-btn {
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  font-size: 1.5rem;
  cursor: pointer;
}

.controls {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.control-btn {
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  padding: 0.5rem;
  margin: 0 0.5rem;
  cursor: pointer;
}
</style>