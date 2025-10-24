<script>
  import {
    formatPrimaryValue,
    formatDelta,
  } from "../../core/index.js";

  export let tile = {};

  $: props = tile?.props ?? {};
  $: formattedValue = formatPrimaryValue(props.value, props.format);
  $: deltaLabel = formatDelta(props.delta);
  $: isNegative = (props.delta ?? 0) < 0;
  $: trendIcon =
    props.trend === "down" ? "▼" : props.trend === "flat" ? "◆" : "▲";
</script>

<div class="metric-card">
  <div class="metric-card__label">{props.label ?? ""}</div>
  <div class="metric-card__value">{formattedValue}</div>
  <div class="metric-card__delta" class:negative={isNegative}>
    <span>{trendIcon}</span>
    <span>{deltaLabel}</span>
  </div>
  <div class="metric-card__footnote">vs {props.period ?? "previous period"}</div>
</div>
