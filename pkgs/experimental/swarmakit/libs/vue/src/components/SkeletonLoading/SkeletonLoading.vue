<template>
  <div class="skeleton-loading" :aria-busy="loading">
    <div v-if="loading" class="skeleton"></div>
    <slot v-else></slot>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'SkeletonLoading',
  props: {
    loading: {
      type: Boolean as PropType<boolean>,
      default: true,
    },
  },
});
</script>

<style scoped lang="css">
.skeleton-loading {
  display: inline-block;
  width: 100%;
}

.skeleton {
  height: 20px;
  background-color: var(--skeleton-bg, #e0e0e0);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: 200px 0;
  }
}
</style>