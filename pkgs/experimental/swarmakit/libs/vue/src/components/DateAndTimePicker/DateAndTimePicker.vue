<template>
  <div class="date-time-picker-container">
    <input 
      type="date" 
      :value="selectedDate" 
      :disabled="disabled" 
      @input="updateDate" 
      aria-label="Select Date"
      :aria-disabled="disabled"
    />
    <input 
      type="time" 
      :value="selectedTime" 
      :disabled="disabled" 
      @input="updateTime" 
      aria-label="Select Time"
      :aria-disabled="disabled"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'DateAndTimePicker',
  props: {
    selectedDate: {
      type: String,
      default: '',
    },
    selectedTime: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    updateDate(event: Event) {
      const input = event.target as HTMLInputElement;
      this.$emit('update:selectedDate', input.value);
    },
    updateTime(event: Event) {
      const input = event.target as HTMLInputElement;
      this.$emit('update:selectedTime', input.value);
    },
  },
});
</script>

<style scoped lang="css">
@import './DateAndTimePicker.css';
</style>