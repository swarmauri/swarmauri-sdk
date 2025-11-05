<template>
  <div class="star-rating-poll" role="radiogroup" aria-labelledby="poll-question">
    <p id="poll-question">{{ question }}</p>
    <div class="stars">
      <button
        v-for="star in totalStars"
        :key="star"
        :aria-checked="star <= rating"
        :disabled="isDisabled"
        @click="rate(star)"
        class="star"
        :class="{ filled: star <= rating }"
        role="radio"
      >
        ★
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'StarRatingPoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    totalStars: {
      type: Number,
      default: 5,
    },
    initialRating: {
      type: Number,
      default: 0,
    },
    isDisabled: {
      type: Boolean,
      default: false,
    },
    showResults: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const rating = ref(props.initialRating);

    const rate = (star: number) => {
      if (!props.isDisabled) {
        rating.value = star;
      }
    };

    return {
      rating,
      rate,
    };
  },
});
</script>

<style scoped>
.star-rating-poll {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 16px;
}

.stars {
  display: flex;
}

.star {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--secondary-color);
}

.star.filled {
  color: var(--primary-color);
}

.star:focus {
  outline: 2px solid var(--primary-color);
}
</style>