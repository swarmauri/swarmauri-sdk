<template>
  <ul class="checklist">
    <li
      v-for="(task, index) in tasks"
      :key="index"
      :class="{
        checked: task.status === 'checked',
        unchecked: task.status === 'unchecked',
        partiallyComplete: task.status === 'partiallyComplete',
      }"
    >
      <input
        type="checkbox"
        :checked="task.status === 'checked'"
        :indeterminate="task.status === 'partiallyComplete'"
        :aria-checked="task.status === 'checked' ? 'true' : task.status === 'partiallyComplete' ? 'mixed' : 'false'"
        disabled
      />
      <span class="task-label">{{ task.label }}</span>
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface Task {
  label: string;
  status: 'checked' | 'unchecked' | 'partiallyComplete';
}

export default defineComponent({
  name: 'TaskCompletionCheckList',
  props: {
    tasks: {
      type: Array as () => Task[],
      required: true,
    },
  },
});
</script>

<style scoped lang="css">
.checklist {
  list-style-type: none;
  padding: 0;
  margin: var(--checklist-margin, 16px 0);
}

.checklist li {
  display: flex;
  align-items: center;
  padding: var(--checklist-item-padding, 8px 0);
}

.checklist li.checked .task-label {
  text-decoration: line-through;
  color: var(--task-checked-color, #28a745);
}

.checklist li.unchecked .task-label {
  color: var(--task-unchecked-color, #6c757d);
}

.checklist li.partiallyComplete .task-label {
  color: var(--task-partially-complete-color, #ffc107);
}

.task-label {
  margin-left: var(--task-label-margin, 8px);
}
</style>