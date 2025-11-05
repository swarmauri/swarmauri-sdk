<script lang="ts">
import { defineComponent} from 'vue';

export default defineComponent({
  name: 'ColumnVisibilityToggle',
  props: {
    columns: {
      type: Array as () => { name: string; visible: boolean }[],
      default: () => [],
    },
  },
  setup(props, { emit }) {
    const toggleColumnVisibility = (index: number) => {
      props.columns[index].visible = !props.columns[index].visible;
      emit('update:columns', props.columns);
    };

    return {
      toggleColumnVisibility,
    };
  },
});
</script>

<template>
  <div class="column-visibility-toggle">
    <ul>
      <li v-for="(column, index) in columns" :key="column.name">
        <button @click="toggleColumnVisibility(index)" :aria-pressed="column.visible">
          {{ column.visible ? 'Hide' : 'Show' }} {{ column.name }}
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped lang="css">
.column-visibility-toggle {
  padding: 16px;
  background-color: var(--toggle-bg);
}

button {
  padding: 8px;
  margin: 4px 0;
  border: none;
  background-color: var(--button-bg);
  color: var(--button-color);
  transition: background-color 0.3s ease;
}

button[aria-pressed="true"] {
  background-color: var(--button-active-bg);
}
</style>