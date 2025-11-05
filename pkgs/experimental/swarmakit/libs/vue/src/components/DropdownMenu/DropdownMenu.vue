<template>
  <div class="dropdown-menu">
    <button @click="toggleDropdown" class="dropdown-toggle" :aria-expanded="isExpanded">
      Menu
    </button>
    <ul v-if="isExpanded" role="menu" class="dropdown-list">
      <li v-for="(item, index) in menuItems" :key="index" role="menuitem">
        <a :href="item.link" @mouseover="hoverItem(index)" @mouseleave="leaveItem" :class="{ active: activeIndex === index }">{{ item.name }}</a>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface MenuItem {
  name: string;
  link: string;
}

export default defineComponent({
  name: 'DropdownMenu',
  props: {
    menuItems: {
      type: Array as () => MenuItem[],
      required: true,
    },
  },
  setup() {
    const isExpanded = ref(false);
    const activeIndex = ref<number | null>(null);

    const toggleDropdown = () => {
      isExpanded.value = !isExpanded.value;
    };

    const hoverItem = (index: number) => {
      activeIndex.value = index;
    };

    const leaveItem = () => {
      activeIndex.value = null;
    };

    return {
      isExpanded,
      toggleDropdown,
      activeIndex,
      hoverItem,
      leaveItem,
    };
  },
});
</script>

<style scoped lang="css">
.dropdown-menu {
  position: relative;
  font-size: var(--font-size, 16px);
}

.dropdown-toggle {
  background-color: var(--toggle-bg-color, #007bff);
  color: var(--toggle-text-color, #fff);
  border: none;
  padding: 10px;
  cursor: pointer;
  font-size: var(--button-font-size, 16px);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: var(--menu-bg-color, #fff);
  border: 1px solid #ccc;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  list-style: none;
  margin: 0;
  padding: 0;
  width: 200px;
}

.dropdown-list li {
  padding: 10px;
}

.dropdown-list a {
  color: var(--menu-link-color, #007bff);
  text-decoration: none;
  display: block;
}

.dropdown-list a:hover {
  background-color: var(--hover-bg-color, #f0f0f0);
}

.dropdown-list a.active {
  font-weight: bold;
  background-color: var(--active-bg-color, #e0e0e0);
}
</style>