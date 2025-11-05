<template>
  <transition name="fade">
    <div v-if="isOpen" class="dialog" role="dialog" aria-labelledby="dialog-title" aria-describedby="dialog-description">
      <div class="dialog-content">
        <h2 id="dialog-title">{{ event.title }}</h2>
        <p id="dialog-description">{{ event.description }}</p>
        <ul>
          <li><strong>Participants:</strong> {{ event.participants.join(', ') }}</li>
          <li><strong>Location:</strong> {{ event.location }}</li>
          <li><strong>Time:</strong> {{ event.time }}</li>
        </ul>
        <div class="dialog-actions">
          <button @click="editEvent" :disabled="isLoading">Edit</button>
          <button @click="deleteEvent" :disabled="isLoading">Delete</button>
          <button @click="duplicateEvent" :disabled="isLoading">Duplicate</button>
        </div>
        <button class="close-button" @click="closeDialog" aria-label="Close dialog">×</button>
      </div>
      <div v-if="isLoading" class="loading">Loading...</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </transition>
</template>

<script lang="ts">
import { defineComponent,PropType } from 'vue';

interface EventDetails {
  title: string;
  description: string;
  participants: string[];
  location: string;
  time: string;
}

export default defineComponent({
  name: 'EventDetailsDialog',
  props: {
    event: {
      type: Object as PropType<EventDetails>,
      required: true
    },
    isOpen: {
      type: Boolean,
      default: false
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    }
  },
  setup() {
    const editEvent = () => {};
    const deleteEvent = () => {};
    const duplicateEvent = () => {};
    const closeDialog = () => {};

    return {
      editEvent,
      deleteEvent,
      duplicateEvent,
      closeDialog
    };
  }
});
</script>

<style scoped>
@import './EventDetailsDialog.css';
</style>