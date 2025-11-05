<template>
  <div role="list" aria-labelledby="poll-question" class="ranking-poll">
    <p id="poll-question">{{ question }}</p>
    <ul>
      <li
        v-for="(option, index) in rankedOptions"
        :key="option"
        :draggable="!isDisabled"
        @dragstart="onDragStart(index)"
        @dragover.prevent
        @drop="onDrop(index)"
        class="rank-option"
      >
        <span>{{ index + 1 }}.</span> {{ option }}
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'RankingPoll',
  props: {
    question: {
      type: String,
      required: true,
    },
    options: {
      type: Array as () => string[],
      required: true,
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
    const rankedOptions = ref([...props.options]);

    const onDragStart = (index: number) => (event: DragEvent) => {
      event.dataTransfer?.setData('text/plain', index.toString());
    };

    const onDrop = (index: number) => (event: DragEvent) => {
      const draggedIndex = Number(event.dataTransfer?.getData('text'));
      const draggedItem = rankedOptions.value[draggedIndex];
      rankedOptions.value.splice(draggedIndex, 1);
      rankedOptions.value.splice(index, 0, draggedItem);
    };

    return {
      rankedOptions,
      onDragStart,
      onDrop,
    };
  },
});
</script>

<style scoped>
.ranking-poll {
  margin: 16px;
}

.rank-option {
  padding: 8px;
  margin-bottom: 4px;
  background-color: var(--secondary-color);
  color: #fff;
  border-radius: 4px;
  cursor: grab;
  user-select: none;
}

.rank-option:focus {
  outline: 2px solid var(--primary-color);
}
</style>