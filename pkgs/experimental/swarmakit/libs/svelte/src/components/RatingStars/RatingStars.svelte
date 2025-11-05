<script lang="ts">
  export let rating: number = 0;
  export let maxRating: number = 5;
  export let state: 'hover' | 'selected' | 'inactive' = 'inactive';
  export let ariaLabel: string = 'Rating Stars';

  const stars = Array.from({ length: maxRating }, (_, i) => i + 1);
</script>

<div
  class="rating-stars"
  role="radiogroup"
  aria-label={ariaLabel}
  data-state={state}
>
  {#each stars as star}
    <button
      role="radio"
      class="star {(star <= rating) ? 'filled' : ''}"
      aria-checked={star === rating}
      aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
      on:click={() => (rating = star)}
    >
      ★
    </button>
  {/each}
</div>

<style lang="css">
  @import './RatingStars.css';
</style>