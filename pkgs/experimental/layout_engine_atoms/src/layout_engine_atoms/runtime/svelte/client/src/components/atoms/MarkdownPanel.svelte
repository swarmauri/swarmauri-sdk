<script>
  import { markdownToHtml } from "../../core/index.js";

  export let tile = {};

  $: props = tile?.props ?? {};
  $: title = props.title ?? "";
  $: bodyHtml = markdownToHtml(props.body ?? "");
</script>

<div class="markdown-panel">
  {#if title}
    <h3 class="markdown-panel__title">{title}</h3>
  {/if}
  <div class="markdown-panel__body">{@html bodyHtml}</div>
</div>
