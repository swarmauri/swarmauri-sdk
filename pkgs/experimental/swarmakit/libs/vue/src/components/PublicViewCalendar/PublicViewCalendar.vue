<template>
  <div class="calendar" role="region" aria-label="Public Calendar">
    <div class="filter-options">
      <label for="category-filter">Category:</label>
      <select id="category-filter" v-model="selectedCategory" aria-label="Filter by category">
        <option value="">All</option>
        <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
      </select>
      
      <label for="location-filter">Location:</label>
      <select id="location-filter" v-model="selectedLocation" aria-label="Filter by location">
        <option value="">All</option>
        <option v-for="location in locations" :key="location" :value="location">{{ location }}</option>
      </select>
    </div>
    
    <div class="events">
      <div v-for="event in filteredEvents" :key="event.id" class="event" @click="showEventDetails(event)">
        <h3>{{ event.title }}</h3>
        <p>{{ event.date }}</p>
      </div>
    </div>
    
    <transition name="fade">
      <div v-if="selectedEvent" class="event-details" role="dialog" aria-labelledby="event-title">
        <h2 id="event-title">{{ selectedEvent.title }}</h2>
        <p>{{ selectedEvent.description }}</p>
        <button class="close-details" @click="closeEventDetails" aria-label="Close event details">Close</button>
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, PropType } from 'vue';

interface Event {
  id: number;
  title: string;
  description: string;
  category: string;
  location: string;
  date: string;
}

export default defineComponent({
  name: 'PublicViewCalendar',
  props: {
    selectedCategoryProp: {
      type: String,
      default:''
    },
    selectedEventProp: { 
      type: Object as PropType<Event | null>,
      default:null,
    }
  },
  setup(props) {
    const events = ref<Event[]>([
      { id: 1, title: 'Project Meeting', description: 'Discussing project scope.', category: 'Work', location: 'Room 101', date: '2023-11-01' },
      { id: 2, title: 'Yoga Class', description: 'Morning yoga session.', category: 'Health', location: 'Gym', date: '2023-11-02' }
    ]);

    const categories = ref([...new Set(events.value.map(event => event.category))]);
    const locations = ref([...new Set(events.value.map(event => event.location))]);
    const selectedCategory = ref('');
    const selectedLocation = ref('');
    const selectedEvent = ref<Event | null>(props.selectedEventProp);

    const filteredEvents = computed(() => {
      return events.value.filter(event => {
        return (!selectedCategory.value || event.category === selectedCategory.value) &&
               (!selectedLocation.value || event.location === selectedLocation.value);
      });
    });

    const showEventDetails = (event: Event) => {
      selectedEvent.value = event;
    };

    const closeEventDetails = () => {
      selectedEvent.value = null;
    };

    return {
      categories,
      locations,
      selectedCategory,
      selectedLocation,
      filteredEvents,
      selectedEvent,
      showEventDetails,
      closeEventDetails
    };
  }
});
</script>

<style scoped>
@import './PublicViewCalendar.css';
</style>