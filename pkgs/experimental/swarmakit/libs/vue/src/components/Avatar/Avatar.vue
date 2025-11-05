<template>
  <div class="avatar-container" role="img" :aria-label="ariaLabel">
    <div v-if="imageSrc" class="avatar" :style="{ backgroundImage: `url(${imageSrc})` }"></div>
    <div v-else class="avatar placeholder">{{ initials }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Avatar',
  props: {
    imageSrc: {
      type: String,
      default: '',
    },
    initials: {
      type: String,
      default: 'A',
    },
    ariaLabel: {
      type: String,
      default: 'User Avatar',
    },
  },
});
</script>

<style scoped lang="css">
.avatar-container {
  display: inline-block;
  width: var(--avatar-size, 50px);
  height: var(--avatar-size, 50px);
  border-radius: 50%;
  overflow: hidden;
}

.avatar {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-color: var(--avatar-bg-color, #ccc);
}

.placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--avatar-placeholder-bg-color, #eee);
  color: var(--avatar-placeholder-text-color, #333);
  font-size: var(--avatar-font-size, 20px);
}
</style>