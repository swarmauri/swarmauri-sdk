<template>
  <div class="rating-stars" role="radiogroup" aria-label="Rating">
    <button
      v-for="star in stars"
      :key="star"
      type="button"
      class="star"
      :class="{ active: star <= currentRating, hover: star <= hoverRating }"
      :aria-checked="star === currentRating"
      :aria-label="`${star} Star${star > 1 ? 's' : ''}`"
      @click="selectRating(star)"
      @mouseenter="setHoverRating(star)"
      @mouseleave="setHoverRating(0)"
    >
      ★
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'RatingStars',
  props: {
    maxStars: {
      type: Number,
      default: 5,
    },
    initialRating: {
      type: Number,
      default: 0,
    },
    inactive: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const currentRating = ref(props.initialRating);
    const hoverRating = ref(0);

    const selectRating = (rating: number) => {
      if (!props.inactive) {
        currentRating.value = rating;
      }
    };

    const setHoverRating = (rating: number) => {
      if (!props.inactive) {
        hoverRating.value = rating;
      }
    };

    return {
      currentRating,
      hoverRating,
      selectRating,
      setHoverRating,
      stars: Array.from({ length: props.maxStars }, (_, i) => i + 1),
    };
  },
});
</script>

<style scoped lang="css">
@import './RatingStars.css';
</style>