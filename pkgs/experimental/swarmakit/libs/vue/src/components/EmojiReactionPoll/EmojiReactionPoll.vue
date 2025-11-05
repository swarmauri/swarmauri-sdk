<template>
  <div class="emoji-reaction-poll" role="radiogroup" aria-labelledby="poll-question">
    <p id="poll-question">{{ question }}</p>
    <div class="emojis">
      <button
        v-for="(emoji, index) in emojis"
        :key="index"
        :aria-checked="index === selectedEmoji"
        :disabled="isDisabled"
        @click="selectEmoji(index)"
        class="emoji"
        :class="{ selected: index === selectedEmoji }"
        role="radio"
      >
        {{ emoji }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'EmojiReactionPoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    emojis: {
      type: Array as () => string[],
      default: () => ['😀', '😐', '😢'],
    },
    initialSelection: {
      type: Number,
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
    const selectedEmoji = ref(props.initialSelection);

    const selectEmoji = (index: number) => {
      if (!props.isDisabled) {
        selectedEmoji.value = index;
      }
    };

    return {
      selectedEmoji,
      selectEmoji,
    };
  },
});
</script>

<style scoped>
.emoji-reaction-poll {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 16px;
}

.emojis {
  display: flex;
}

.emoji {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  margin: 0 5px;
  color: var(--secondary-color);
}

.emoji.selected {
  color: var(--primary-color);
}

.emoji:focus {
  outline: 2px solid var(--primary-color);
}
</style>