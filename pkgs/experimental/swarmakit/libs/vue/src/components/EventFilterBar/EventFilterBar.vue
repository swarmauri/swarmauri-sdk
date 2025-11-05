<template>
  <div class="event-filter-bar" role="toolbar" aria-label="Event Filter Bar">
    <form @submit.prevent="applyFilters">
      <div class="filter-group">
        <label for="category">Category</label>
        <select id="category" v-model="filters.category">
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="date-range">Date Range</label>
        <input type="date" id="start-date" v-model="filters.startDate" />
        <input type="date" id="end-date" v-model="filters.endDate" />
      </div>

      <div class="filter-group">
        <label for="location">Location</label>
        <input type="text" id="location" v-model="filters.location" placeholder="Enter location" />
      </div>

      <div class="filter-group">
        <label for="participants">Participants</label>
        <input type="number" id="participants" v-model="filters.participants" min="1" />
      </div>

      <div class="filter-buttons">
        <button type="submit">Apply Filters</button>
        <button type="button" @click="clearFilters">Clear Filters</button>
      </div>
    </form>

    <div v-if="activeFilters" class="active-filters">
      Active Filters: {{ activeFilters }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'EventFilterBar',
  setup() {
    const categories = ref(['Conference', 'Meetup', 'Workshop']);
    const filters = ref({
      category: '',
      startDate: '',
      endDate: '',
      location: '',
      participants: 1
    });

    const activeFilters = computed(() => {
      return Object.entries(filters.value)
        .filter(([, value]) => value)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
    });

    const applyFilters = () => {
      console.log('Filters applied:', filters.value);
    };

    const clearFilters = () => {
      filters.value = {
        category: '',
        startDate: '',
        endDate: '',
        location: '',
        participants: 1
      };
    };

    return {
      categories,
      filters,
      activeFilters,
      applyFilters,
      clearFilters
    };
  }
});
</script>

<style scoped>
@import './EventFilterBar.css';
</style>