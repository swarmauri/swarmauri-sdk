<script lang="ts">
  export let date: string = '';
  export let time: string = '';
  export let disabled: boolean = false;

  function handleDateChange(event: Event) {
    date = (event.target as HTMLInputElement).value;
  }

  function handleTimeChange(event: Event) {
    time = (event.target as HTMLInputElement).value;
  }
</script>

<div class="date-time-picker-container">
  <input
    type="date"
    bind:value={date}
    aria-label="Select Date"
    on:input={handleDateChange}
    disabled={disabled}
  />
  <input
    type="time"
    bind:value={time}
    aria-label="Select Time"
    on:input={handleTimeChange}
    disabled={disabled}
  />
</div>

<style lang="css">
  @import './DateAndTimePicker.css';
</style>