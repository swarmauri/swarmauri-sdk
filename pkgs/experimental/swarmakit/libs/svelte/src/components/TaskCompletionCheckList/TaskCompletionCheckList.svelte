<script lang="ts">
  interface Task {
    id: number;
    label: string;
    completed: boolean;
  }

  export let tasks: Task[] = [];
  export let ariaLabel: string = 'Task Completion Checklist';

  function toggleTaskCompletion(taskId: number) {
    tasks = tasks.map(task => 
      task.id === taskId ? { ...task, completed: !task.completed } : task
    );
  }
</script>

<ul class="checklist" aria-label={ariaLabel}>
  {#each tasks as { id, label, completed }}
    <li>
      <input 
        type="checkbox" 
        id={"task-" + id} 
        checked={completed} 
        on:change={() => toggleTaskCompletion(id)} 
      />
      <label for={"task-" + id}>{label}</label>
    </li>
  {/each}
</ul>

<style lang="css">
  @import './TaskCompletionCheckList.css';
</style>