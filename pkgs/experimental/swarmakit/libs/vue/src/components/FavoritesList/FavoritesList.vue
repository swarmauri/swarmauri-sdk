<template>
  <div class="favorites-list" role="list" aria-label="Favorites list">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="list-item"
      :class="{ selected: selectedItem === index, hover: hoveredItem === index }"
      @click="selectItem(index)"
      @mouseover="hoverItem(index)"
      @mouseleave="hoverItem(null)"
    >
      <div class="item-header">
        {{ item.title }}
        <button
          class="star-button"
          :aria-pressed="item.starred"
          @click.stop="toggleStar(index)"
        >
          {{ item.starred ? '★' : '☆' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'FavoritesList',
  props: {
    items: {
      type: Array as () => Array<{ title: string; starred: boolean }>,
      required: true,
    },
  },
  setup(props) {
    const selectedItem = ref<number | null>(null);
    const hoveredItem = ref<number | null>(null);

    const selectItem = (index: number) => {
      selectedItem.value = selectedItem.value === index ? null : index;
    };

    const hoverItem = (index: number | null) => {
      hoveredItem.value = index;
    };

    const toggleStar = (index: number) => {
      props.items[index].starred = !props.items[index].starred;
    };

    return { selectedItem, hoveredItem, selectItem, hoverItem, toggleStar };
  },
});
</script>

<style scoped lang="css">
.favorites-list {
  list-style: none;
  padding: 0;
}

.list-item {
  margin: var(--item-margin, 5px 0);
  padding: var(--item-padding, 10px);
  border: var(--item-border, 1px solid #ccc);
  cursor: pointer;
}

.list-item.selected {
  background-color: var(--selected-background-color, #e0e0e0);
}

.list-item.hover {
  background-color: var(--hover-background-color, #f0f0f0);
}

.item-header {
  display: flex;
  justify-content: space-between;
  font-weight: var(--item-header-font-weight, bold);
}

.star-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--star-button-font-size, 1.5em);
}
</style>