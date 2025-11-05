<template>
  <div class="date-picker-container">
    <input 
      type="date" 
      :value="startDate" 
      :disabled="disabled" 
      @input="updateStartDate" 
      aria-label="Start Date"
      :aria-disabled="disabled"
    />
    <input 
      v-if="isDateRange" 
      type="date" 
      :value="endDate" 
      :disabled="disabled" 
      @input="updateEndDate" 
      aria-label="End Date"
      :aria-disabled="disabled"
    />
    <input 
      v-if="isTimePicker" 
      type="time" 
      :value="selectedTime" 
      :disabled="disabled" 
      @input="updateTime" 
      aria-label="Time Picker"
      :aria-disabled="disabled"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'DatePicker',
  props: {
    startDate: {
      type: String,
      default: '',
    },
    endDate: {
      type: String,
      default: '',
    },
    selectedTime: {
      type: String,
      default: '',
    },
    isDateRange: {
      type: Boolean,
      default: false,
    },
    isTimePicker: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    updateStartDate(event: Event) {
      const input = event.target as HTMLInputElement;
      this.$emit('update:startDate', input.value);
    },
    updateEndDate(event: Event) {
      const input = event.target as HTMLInputElement;
      this.$emit('update:endDate', input.value);
    },
    updateTime(event: Event) {
      const input = event.target as HTMLInputElement;
      this.$emit('update:selectedTime', input.value);
    },
  },
});
</script>

<style scoped lang="css">
@import './DatePicker.css';
</style>