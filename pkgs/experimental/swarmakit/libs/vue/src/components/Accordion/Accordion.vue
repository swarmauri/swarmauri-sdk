<template>
  <div class="accordion" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <button
      class="accordion-header"
      :aria-expanded="isOpen"
      @click="toggleAccordion"
      :class="{ hovered: isHovered }"
    >
      <slot name="header"></slot>
    </button>
    <div v-if="isOpen" class="accordion-content">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Accordion',
  props: {
    defaultOpen: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const isOpen = ref(props.defaultOpen);
    const isHovered = ref(false);

    const toggleAccordion = () => {
      isOpen.value = !isOpen.value;
    };

    return { isOpen, toggleAccordion, isHovered };
  },
});
</script>

<style scoped lang="css">
.accordion {
  border: var(--accordion-border, 1px solid #ccc);
  margin: var(--accordion-margin, 10px 0);
  border-radius: var(--accordion-border-radius, 4px);
}

.accordion-header {
  background-color: var(--accordion-header-bg, #f1f1f1);
  color: var(--accordion-header-color, #333);
  padding: var(--accordion-header-padding, 10px);
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: var(--accordion-header-font-size, 16px);
  border: none;
  outline: none;
  transition: background-color 0.3s ease;
}

.accordion-header.hovered {
  background-color: var(--accordion-header-hover-bg, #ddd);
}

.accordion-content {
  padding: var(--accordion-content-padding, 10px);
  background-color: var(--accordion-content-bg, #fff);
  border-top: var(--accordion-content-border-top, 1px solid #ccc);
}
</style>