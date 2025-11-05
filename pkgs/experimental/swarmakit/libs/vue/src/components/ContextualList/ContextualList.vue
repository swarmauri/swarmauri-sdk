<template>
  <div class="contextual-list" role="list">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="list-item"
      :class="{ actionTriggered: item.actionTriggered, dismissed: item.dismissed }"
    >
      <span>{{ item.label }}</span>
      <button @click="triggerAction(index)">Action</button>
      <button @click="dismissItem(index)">Dismiss</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface ListItem {
  label: string;
  actionTriggered: boolean;
  dismissed: boolean;
}

export default defineComponent({
  name: 'ContextualList',
  props: {
    items: {
      type: Array as () => ListItem[],
      required: true,
    },
  },
  setup(props) {
    const triggerAction = (index: number) => {
      props.items[index].actionTriggered = true;
    };

    const dismissItem = (index: number) => {
      props.items[index].dismissed = true;
    };

    return { triggerAction, dismissItem };
  },
});
</script>

<style scoped lang="css">
.contextual-list {
  padding: 0;
}

.list-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--list-item-margin-bottom, 10px);
  padding: var(--list-item-padding, 10px);
  background-color: var(--list-item-background, #fff);
  border: var(--list-item-border, 1px solid #ccc);
}

.list-item.actionTriggered {
  background-color: var(--action-triggered-background, #e0f7fa);
}

.list-item.dismissed {
  display: none;
}
</style>