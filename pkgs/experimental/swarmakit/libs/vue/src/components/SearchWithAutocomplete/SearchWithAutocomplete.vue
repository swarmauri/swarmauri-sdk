<template>
  <div class="search-autocomplete">
    <input
      type="text"
      v-model="query"
      @input="onInput"
      placeholder="Search..."
      aria-label="Search input"
    />
    <ul v-if="query && filteredResults.length" class="results-list">
      <li v-for="(result, index) in filteredResults" :key="index">{{ result }}</li>
    </ul>
    <p v-if="query && !filteredResults.length" class="no-results">No results found.</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'SearchWithAutocomplete',
  props: {
    options: {
      type: Array as () => string[],
      default: () => [],
    },
    query:{
      type:String,
      default:'',
    },
  },
  setup(props) {
    const query = ref(props.query);

    const filteredResults = computed(() =>
      props.options.filter(option =>
        option.toLowerCase().includes(query.value.toLowerCase())
      )
    );

    const onInput = () => {
      // Logic to handle input can be added here
    };

    return { query, filteredResults, onInput };
  },
});
</script>

<style scoped lang="css">
.search-autocomplete {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.results-list {
  position: absolute;
  width: 100%;
  background-color: var(--results-bg, white);
  border: 1px solid var(--results-border, #ccc);
  z-index: 10;
  list-style: none;
  margin: 0;
  padding: 0;
}

.results-list li {
  padding: 10px;
  cursor: pointer;
}

.results-list li:hover {
  background-color: var(--results-hover-bg, #f0f0f0);
}

.no-results {
  color: var(--no-results-color, #ff0000);
  margin-top: 5px;
}
</style>