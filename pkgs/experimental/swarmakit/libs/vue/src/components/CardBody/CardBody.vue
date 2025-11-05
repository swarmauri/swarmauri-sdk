<template>
  <section class="card-body" :aria-expanded="expanded" :aria-label="ariaLabel">
    <div class="card-body__content" :class="{ 'card-body__content--collapsed': !expanded }">
      <slot></slot>
    </div>
    <button v-if="collapsible" class="card-body__toggle" @click="toggleExpand" :aria-controls="'card-body-content'">
      {{ expanded ? 'Collapse' : 'Expand' }}
    </button>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'CardBody',
  props: {
    expanded: {
      type: Boolean,
      default: true,
    },
    collapsible: {
      type: Boolean,
      default: false,
    },
    ariaLabel: {
      type: String,
      default: 'Card Body',
    },
  },
  setup(props) {
    const isExpanded = ref(props.expanded);

    const toggleExpand = () => {
      isExpanded.value = !isExpanded.value;
    };

    return { isExpanded, toggleExpand };
  },
});
</script>

<style scoped lang="css">
.card-body {
  padding: var(--spacing-md);
  background-color: var(--color-background);
}

.card-body__content {
  max-height: none;
  overflow: auto;
  transition: max-height 0.3s ease;
}

.card-body__content--collapsed {
  max-height: var(--collapsed-height);
  overflow: hidden;
}

.card-body__toggle {
  margin-top: var(--spacing-sm);
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.card-body__toggle:hover {
  background-color: var(--color-primary-hover);
}
</style>