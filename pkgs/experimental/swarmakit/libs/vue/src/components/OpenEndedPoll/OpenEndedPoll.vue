<template>
  <div class="open-ended-poll" role="form" aria-labelledby="open-ended-poll-label">
    <label id="open-ended-poll-label" class="poll-label">{{ question }}</label>
    <textarea
      v-model="response"
      :disabled="disabled"
      :aria-disabled="disabled"
      aria-required="true"
      placeholder="Type your response here..."
      class="response-input"
    ></textarea>
    <button
      @click="submitResponse"
      :disabled="disabled || !response.trim()"
      class="submit-button"
    >
      Submit
    </button>
    <div v-if="resultsVisible" class="results">
      <h3>Responses:</h3>
      <ul>
        <li v-for="(res, index) in responses" :key="index">{{ res }}</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'OpenEndedPoll',
  props: {
    question: {
      type: String,
      required: true
    },
    initialResponses: {
      type: Array as () => string[],
      default: () => []
    },
    resultsVisible: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const response = ref('');
    const responses = ref([...props.initialResponses]);

    const submitResponse = () => {
      if (response.value.trim()) {
        responses.value.push(response.value.trim());
        response.value = '';
      }
    };

    return {
      response,
      responses,
      submitResponse
    };
  }
});
</script>

<style scoped lang="css">
.open-ended-poll {
  padding: 1rem;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 5px;
  max-width: 500px;
  margin: 0 auto;
}

.poll-label {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.response-input {
  width: 100%;
  height: 100px;
  border: 1px solid var(--input-border-color, #ddd);
  border-radius: 5px;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  resize: none;
}

.submit-button {
  background-color: var(--button-bg-color, #007bff);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
}

.submit-button:disabled {
  background-color: var(--button-disabled-bg-color, #ccc);
  cursor: not-allowed;
}

.results {
  margin-top: 1rem;
}

.results h3 {
  margin-bottom: 0.5rem;
}

.results ul {
  list-style-type: disc;
  padding-left: 1.5rem;
}
</style>