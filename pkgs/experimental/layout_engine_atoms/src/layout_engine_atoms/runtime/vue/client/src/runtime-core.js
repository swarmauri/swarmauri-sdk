import { createAtomRenderers } from "./atom-renderers.js";

/**
 * Create a runtime abstraction around the Vue exports and atom registry.
 *
 * @param {{ computed: Function, createApp: Function, defineComponent: Function, h: Function, reactive: Function, watch: Function }} vue
 *        The Vue module (or compatible composition API exports).
 * @param {{ atomRenderers?: Record<string, any> }} options
 */
export function createRuntime(vue, options = {}) {
  const { computed, createApp, defineComponent, h, reactive, watch } = vue;
  if (!computed || !createApp || !defineComponent || !reactive || !watch || !h) {
    throw new Error("createRuntime requires Vue composition API exports");
  }

  const defaultRenderers = createAtomRenderers({ computed, defineComponent, h });

  const baseRenderers = {
    ...defaultRenderers,
    ...(options.atomRenderers ?? {}),
  };

  if (!baseRenderers.default) {
    baseRenderers.default = defaultRenderers.default;
  }

  function computeGridPlacement(frame, grid, viewport) {
    if (!grid || !frame) {
      return {};
    }

    const columnCount = grid.columns?.length ?? 1;
    const totalGap = grid.gap_x * Math.max(columnCount - 1, 0);
    const averageColumnWidth =
      columnCount > 0 ? (viewport.width - totalGap) / columnCount : viewport.width;
    const stepX = averageColumnWidth + grid.gap_x;
    const stepY = grid.row_height + grid.gap_y;

    const columnStart = Math.round(frame.x / stepX) + 1;
    const rowStart = Math.round(frame.y / stepY) + 1;
    const columnSpan = Math.max(
      1,
      Math.min(
        columnCount,
        Math.round(frame.w / stepX) || 1,
        columnCount - columnStart + 1,
      ),
    );
    const rowSpan = Math.max(1, Math.round(frame.h / grid.row_height) || 1);

    return {
      gridColumn: `${columnStart} / span ${columnSpan}`,
      gridRow: `${rowStart} / span ${rowSpan}`,
    };
  }

  const TileHost = defineComponent({
    name: "LayoutEngineTileHost",
    props: {
      tile: { type: Object, required: true },
      grid: { type: Object, required: true },
      viewport: { type: Object, required: true },
      components: { type: Object, required: true },
    },
    setup(props) {
      const renderer = computed(() => {
        const registry = props.components ?? baseRenderers;
        return (
          registry[props.tile.role] ??
          registry.default ??
          baseRenderers.default
        );
      });

      const placement = computed(() =>
        computeGridPlacement(props.tile.frame, props.grid, props.viewport),
      );

      return {
        renderer,
        placement,
      };
    },
    template: `
      <div class="tile" :style="placement">
        <component :is="renderer" :tile="tile" />
      </div>
    `,
  });

  const DashboardApp = defineComponent({
    name: "LayoutEngineDashboard",
    components: { TileHost },
    props: {
      manifestUrl: { type: String, default: "" },
      fetchOptions: {
        type: Object,
        default: () => ({}),
      },
      components: {
        type: Object,
        default: () => ({}),
      },
      onError: {
        type: Function,
        default: null,
      },
      onReady: {
        type: Function,
        default: null,
      },
    },
    setup(props, { expose }) {
      const state = reactive({
        manifest: null,
        loading: true,
        error: null,
      });

      const mergedComponents = computed(() => {
        const custom = props.components ?? {};
        const combined = { ...baseRenderers, ...custom };
        if (!combined.default && baseRenderers.default) {
          combined.default = baseRenderers.default;
        }
        return combined;
      });

      const resolvedManifestUrl = computed(() => {
        if (props.manifestUrl) {
          return props.manifestUrl;
        }
        if (typeof window !== "undefined" && window) {
          return (
            window.__LE_MANIFEST_URL__ ??
            new URL("manifest.json", window.location.href).toString()
          );
        }
        return "manifest.json";
      });

      const gridStyle = computed(() => {
        const manifestGrid = state.manifest?.grid;
        if (!manifestGrid) {
          return {};
        }
        const columnCount = manifestGrid.columns?.length ?? 1;
        return {
          gridTemplateColumns: `repeat(${columnCount}, minmax(200px, 1fr))`,
          gap: `${manifestGrid.gap_y}px ${manifestGrid.gap_x}px`,
        };
      });

      const summary = computed(() => {
        const tiles = state.manifest?.tiles ?? [];
        const roles = new Set(tiles.map((tile) => tile.role));
        return {
          tileCount: tiles.length,
          roleCount: roles.size,
        };
      });

      async function fetchManifest() {
        state.loading = true;
        try {
          const response = await fetch(
            resolvedManifestUrl.value,
            props.fetchOptions ?? {},
          );
          if (!response.ok) {
            throw new Error(
              `Failed to fetch manifest (${response.status} ${response.statusText})`,
            );
          }
          const payload = await response.json();
          state.manifest = payload;
          state.error = null;
          props.onReady?.(payload);
        } catch (error) {
          const err =
            error instanceof Error ? error : new Error(String(error));
          state.error = err;
          props.onError?.(err);
        } finally {
          state.loading = false;
        }
      }

      watch(
        resolvedManifestUrl,
        () => {
          fetchManifest();
        },
        { immediate: true },
      );

      expose({
        refresh: fetchManifest,
        state,
      });

      return {
        state,
        gridStyle,
        summary,
        mergedComponents,
      };
    },
    template: `
      <div class="dashboard">
        <header class="dashboard__header">
          <div>
            <h1 class="dashboard__title">Revenue Operations Overview</h1>
            <p class="dashboard__meta">
              <span>Manifest v{{ state.manifest?.version ?? "—" }}</span>
              <span aria-hidden="true">•</span>
              <span>Tiles: {{ summary.tileCount }}</span>
              <span aria-hidden="true">•</span>
              <span>Roles: {{ summary.roleCount }}</span>
            </p>
          </div>
          <div class="dashboard__meta">
            <span>
              Viewport:
              {{ state.manifest?.viewport?.width ?? "—" }}×{{ state.manifest?.viewport?.height ?? "—" }}
            </span>
            <span aria-hidden="true">•</span>
            <span>Generated by layout-engine</span>
          </div>
        </header>

        <div v-if="state.loading" class="dashboard__meta">
          Fetching manifest…
        </div>
        <div v-else-if="state.error" class="dashboard__meta">
          Failed to load manifest: {{ state.error.message }}
        </div>

        <section
          v-if="state.manifest && !state.error"
          class="dashboard-grid"
          :style="gridStyle"
        >
          <TileHost
            v-for="tile in state.manifest.tiles"
            :key="tile.id"
            :tile="tile"
            :grid="state.manifest.grid"
            :viewport="state.manifest.viewport"
            :components="mergedComponents"
          />
        </section>
      </div>
    `,
  });

  function createLayoutApp(userOptions = {}) {
    const targetSelector = userOptions.target ?? "#app";
    const manifestUrl = userOptions.manifestUrl ?? "";
    const componentsOverride = userOptions.components ?? {};
    const fetchOptions = userOptions.fetchOptions ?? {};
    const onError = userOptions.onError ?? null;
    const onReady = userOptions.onReady ?? null;

    const combinedComponents = {
      ...baseRenderers,
      ...componentsOverride,
    };
    if (!combinedComponents.default && baseRenderers.default) {
      combinedComponents.default = baseRenderers.default;
    }

    const props = {
      manifestUrl,
      fetchOptions,
      components: combinedComponents,
      onError,
      onReady,
    };

    const app = createApp(DashboardApp, props);

    if (onError) {
      app.config.errorHandler = (err, instance, info) => {
        onError(err, info);
      };
    }

    const mountTarget =
      typeof targetSelector === "string"
        ? typeof document !== "undefined"
          ? document.querySelector(targetSelector)
          : null
        : targetSelector;

    if (!mountTarget) {
      throw new Error(
        `Unable to find mount target "${targetSelector}". Ensure the element exists.`,
      );
    }

    const vm = app.mount(mountTarget);

    return {
      app,
      refresh() {
        vm.refresh?.();
      },
      unmount() {
        app.unmount();
      },
      get state() {
        return vm.state;
      },
    };
  }

  return {
    createLayoutApp,
    DashboardApp,
    TileHost,
    computeGridPlacement,
  };
}
