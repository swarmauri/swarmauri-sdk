<script lang="ts">
  export let events: { title: string, description: string, completed: boolean, active: boolean }[] = [];

  function handleClick(index: number) {
    events = events.map((event, i) => ({
      ...event,
      active: i === index ? true : false
    }));
  }
</script>

<ul class="timeline" role="list">
  {#each events as { title, description, completed, active }, index}
    <li class="timeline-event" role="listitem">
      <div
        class="event-content"
        class:active={active}
        class:completed={completed}
        tabindex="0"
        on:click={() => handleClick(index)}
        on:keydown={(event) => event.key === 'Enter' && handleClick(index)}
        role='button'
      >
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </li>
  {/each}
</ul>

<style lang="css">
  @import './TimelineList.css';
</style>