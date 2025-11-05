<script lang="ts">
  export let isOpen: boolean = false;
  export let title: string = 'Accordion Title';
  export let content: string = 'Accordion content goes here.';

  const toggle = () => {
    isOpen = !isOpen;
  };
</script>

<div class="accordion">
  <button 
    class="accordion-header" 
    on:click={toggle} 
    aria-expanded={isOpen} 
    aria-controls="accordion-content"
  >
    {title}
  </button>
  {#if isOpen}
    <div id="accordion-content" class="accordion-content">
      {content}
    </div>
  {/if}
</div>

<style lang="css">
  @import './Accordion.css';
</style>