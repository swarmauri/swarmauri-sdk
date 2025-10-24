<script>
  import { getContext } from "svelte";
  import { LAYOUT_CONTEXT_KEY } from "../../context.js";

  export let tile = {};

  const layoutCtx = getContext(LAYOUT_CONTEXT_KEY) ?? {};

  $: props = tile?.props ?? {};
  $: roleVariant = (tile?.role ?? "").endsWith("secondary") ? "secondary" : null;
  $: variant = props.variant ?? roleVariant ?? "primary";
  $: label = props.label ?? "Navigate";
  $: caption = props.caption ?? "";
  $: buttonClass =
    variant === "secondary" ? "nav-button nav-button--secondary" : "nav-button";

  function handleClick(event) {
    event?.preventDefault?.();

    const targetPage = props.targetPage ?? props.page ?? null;
    if (targetPage && typeof layoutCtx?.setPage === "function") {
      layoutCtx.setPage(targetPage);
    }

    const href = props.href ?? null;
    if (href && typeof window !== "undefined" && typeof window.open === "function") {
      const target = props.target ?? "_blank";
      window.open(href, target);
    }

    if (typeof layoutCtx?.sendEvent === "function") {
      layoutCtx.sendEvent({
        type: "ui:button.click",
        tile_id: tile?.id,
        target_page: targetPage,
        href,
      });
    }
  }
</script>

<button class={buttonClass} type="button" on:click={handleClick}>
  <span class="nav-button__label">{label}</span>
  {#if caption}
    <span class="nav-button__caption">{caption}</span>
  {/if}
</button>
