<template>
  <button
    class="floating-action-button"
    @click="toggleExpand"
    :aria-expanded="localIsExpanded"
  >
    <span v-if="localIsExpanded" aria-hidden="true">✖</span>
    <span v-else aria-hidden="true">+</span>
    <span class="sr-only">{{ localIsExpanded ? 'Close menu' : 'Open menu' }}</span>
  </button>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'FloatingActionButton',
  props: {
    isExpanded: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const localIsExpanded = ref(props.isExpanded);

    const toggleExpand = () => {
      localIsExpanded.value = !localIsExpanded.value;
    };

    return { localIsExpanded, toggleExpand };
  },
});
</script>

<style scoped lang="css">
.floating-action-button {
  background-color: var(--fab-bg-color, #6200ee);
  color: var(--fab-color, #fff);
  border: none;
  border-radius: var(--fab-radius, 50%);
  padding: 15px;
  position: fixed;
  bottom: 20px;
  right: 20px;
  cursor: pointer;
  transition: transform 0.3s, background-color 0.3s;
}

.floating-action-button:hover {
  background-color: var(--fab-hover-bg-color, #3700b3);
}

.floating-action-button:focus {
  outline: 2px solid var(--fab-focus-color, #000);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>