<template>
  <div class="thumbs-poll" role="radiogroup" aria-labelledby="poll-question">
    <p id="poll-question">{{ question }}</p>
    <div class="thumbs">
      <button
        :aria-checked="selectedThumb === 'up'"
        :disabled="isDisabled"
        @click="selectThumb('up')"
        class="thumb"
        :class="{ selected: selectedThumb === 'up' }"
        role="radio"
      >
        👍
      </button>
      <button
        :aria-checked="selectedThumb === 'down'"
        :disabled="isDisabled"
        @click="selectThumb('down')"
        class="thumb"
        :class="{ selected: selectedThumb === 'down' }"
        role="radio"
      >
        👎
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'ThumbsUpThumbsDownPoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    initialSelection: {
      type: String as () => 'up' | 'down' | null,
      default: null,
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
    const selectedThumb = ref(props.initialSelection);

    const selectThumb = (thumb: 'up' | 'down') => {
      if (!props.isDisabled) {
        selectedThumb.value = thumb;
      }
    };

    return {
      selectedThumb,
      selectThumb,
    };
  },
});
</script>

<style scoped>
.thumbs-poll {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 16px;
}

.thumbs {
  display: flex;
}

.thumb {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  margin: 0 5px;
  color: var(--secondary-color);
}

.thumb.selected {
  color: var(--primary-color);
}

.thumb:focus {
  outline: 2px solid var(--primary-color);
}
</style>