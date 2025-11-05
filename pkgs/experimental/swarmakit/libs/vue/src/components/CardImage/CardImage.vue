<template>
  <div class="card-image" :style="{ backgroundImage: `url(${src})` }" @mouseover="hover = true" @mouseleave="hover = false">
    <div v-if="caption" class="caption">{{ caption }}</div>
    <div v-if="hover && overlay" class="overlay">{{ overlay }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'CardImage',
  props: {
    src: {
      type: String,
      required: true,
    },
    caption: {
      type: String,
      default: '',
    },
    overlay: {
      type: String,
      default: '',
    },
  },
  setup() {
    const hover = ref(false);
    return { hover };
  },
});
</script>

<style scoped lang="css">
.card-image {
  background-size: cover;
  background-position: center;
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  border-radius: var(--border-radius);
  overflow: hidden;
}

.caption {
  position: absolute;
  bottom: 0;
  width: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  color: var(--color-text-light);
  padding: var(--spacing-sm);
  text-align: center;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3);
  color: var(--color-text-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
}
</style>