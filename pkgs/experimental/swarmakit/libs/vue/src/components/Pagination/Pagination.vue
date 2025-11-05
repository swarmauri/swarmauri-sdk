<template>
  <nav class="pagination" aria-label="Pagination Navigation">
    <ul class="pagination-list">
      <li
        v-for="page in pages"
        :key="page"
        :class="['pagination-item', { active: page === currentPage }]"
        @click="changePage(page)"
        @mouseover="hoveredPage = page"
        @mouseleave="hoveredPage = null"
        :aria-current="page === currentPage ? 'page' : undefined"
      >
        {{ page }}
      </li>
    </ul>
  </nav>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'Pagination',
  props: {
    totalPages: {
      type: Number,
      required: true,
    },
    currentPage: {
      type: Number,
      required: true,
    },
  },
  setup(props, { emit }) {
    const hoveredPage = ref<number | null>(null);

    const pages = computed(() => {
      return Array.from({ length: props.totalPages }, (_, i) => i + 1);
    });

    const changePage = (page: number) => {
      if (page !== props.currentPage) {
        emit('update:currentPage', page);
      }
    };

    return { pages, hoveredPage, changePage };
  },
});
</script>

<style scoped lang="css">
.pagination {
  display: flex;
  justify-content: center;
}

.pagination-list {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
}

.pagination-item {
  padding: var(--pagination-item-padding, 8px 12px);
  margin: 0 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: var(--pagination-border-radius, 4px);
}

.pagination-item.active {
  background-color: var(--active-bg, #007bff);
  color: var(--active-color, #fff);
}

.pagination-item:hover:not(.active) {
  background-color: var(--hover-bg, #e9ecef);
}
</style>