<template>
  <div class="event-reminder-system" role="region" aria-label="Event Reminder System">
    <form @submit.prevent="setReminder">
      <div class="form-group">
        <label for="event">Event</label>
        <select id="event" v-model="form.event" required>
          <option v-for="event in events" :key="event.id" :value="event.id">{{ event.title }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="time">Reminder Time</label>
        <select id="time" v-model="form.time" required>
          <option value="1 hour">1 hour before</option>
          <option value="1 day">1 day before</option>
          <option value="1 week">1 week before</option>
        </select>
      </div>

      <div class="form-group">
        <label for="method">Notification Method</label>
        <select id="method" v-model="form.method" required>
          <option value="email">Email</option>
          <option value="sms">SMS</option>
          <option value="push">Push Notification</option>
        </select>
      </div>

      <div class="reminder-buttons">
        <button type="submit">Set Reminder</button>
        <button type="button" @click="cancelReminder">Cancel Reminder</button>
      </div>
    </form>

    <div v-if="localFeedbackMessage" class="feedback">{{ localFeedbackMessage }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface Event {
  id: string;
  title: string;
}

export default defineComponent({
  name: 'EventReminderSystem',
  props: {
    feedbackMessage: {
      type: String,
      default:'',
    },
  },
  setup(props) {
    const events = ref<Event[]>([
      { id: '1', title: 'Team Meeting' },
      { id: '2', title: 'Project Deadline' },
      { id: '3', title: 'Client Call' }
    ]);

    const form = ref({
      event: '',
      time: '',
      method: ''
    });

    const localFeedbackMessage = ref(props.feedbackMessage);

    const setReminder = () => {
      localFeedbackMessage.value = `Reminder set for "${form.value.event}" via ${form.value.method}.`;
      clearForm();
    };

    const cancelReminder = () => {
      localFeedbackMessage.value = `Reminder for "${form.value.event}" canceled.`;
      clearForm();
    };

    const clearForm = () => {
      form.value = {
        event: '',
        time: '',
        method: ''
      };
    };

    return {
      events,
      form,
      localFeedbackMessage,
      setReminder,
      cancelReminder
    };
  }
});
</script>

<style scoped>
@import './EventReminderSystem.css';
</style>