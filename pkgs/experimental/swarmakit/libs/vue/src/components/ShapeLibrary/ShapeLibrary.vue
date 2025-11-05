<template>
  <div class="shape-library">
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Search shapes..."
      aria-label="Search shapes"
    />
    <div class="shape-list">
      <div
        v-for="(shape, index) in filteredShapes"
        :key="index"
        class="shape-item"
        draggable="true"
        @dragstart="onDragStart(shape)"
        aria-label="Shape"
      >
        <img :src="shape.icon" :alt="shape.name" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

interface Shape {
  name: string;
  icon: string;
}

export default defineComponent({
  name: 'ShapeLibrary',
  setup() {
    const searchQuery = ref('');
    const shapes: Shape[] = [
      { name: 'Circle', icon: '/icons/circle.svg' },
      { name: 'Square', icon: '/icons/square.svg' },
      { name: 'Triangle', icon: '/icons/triangle.svg' },
    ];

    const filteredShapes = computed(() =>
      shapes.filter(shape => shape.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
    );

    const onDragStart = (shape: Shape) => {
      // Logic to handle drag start
      console.log(shape)
    };

    return {
      searchQuery,
      filteredShapes,
      onDragStart,
    };
  },
});
</script>

<style scoped>
.shape-library {
  padding: 10px;
  background-color: var(--library-bg);
}

.shape-list {
  display: flex;
  flex-wrap: wrap;
}

.shape-item {
  margin: 5px;
  cursor: grab;
}

.shape-item img {
  width: 50px;
  height: 50px;
}

input[type='text'] {
  width: 100%;
  padding: 5px;
  margin-bottom: 10px;
  border: 1px solid var(--input-border);
}
</style>