<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'DataSummary',
  props: {
    data: {
      type: Array as () => number[],
      default: () => [],
    },
  },
  setup(props) {
    const total = ref<number | null>(null);
    const average = ref<number | null>(null);
    const count = ref<number | null>(null);
    const error = ref<string | null>(null);

    const calculateSummary = () => {
      try {
        if (!props.data.length) throw new Error('No data available');
        total.value = props.data.reduce((acc, val) => acc + val, 0);
        average.value = total.value / props.data.length;
        count.value = props.data.length;
        error.value = null;
      } catch (err: any) {
        error.value = err.message;
        total.value = null;
        average.value = null;
        count.value = null;
      }
    };

    watch(() => props.data, calculateSummary, { immediate: true });

    return {
      total,
      average,
      count,
      error,
    };
  },
});
</script>

<template>
  <div class="data-summary">
    <div v-if="error" class="error-message" role="alert">
      {{ error }}
    </div>
    <div v-else>
      <div>Total: {{ total }}</div>
      <div>Average: {{ average }}</div>
      <div>Count: {{ count }}</div>
    </div>
  </div>
</template>

<style scoped lang="css">
.data-summary {
  padding: 16px;
  border: 1px solid var(--summary-border-color);
  border-radius: 8px;
  background-color: var(--summary-bg);
}

.error-message {
  color: var(--error-color);
  font-weight: bold;
}
</style>