<template>
  <div class="schedule-crud-panel" role="region" aria-label="Schedule CRUD Panel">
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title">Event Title</label>
        <input type="text" id="title" v-model="form.title" required />
      </div>

      <div class="form-group">
        <label for="date">Date</label>
        <input type="date" id="date" v-model="form.date" required />
      </div>

      <div class="form-group">
        <label for="time">Time</label>
        <input type="time" id="time" v-model="form.time" required />
      </div>

      <div class="form-group">
        <label for="location">Location</label>
        <input type="text" id="location" v-model="form.location" />
      </div>

      <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" v-model="form.description"></textarea>
      </div>

      <div class="form-group">
        <label for="participants">Participants</label>
        <input type="text" id="participants" v-model="form.participants" />
      </div>

      <div class="crud-buttons">
        <button type="submit">Create Event</button>
        <button type="button" @click="updateEvent">Update Event</button>
        <button type="button" @click="deleteEvent">Delete Event</button>
      </div>
    </form>

    <div v-if="feedbackMessage" class="feedback">{{ feedbackMessage }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ScheduleCRUDPanel',
  props: {
    feedbackMessageProp: {
      type:String,
      default:'',
    }
  },
  setup(props) {
    const form = ref({
      title: '',
      date: '',
      time: '',
      location: '',
      description: '',
      participants: ''
    });

    const feedbackMessage = ref(props.feedbackMessageProp);

    const handleSubmit = () => {
      feedbackMessage.value = `Event "${form.value.title}" created successfully.`;
      clearForm();
    };

    const updateEvent = () => {
      feedbackMessage.value = `Event "${form.value.title}" updated successfully.`;
    };

    const deleteEvent = () => {
      feedbackMessage.value = `Event "${form.value.title}" deleted successfully.`;
      clearForm();
    };

    const clearForm = () => {
      form.value = {
        title: '',
        date: '',
        time: '',
        location: '',
        description: '',
        participants: ''
      };
    };

    return {
      form,
      feedbackMessage,
      handleSubmit,
      updateEvent,
      deleteEvent
    };
  }
});
</script>

<style scoped>
@import './ScheduleCRUDPanel.css';
</style>