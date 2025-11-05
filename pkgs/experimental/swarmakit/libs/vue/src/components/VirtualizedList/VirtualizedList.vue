<template>
  <div class="virtualized-list" role="list" @scroll="onScroll">
    <div
      v-for="item in visibleItems"
      :key="item.id"
      class="list-item"
      role="listitem"
    >
      {{ item.label }}
    </div>
    <div v-if="loading" class="loading-indicator">Loading more items...</div>
    <div v-else-if="endOfList" class="end-of-list">End of list</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';

interface ListItem {
  id: number;
  label: string;
}

export default defineComponent({
  name: 'VirtualizedList',
  props: {
    items: {
      type: Array as () => ListItem[],
      required: true,
    },
    itemHeight: {
      type: Number,
      default: 50,
    },
  },
  setup(props) {
    const containerHeight = ref(400);
    const visibleItemsCount = computed(() => Math.ceil(containerHeight.value / props.itemHeight));
    const startIndex = ref(0);
    const loading = ref(false);
    const endOfList = ref(false);

    const visibleItems = computed(() => {
      return props.items.slice(startIndex.value, startIndex.value + visibleItemsCount.value);
    });

    const onScroll = (event: Event) => {
      const target = event.target as HTMLElement;
      if (target.scrollTop + target.clientHeight >= target.scrollHeight) {
        if (startIndex.value + visibleItemsCount.value < props.items.length) {
          loading.value = true;
          setTimeout(() => {
            startIndex.value += visibleItemsCount.value;
            loading.value = false;
          }, 1000);
        } else {
          endOfList.value = true;
        }
      }
    };

    onMounted(() => {
      containerHeight.value = document.querySelector('.virtualized-list')?.clientHeight || 400;
    });

    return { visibleItems, onScroll, loading, endOfList };
  },
});
</script>

<style scoped lang="css">
.virtualized-list {
  height: 400px;
  overflow-y: auto;
  border: 1px solid var(--list-border-color);
}

.list-item {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  border-bottom: 1px solid var(--item-border-color);
}

.loading-indicator,
.end-of-list {
  text-align: center;
  padding: 10px;
  color: var(--indicator-color);
}
</style>