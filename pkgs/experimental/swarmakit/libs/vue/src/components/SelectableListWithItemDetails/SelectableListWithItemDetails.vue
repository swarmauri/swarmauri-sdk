<template>
  <div class="selectable-list">
    <ul class="selectable-list-items">
      <li
        v-for="item in items"
        :key="item.id"
        :class="['selectable-list-item', { selected: item.id === selectedItem, disabled: disabled }]"
        @click="toggleSelection(item.id)"
      >
        <div class="item-content">
          {{ item.label }}
          <button @click.stop="toggleDetails(item.id)" class="details-button" :aria-expanded="item.id === openDetails ? 'true' : 'false'">
            {{ item.id === openDetails ? 'Hide Details' : 'Show Details' }}
          </button>
        </div>
        <div v-if="item.id === openDetails" class="item-details">
          {{ item.details }}
        </div>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface ListItem {
  id: number;
  label: string;
  details: string;
}

export default defineComponent({
  name: 'SelectableListWithItemDetails',
  props: {
    items: {
      type: Array as () => ListItem[],
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const selectedItem = ref<number | null>(null);
    const openDetails = ref<number | null>(null);

    const toggleSelection = (id: number) => {
      if (!props.disabled) {
        selectedItem.value = selectedItem.value === id ? null : id;
      }
    };

    const toggleDetails = (id: number) => {
      openDetails.value = openDetails.value === id ? null : id;
    };

    return { selectedItem, openDetails, toggleSelection, toggleDetails };
  },
});
</script>

<style scoped lang="css">
.selectable-list {
  border: var(--list-border, 1px solid #ddd);
  border-radius: var(--list-border-radius, 4px);
}

.selectable-list-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.selectable-list-item {
  padding: var(--list-item-padding, 10px 15px);
  margin: 4px 0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.selectable-list-item.selected {
  background-color: var(--selected-bg, #d0eaff);
}

.selectable-list-item.disabled {
  color: var(--disabled-color, #ccc);
  cursor: not-allowed;
}

.item-details {
  padding: var(--details-padding, 8px 12px);
  background-color: var(--details-bg, #f8f9fa);
}

.details-button {
  background: none;
  border: none;
  color: var(--button-color, #007bff);
  cursor: pointer;
  padding: 0;
}
</style>