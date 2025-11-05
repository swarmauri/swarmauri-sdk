<template>
  <div class="contextual-navigation" :aria-hidden="!isVisible">
    <button @click="toggleMenu" class="contextual-toggle" :aria-expanded="isVisible">
      <span v-if="isVisible">Close Menu</span>
      <span v-else>Open Menu</span>
    </button>
    <div v-if="isVisible" class="contextual-menu" role="menu">
      <ul>
        <li v-for="(item, index) in menuItems" :key="index" role="menuitem">
          <a :href="item.link">{{ item.name }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

interface MenuItem {
  name: string;
  link: string;
}

export default defineComponent({
  name: 'ContextualNavigation',
  props: {
    menuItems: {
      type: Array as () => MenuItem[],
      required: true,
    },
  },
  setup() {
    const isVisible = ref(false);
    const toggleMenu = () => {
      isVisible.value = !isVisible.value;
    };

    return {
      isVisible,
      toggleMenu,
    };
  },
});
</script>

<style scoped lang="css">
.contextual-navigation {
  position: relative;
  font-size: var(--font-size, 16px);
}

.contextual-toggle {
  background-color: var(--toggle-bg-color, #007bff);
  color: var(--toggle-text-color, #fff);
  border: none;
  padding: 10px;
  cursor: pointer;
  font-size: var(--button-font-size, 16px);
}

.contextual-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: var(--menu-bg-color, #fff);
  border: 1px solid #ccc;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.contextual-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.contextual-menu li {
  padding: 10px;
}

.contextual-menu a {
  color: var(--menu-link-color, #007bff);
  text-decoration: none;
}

.contextual-menu a:hover {
  text-decoration: underline;
}
</style>