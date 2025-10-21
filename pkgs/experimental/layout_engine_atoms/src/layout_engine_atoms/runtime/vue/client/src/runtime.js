import {
  computed,
  createApp,
  defineComponent,
  h,
  reactive,
  ref,
  watch,
  onBeforeUnmount,
  provide,
  inject,
} from "vue";
import { createAtomRenderers } from "./atom-renderers.js";
import { createRuntime } from "./runtime-core.js";

const atomRenderers = createAtomRenderers({
  computed,
  defineComponent,
  h,
  inject,
});

const runtime = createRuntime(
  {
    computed,
    createApp,
    defineComponent,
    h,
    reactive,
    ref,
    watch,
    onBeforeUnmount,
    provide,
    inject,
  },
  { atomRenderers },
);

export const createLayoutApp = runtime.createLayoutApp;
export const DashboardApp = runtime.DashboardApp;
export const TileHost = runtime.TileHost;
export const computeGridPlacement = runtime.computeGridPlacement;

export default createLayoutApp;
