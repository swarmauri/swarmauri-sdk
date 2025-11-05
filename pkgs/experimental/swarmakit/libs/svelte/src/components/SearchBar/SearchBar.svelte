<script lang="ts">
  export let isFocused: boolean = false;
  export let isDisabled: boolean = false;
  export let placeholder: string = 'Search...';
</script>

<input
  type="text"
  class="search-bar"
  class:is-focused={isFocused}
  disabled={isDisabled}
  placeholder={placeholder}
  aria-label="Search"
  tabindex="0"
/>

<style lang="css">
  @import './SearchBar.css';
</style>