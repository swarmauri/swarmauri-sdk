<template>
  <div
    v-show="isOpen"
    class="command-palette"
    role="dialog"
    aria-modal="true"
    aria-labelledby="command-palette-title"
  >
    <div class="command-palette-content">
      <input
        type="text"
        v-model="searchQuery"
        class="command-palette-input"
        placeholder="Type a command..."
        aria-controls="command-list"
        @keydown.arrow-down.prevent="focusNext"
        @keydown.arrow-up.prevent="focusPrev"
      />
      <ul id="command-list" class="command-list" role="listbox">
        <li
          v-for="(command, index) in filteredCommands"
          :key="command.id"
          :class="{ active: index === activeIndex }"
          role="option"
          tabindex="0"
          @click="selectCommand(command)"
          @keydown.enter.prevent="selectCommand(command)"
          @keydown.space.prevent="selectCommand(command)"
        >
          {{ command.name }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';

interface Command {
  id: number;
  name: string;
}

export default defineComponent({
  name: 'CommandPalette',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const searchQuery = ref('');
    const commands = ref<Command[]>([
      { id: 1, name: 'Command 1' },
      { id: 2, name: 'Command 2' },
      { id: 3, name: 'Command 3' },
    ]);
    const activeIndex = ref(0);

    const filteredCommands = computed(() =>
      commands.value.filter(command =>
        command.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    );

    const focusNext = () => {
      if (activeIndex.value < filteredCommands.value.length - 1) {
        activeIndex.value++;
      }
    };

    const focusPrev = () => {
      if (activeIndex.value > 0) {
        activeIndex.value--;
      }
    };

    const selectCommand = (command: Command) => {
      console.log('Selected command:', command.name);
    };

    onMounted(() => {
      if (filteredCommands.value.length > 0) {
        activeIndex.value = 0;
      }
    });

    return { searchQuery, filteredCommands, activeIndex, focusNext, focusPrev, selectCommand };
  },
});
</script>

<style scoped lang="css">
.command-palette {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 600px;
  background-color: var(--palette-bg-color, #fff);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: var(--palette-radius, 8px);
  padding: 20px;
  z-index: 1000;
}

.command-palette-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.command-palette-input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--input-border-color, #ccc);
  border-radius: var(--input-radius, 4px);
}

.command-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.command-list li {
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.command-list li.active {
  background-color: var(--command-active-bg-color, #e0e0e0);
}
</style>