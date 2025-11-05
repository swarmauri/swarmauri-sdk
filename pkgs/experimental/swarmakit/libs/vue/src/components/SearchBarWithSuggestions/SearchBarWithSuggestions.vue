<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'SearchBarWithSuggestions',
  props: {
    suggestions: {
      type: Array as () => string[],
      default: () => [],
    },
    filterOptions: {
      type: Array as () => string[],
      default: () => [],
    },
  },
  emits: ['search'],
  setup(props, { emit }) {
    const query = ref('');
    const filteredSuggestions = ref<string[]>([]);
    const showSuggestions = ref(false);

    const updateSuggestions = () => {
      if (query.value) {
        filteredSuggestions.value = props.suggestions.filter((suggestion) =>
          suggestion.toLowerCase().includes(query.value.toLowerCase())
        );
        showSuggestions.value = filteredSuggestions.value.length > 0;
      } else {
        showSuggestions.value = false;
      }
    };

    watch(query, updateSuggestions);

    const handleSearch = () => {
      emit('search', query.value);
    };

    return {
      query,
      filteredSuggestions,
      showSuggestions,
      handleSearch,
      updateSuggestions,
    };
  },
});
</script>

<template>
  <div class="search-bar-with-suggestions">
    <input
      type="text"
      v-model="query"
      @input="updateSuggestions"
      @keyup.enter="handleSearch"
      placeholder="Search..."
      aria-label="Search"
    />
    <ul v-if="showSuggestions" class="suggestions-list" aria-live="polite">
      <li v-for="suggestion in filteredSuggestions" :key="suggestion" @click="query = suggestion; handleSearch()">
        {{ suggestion }}
      </li>
    </ul>
    <div v-if="query && !filteredSuggestions.length" class="no-results">
      No results found
    </div>
  </div>
</template>

<style scoped lang="css">
.search-bar-with-suggestions {
  --input-border-color: #cccccc;
  --suggestion-bg: #ffffff;
  --suggestion-hover-bg: #f0f0f0;
  --no-results-color: #ff0000;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--input-border-color);
  border-radius: 4px;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid var(--input-border-color);
  border-top: none;
}

.suggestions-list li {
  padding: 8px;
  background-color: var(--suggestion-bg);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.suggestions-list li:hover {
  background-color: var(--suggestion-hover-bg);
}

.no-results {
  color: var(--no-results-color);
  padding: 8px;
}
</style>