<script>
  import { normalizeBarSeries } from "../../core/index.js";

  export let tile = {};

  $: props = tile?.props ?? {};
  $: heading = props.label ?? "";
  $: items = normalizeBarSeries(props.series ?? []);
</script>

<div class="bar-card">
  {#if heading}
    <h3 class="bar-card__title">{heading}</h3>
  {/if}

  {#each items as item (item.label ?? item.id ?? item.valueLabel)}
    <div class="bar-card__row">
      <div class="bar-card__row-header">
        <span class="bar-card__label">{item.label}</span>
        <span class="bar-card__value">{item.valueLabel}</span>
      </div>
      <div class="bar-card__bar">
        <div
          class="bar-card__bar-fill"
          style={`width: ${item.percent ?? 0}%`}
        ></div>
      </div>
      {#if item.annotation}
        <p class="bar-card__annotation">{item.annotation}</p>
      {/if}
    </div>
  {/each}

  {#if !items.length}
    <p class="bar-card__empty">No segment data available.</p>
  {/if}
</div>
