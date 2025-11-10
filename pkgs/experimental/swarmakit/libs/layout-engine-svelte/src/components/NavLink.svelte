<script lang="ts">
  import { derived } from "svelte/store";
  import { useManifestStore } from "../context";
  import { createSiteNavigation } from "../site";

  export let pageId: string;

  const manifest = useManifestStore();
  const navigation = createSiteNavigation(manifest);
  const pages = navigation.pages;
  const activePageId = navigation.activePageId;
  const page = derived([pages], ([$pages]) => $pages.find((candidate) => candidate.id === pageId));

  const onClick = () => {
    navigation.navigate(pageId);
  };
</script>

<button class:selected={$activePageId === pageId} on:click={onClick}>
  <slot>{#if $page}{$page.title ?? pageId}{:else}{pageId}{/if}</slot>
</button>
