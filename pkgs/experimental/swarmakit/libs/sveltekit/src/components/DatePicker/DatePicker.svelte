<script lang="ts">
  export let date: string = '';
  export let startDate: string = '';
  export let endDate: string = '';
  export let time: string = '';
  export let mode: 'single' | 'range' | 'time' = 'single';

  function handleDateChange(event: Event) {
    date = (event.target as HTMLInputElement).value;
  }

  function handleStartDateChange(event: Event) {
    startDate = (event.target as HTMLInputElement).value;
  }

  function handleEndDateChange(event: Event) {
    endDate = (event.target as HTMLInputElement).value;
  }

  function handleTimeChange(event: Event) {
    time = (event.target as HTMLInputElement).value;
  }
</script>

<div class="date-picker-container">
  {#if mode === 'single'}
    <input
      type="date"
      bind:value={date}
      aria-label="Select Date"
      on:input={handleDateChange}
    />
  {:else if mode === 'range'}
    <input
      type="date"
      bind:value={startDate}
      aria-label="Select Start Date"
      on:input={handleStartDateChange}
    />
    <input
      type="date"
      bind:value={endDate}
      aria-label="Select End Date"
      on:input={handleEndDateChange}
    />
  {:else if mode === 'time'}
    <input
      type="time"
      bind:value={time}
      aria-label="Select Time"
      on:input={handleTimeChange}
    />
  {/if}
</div>

<style lang="css">
  @import './DatePicker.css';
</style>