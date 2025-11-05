<script lang="ts">
  export let cards: { id: number; title: string; description: string; selected?: boolean; disabled?: boolean }[] = [];

  const selectCard = (card: { id: number; title: string; description: string; selected?: boolean; disabled?: boolean }) => {
    if (!card.disabled) {
      card.selected = !card.selected;
    }
  };
</script>

<div class="cardbased-list">
  {#each cards as card (card.id)}
    <div 
      class="card {card.selected ? 'selected' : ''} {card.disabled ? 'disabled' : ''}" 
      on:click={() => selectCard(card)} 
      aria-disabled={card.disabled}
      role ='button'
      tabindex = "0"
      on:keydown={(e)=> e.key === 'Enter' && selectCard(card)} 
    >
      <h2>{card.title}</h2>
      <p>{card.description}</p>
    </div>
  {/each}
</div>

<style lang="css">
  @import './CardbasedList.css';
</style>