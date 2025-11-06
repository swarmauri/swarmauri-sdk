<template>
  <div class="playground">
    <header class="header">
      <h1>ActionableList Playground</h1>
      <p>
        Toggle item states to preview the component directly from
        <code>src/components/ActionableList</code>.
      </p>
    </header>

    <section class="controls">
      <label>
        Item 1 loading
        <input type="checkbox" v-model="firstItemLoading" />
      </label>

      <label>
        Item 2 disabled
        <input type="checkbox" v-model="secondItemDisabled" />
      </label>

      <label>
        Accent style
        <select v-model="theme">
          <option value="teal">Teal</option>
          <option value="blue">Blue</option>
          <option value="violet">Violet</option>
        </select>
      </label>

      <label>
        Progress %
        <input type="range" v-model.number="progressValue" min="0" max="100" />
      </label>

      <label>
        Progress status
        <select v-model="progressStatus">
          <option value="active">Active</option>
          <option value="complete">Complete</option>
          <option value="paused">Paused</option>
          <option value="incomplete">Incomplete</option>
        </select>
      </label>
    </section>

    <section class="preview">
      <div class="preview-card">
        <ActionableList :items="items" :style="listStyle" />
      </div>
      <div class="preview-card progress-card">
        <ProgressCircle
          :progress="progressValue"
          :status="progressStatus"
          :style="progressStyle"
        />
        <span class="progress-label">{{ progressValue }}%</span>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from 'vue';
import ActionableList from './components/ActionableList/ActionableList.vue';
import ProgressCircle from './components/ProgressCircle/ProgressCircle.vue';

export default defineComponent({
  name: 'App',
  components: {
    ActionableList,
    ProgressCircle,
  },
  setup() {
    const firstItemLoading = ref(false);
    const secondItemDisabled = ref(false);
    const theme = ref<'teal' | 'blue' | 'violet'>('teal');
    const progressValue = ref(72);
    const progressStatus = ref<'active' | 'complete' | 'paused' | 'incomplete'>('active');

    const items = computed(() => [
      {
        label: 'Sync node transport policy',
        actionLabel: 'Execute',
        loading: firstItemLoading.value,
      },
      {
        label: 'Rebalance ingestion runners',
        actionLabel: 'View',
        disabled: secondItemDisabled.value,
      },
      {
        label: 'Share reliability digest',
        actionLabel: 'Open',
      },
    ]);

    const listStyle = computed(() => {
      const palette = {
        teal: {
          background: 'rgba(15, 118, 110, 0.15)',
          border: '1px solid rgba(20, 184, 166, 0.45)',
        },
        blue: {
          background: 'rgba(37, 99, 235, 0.14)',
          border: '1px solid rgba(59, 130, 246, 0.45)',
        },
        violet: {
          background: 'rgba(124, 58, 237, 0.14)',
          border: '1px solid rgba(139, 92, 246, 0.45)',
        },
      }[theme.value];

      return {
        ...palette,
        padding: '24px 28px',
        borderRadius: '20px',
        backdropFilter: 'blur(18px)',
      };
    });

    const progressStyle = computed(() => ({
      '--progress-circle-size': '164px',
      '--progress-circle-active-color': '#38bdf8',
      '--progress-circle-complete-color': '#34d399',
      '--progress-circle-paused-color': '#fbbf24',
      '--progress-circle-incomplete-color': '#f87171',
      display: 'block',
    }));

    return {
      firstItemLoading,
      secondItemDisabled,
      theme,
      progressValue,
      progressStatus,
      items,
      listStyle,
      progressStyle,
    };
  },
});
</script>

<style scoped>
.playground {
  min-height: 100vh;
  padding: 48px;
  background: linear-gradient(160deg, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1));
  color: #e2e8f0;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.header h1 {
  margin: 0 0 8px;
  font-size: 28px;
  color: #f8fafc;
}

.header p {
  margin: 0;
  color: rgba(226, 232, 240, 0.72);
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: rgba(226, 232, 240, 0.86);
}

select,
input[type='text'] {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.7);
  color: #f8fafc;
  min-width: 240px;
}

input[type='checkbox'] {
  transform: scale(1.2);
  accent-color: #38bdf8;
}

select:focus,
input[type='text']:focus {
  outline: none;
  border-color: rgba(56, 189, 248, 0.6);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

.controls {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.controls input[type='range'] {
  width: 220px;
}

.preview-card {
  padding: 36px 32px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(30, 41, 59, 0.65);
  max-width: 520px;
  display: grid;
  place-items: center;
}

.preview {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.progress-card {
  gap: 16px;
}

.progress-label {
  font-size: 18px;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.88);
}
</style>
