<template>
  <nav aria-label="Breadcrumb" class="breadcrumb">
    <ol class="breadcrumb-list">
      <li v-for="(crumb, index) in breadcrumbs" :key="index" class="breadcrumb-item">
        <span 
          v-if="!crumb.dropdown" 
          :class="{ 'breadcrumb-link': crumb.link }"
          @click="crumb.link ? navigateTo(crumb.link) : null"
          :aria-current="index === breadcrumbs.length - 1 ? 'page' : undefined"
        >
          {{ crumb.name }}
        </span>
        <div v-else class="dropdown">
          <button 
            @click="toggleDropdown(index)" 
            :aria-expanded="isDropdownOpen(index)"
            aria-haspopup="true"
          >
            {{ crumb.name }}
          </button>
          <ul v-if="isDropdownOpen(index)" class="dropdown-menu">
            <li 
              v-for="(item, idx) in crumb.dropdown" 
              :key="idx"
              @click="navigateTo(item.link)"
            >
              {{ item.name }}
            </li>
          </ul>
        </div>
      </li>
    </ol>
  </nav>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

interface Breadcrumb {
  name: string;
  link?: string;
  dropdown?: Array<{ name: string; link: string }>;
}

export default defineComponent({
  name: 'BreadcrumbWithDropdowns',
  props: {
    breadcrumbs: {
      type: Array as () => Breadcrumb[],
      required: true,
    },
  },
  data() {
    return {
      openDropdownIndex: null as number | null,
    };
  },
  methods: {
    navigateTo(link: string) {
      window.location.href = link;
    },
    toggleDropdown(index: number) {
      this.openDropdownIndex = this.openDropdownIndex === index ? null : index;
    },
    isDropdownOpen(index: number): boolean {
      return this.openDropdownIndex === index;
    },
  },
});
</script>

<style scoped lang="css">
.breadcrumb {
  display: flex;
  align-items: center;
  font-size: var(--font-size, 16px);
  color: var(--breadcrumb-color, #333);
}

.breadcrumb-list {
  list-style: none;
  display: flex;
  padding: 0;
}

.breadcrumb-item {
  margin-right: var(--breadcrumb-separator, 10px);
  position: relative;
}

.breadcrumb-link {
  cursor: pointer;
  color: var(--breadcrumb-link-color, #007bff);
}

.dropdown button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--breadcrumb-link-color, #007bff);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: var(--dropdown-bg, #fff);
  border: 1px solid var(--dropdown-border-color, #ccc);
  list-style: none;
  padding: 5px 0;
  display: block;
}

.dropdown-menu li {
  padding: 5px 10px;
  cursor: pointer;
}

.dropdown-menu li:hover {
  background-color: var(--dropdown-hover-bg, #f1f1f1);
}
</style>