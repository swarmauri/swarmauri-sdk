<template>
  <div class="recurring-event-scheduler" role="region" aria-label="Recurring Event Scheduler">
    <div class="recurrence-settings">
      <label for="recurrence-pattern">Recurrence Pattern:</label>
      <select id="recurrence-pattern" v-model="recurrencePattern" aria-label="Select recurrence pattern">
        <option value="daily">Daily</option>
        <option value="weekly">Weekly</option>
        <option value="monthly">Monthly</option>
      </select>
      
      <label for="start-date">Start Date:</label>
      <input id="start-date" type="date" v-model="startDate" aria-label="Select start date" />
      
      <label for="end-date">End Date:</label>
      <input id="end-date" type="date" v-model="endDate" aria-label="Select end date" />
    </div>
    
    <button @click="setRecurrence" aria-label="Set recurrence">Set Recurrence</button>
    
    <div v-if="feedbackMessage" class="feedback">{{ feedbackMessage }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'RecurringEventScheduler',
  props:{
    feedbackMessageProp: {
      type:String,
      default:'',
    }
  },
  setup(props) {
    const recurrencePattern = ref('daily');
    const startDate = ref('');
    const endDate = ref('');
    const feedbackMessage = ref(props.feedbackMessageProp);

    const setRecurrence = () => {
      if (startDate.value && endDate.value) {
        feedbackMessage.value = `Recurrence set: ${recurrencePattern.value} from ${startDate.value} to ${endDate.value}`;
      } else {
        feedbackMessage.value = 'Please select start and end dates';
      }
    };

    return {
      recurrencePattern,
      startDate,
      endDate,
      feedbackMessage,
      setRecurrence
    };
  }
});
</script>

<style scoped>
@import './RecurringEventScheduler.css';
</style>