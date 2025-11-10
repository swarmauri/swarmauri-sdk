<script lang="ts">
  import { derived } from "svelte/store";
  import LayoutEngineView from "./LayoutEngineView.svelte";
  import { useManifestStore } from "../context";
  import { createSiteNavigation } from "../site";

  const manifest = useManifestStore();
  const navigation = createSiteNavigation(manifest);
  const pages = navigation.pages;
  const activePageId = navigation.activePageId;
  const activePage = derived([pages, activePageId], ([$pages, $activeId]) =>
    $pages.find((page) => page.id === $activeId) ?? null,
  );

  const handleNavigate = (pageId: string) => {
    const route = navigation.navigate(pageId);
    if (route && typeof window !== "undefined") {
      window.history.pushState({}, "", route);
    }
    if (typeof window !== "undefined") {
      window.dispatchEvent(
        new CustomEvent("layout-engine:navigate", {
          detail: { pageId },
        }),
      );
    }
  };
</script>

<div class="layout-engine-shell">
  <slot {navigation} {manifest}>
    {#if $pages.length}
      <nav class="layout-engine-shell__nav">
        {#each $pages as page (page.id)}
          <button
            type="button"
            class:selected={page.id === $activePage?.id}
            on:click={() => handleNavigate(page.id)}
          >
            {page.title ?? page.id}
          </button>
        {/each}
      </nav>
    {/if}
  </slot>
  <LayoutEngineView />
</div>

<style>
  .layout-engine-shell__nav {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.25rem;
  }

  .layout-engine-shell__nav button {
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: rgba(15, 23, 42, 0.8);
    color: inherit;
    border-radius: 12px;
    padding: 0.35rem 0.9rem;
    cursor: pointer;
  }

  .layout-engine-shell__nav button.selected {
    border-color: rgba(56, 189, 248, 0.85);
  }
</style>
