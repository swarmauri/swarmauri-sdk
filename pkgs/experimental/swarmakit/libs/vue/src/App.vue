<template>
  <div id="app">
    <h1>Hello, Vue with Vite and TypeScript!</h1>
    <button @click="count++">Clicked {{ count }} times</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  setup() {
    const count = ref(0);
    return {
      count,
    };
  },
});
</script>

<style scoped>
h1 {
  color: #42b983;
}
</style>
