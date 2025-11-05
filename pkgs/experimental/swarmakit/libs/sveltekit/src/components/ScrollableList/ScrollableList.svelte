<script lang="ts">
  type ListItem = {
    id: number;
    text: string;
  };

  export let items: ListItem[] = [];
  export let disabled: boolean = false;

  let isScrolling = false;
  let endOfList = false;

  const onScroll = (event: Event) => {
    const { scrollTop, scrollHeight, clientHeight } = event.target as HTMLElement;
    isScrolling = scrollTop > 0;
    endOfList = scrollTop + clientHeight >= scrollHeight;
  };
</script>

<div
  class="scrollable-list {disabled ? 'disabled' : ''}"
  on:scroll={onScroll}
  aria-disabled={disabled}
  tabindex={disabled ? -1 : 0}
  role="menu"
>
  {#each items as item (item.id)}
    <div class="list-item" role="listitem">{item.text}</div>
  {/each}
</div>

<style lang="css">
  @import './ScrollableList.css';
</style>