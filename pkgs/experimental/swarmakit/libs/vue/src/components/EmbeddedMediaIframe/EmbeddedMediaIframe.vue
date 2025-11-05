<template>
  <div class="embedded-media-iframe" :class="{ fullscreen: isFullscreen }">
    <iframe
      ref="iframe"
      :src="src"
      frameborder="0"
      allowfullscreen
      :aria-busy="isBuffering"
      @load="handleLoad"
    ></iframe>
    <button v-if="!isFullscreen" @click="toggleFullscreen" aria-label="Enter fullscreen" class="fullscreen-btn">⤢</button>
    <button v-else @click="toggleFullscreen" aria-label="Exit fullscreen" class="fullscreen-btn">⤡</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'EmbeddedMediaIframe',
  props: {
    src: {
      type: String,
      required: true,
    },
  },
  setup() {
    const isFullscreen = ref(false);
    const isBuffering = ref(true);

    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value;
    };

    const handleLoad = () => {
      isBuffering.value = false;
    };

    return {
      isFullscreen,
      isBuffering,
      toggleFullscreen,
      handleLoad,
    };
  },
});
</script>

<style scoped lang="css">
.embedded-media-iframe {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%;
  background-color: var(--iframe-bg-color);
  overflow: hidden;
}

.embedded-media-iframe iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.embedded-media-iframe.fullscreen {
  width: 100vw;
  height: 100vh;
  padding-bottom: 0;
}

.fullscreen-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}
</style>