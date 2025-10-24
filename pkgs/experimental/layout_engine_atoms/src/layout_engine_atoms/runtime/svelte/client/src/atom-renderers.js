import FallbackRenderer from "./components/FallbackRenderer.svelte";
import MetricCard from "./components/atoms/MetricCard.svelte";
import MarkdownPanel from "./components/atoms/MarkdownPanel.svelte";
import HorizontalBarCard from "./components/atoms/HorizontalBarCard.svelte";
import LineChartCard from "./components/atoms/LineChartCard.svelte";
import TableCard from "./components/atoms/TableCard.svelte";
import NavButton from "./components/atoms/NavButton.svelte";

export function createAtomRenderers() {
  return {
    "viz:metric:kpi": MetricCard,
    "viz:panel:markdown": MarkdownPanel,
    "viz:bar:horizontal": HorizontalBarCard,
    "viz:timeseries:line": LineChartCard,
    "viz:table:basic": TableCard,
    "ui:button:primary": NavButton,
    "ui:button:secondary": NavButton,
    default: FallbackRenderer,
  };
}
