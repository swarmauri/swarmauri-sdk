<template>
  <header class="card-header" :aria-label="ariaLabel">
    <img v-if="image" :src="image" alt="" class="card-header__image" />
    <i v-if="icon" :class="`card-header__icon ${icon}`" aria-hidden="true"></i>
    <div class="card-header__text">
      <h1 class="card-header__title">{{ title }}</h1>
      <h2 class="card-header__subtitle">{{ subtitle }}</h2>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'CardHeader',
  props: {
    title: {
      type: String as PropType<string>,
      required: true,
    },
    subtitle: {
      type: String as PropType<string>,
      default: '',
    },
    image: {
      type: String as PropType<string>,
      default: '',
    },
    icon: {
      type: String as PropType<string>,
      default: '',
    },
    ariaLabel: {
      type: String as PropType<string>,
      default: 'Card Header',
    },
  },
});
</script>

<style scoped lang="css">
.card-header {
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--color-background);
  border-bottom: var(--border-width) solid var(--color-border);
}

.card-header__image {
  width: var(--image-size);
  height: var(--image-size);
  margin-right: var(--spacing-sm);
  border-radius: var(--border-radius);
  object-fit: cover;
}

.card-header__icon {
  font-size: var(--icon-size);
  margin-right: var(--spacing-sm);
}

.card-header__text {
  flex-grow: 1;
}

.card-header__title {
  font-size: var(--font-size-lg);
  margin: 0;
}

.card-header__subtitle {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  margin: 0;
}
</style>