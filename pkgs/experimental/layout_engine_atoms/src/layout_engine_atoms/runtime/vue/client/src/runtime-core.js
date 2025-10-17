import { createAtomRenderers } from "./atom-renderers.js";

function normalizeTheme(input = {}) {
  if (!input) {
    return { className: "", style: {}, tokens: {} };
  }
  return {
    className: input.className ?? "",
    style: { ...(input.style ?? {}) },
    tokens: { ...(input.tokens ?? {}) },
  };
}

function mergeTheme(base, patch) {
  const output = normalizeTheme(base);
  if (!patch) {
    return output;
  }
  const addition = normalizeTheme(patch);
  if (addition.className) {
    output.className = [output.className, addition.className]
      .filter(Boolean)
      .join(" ");
  }
  Object.assign(output.style, addition.style);
  Object.assign(output.tokens, addition.tokens);
  return output;
}

function matchesPageId(page, identifier) {
  if (identifier === undefined || identifier === null) {
    return false;
  }
  const id = page?.id ?? page?.slug ?? page?.name;
  return id !== undefined && String(id) === String(identifier);
}

function resolveManifestPage(manifest, requestedId, resolver) {
  const pages = Array.isArray(manifest?.pages) ? manifest.pages : [];
  if (!pages.length) {
    return null;
  }

  const attempt = (candidate) => {
    if (candidate === undefined || candidate === null) {
      return null;
    }
    if (typeof candidate === "string" || typeof candidate === "number") {
      return pages.find((page) => matchesPageId(page, candidate)) ?? null;
    }
    if (typeof candidate === "object") {
      if (candidate.id !== undefined || candidate.slug !== undefined) {
        return attempt(candidate.id ?? candidate.slug);
      }
      return candidate;
    }
    return null;
  };

  const fromResolver = resolver ? attempt(resolver(manifest, requestedId)) : null;
  if (fromResolver) {
    return fromResolver;
  }

  const fromRequested = attempt(requestedId);
  if (fromRequested) {
    return fromRequested;
  }

  return pages[0] ?? null;
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

export function createRuntime(vue, options = {}) {
  const {
    computed,
    createApp,
    defineComponent,
    h,
    reactive,
    ref,
    watch,
  } = vue;
  if (!computed || !createApp || !defineComponent || !h || !reactive || !ref || !watch) {
    throw new Error("createRuntime requires Vue composition API exports");
  }

  const defaultRenderers = createAtomRenderers({ computed, defineComponent, h });
  const rendererOverrides = options.atomRenderers ?? {};
  const baseRenderers = {
    ...defaultRenderers,
    ...rendererOverrides,
  };
  if (!baseRenderers.default) {
    baseRenderers.default = defaultRenderers.default;
  }

  const defaultTheme = normalizeTheme(options.theme);

  const TileHost = defineComponent({
    name: "LayoutEngineTileHost",
    props: {
      tile: { type: Object, required: true },
      grid: { type: Object, required: false, default: null },
      viewport: { type: Object, required: false, default: null },
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
      theme: {
        type: Object,
        default: () => ({}),
      },
      initialPageId: {
        type: [String, Number],
        default: null,
      },
      pageId: {
        type: [String, Number],
        default: null,
      },
      resolvePage: {
        type: Function,
        default: null,
      },
      onError: {
        type: Function,
        default: null,
      },
      onReady: {
        type: Function,
        default: null,
      },
      onPageChange: {
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

      const pageState = reactive({
        id: props.pageId ?? props.initialPageId ?? null,
      });
      const pendingPageId = ref(pageState.id);

      const themeState = reactive(normalizeTheme(defaultTheme));

      function resetTheme(base = defaultTheme) {
        const normalized = normalizeTheme(base);
        themeState.className = normalized.className;

        for (const key of Object.keys(themeState.style)) {
          delete themeState.style[key];
        }
        Object.assign(themeState.style, normalized.style);

        for (const key of Object.keys(themeState.tokens)) {
          delete themeState.tokens[key];
        }
        Object.assign(themeState.tokens, normalized.tokens);
      }

      function applyThemePatch(patch, { replace = false } = {}) {
        if (replace || patch?.reset) {
          resetTheme();
        }
        if (!patch) {
          return themeState;
        }
        if (patch.className !== undefined) {
          themeState.className = patch.className ?? "";
        }
        if (patch.style) {
          Object.assign(themeState.style, patch.style);
        }
        if (patch.tokens) {
          Object.assign(themeState.tokens, patch.tokens);
        }
        return themeState;
      }

      applyThemePatch(props.theme, { replace: true });

      watch(
        () => props.theme,
        (next) => {
          applyThemePatch(next, { replace: true });
        },
        { deep: true }
      );

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

      function syncPage(manifest) {
        const nextPage = resolveManifestPage(
          manifest,
          pendingPageId.value ?? pageState.id ?? props.pageId ?? props.initialPageId,
          props.resolvePage,
        );
        if (nextPage) {
          pageState.id = nextPage.id ?? nextPage.slug ?? nextPage.name ?? null;
          pendingPageId.value = pageState.id;
          props.onPageChange?.(pageState.id, nextPage);
        } else {
          pageState.id = null;
          pendingPageId.value = null;
          props.onPageChange?.(null, null);
        }
      }

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
          syncPage(payload);
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

      function setPage(nextPageId) {
        pendingPageId.value = nextPageId ?? null;
        if (!state.manifest) {
          return null;
        }
        const nextPage = resolveManifestPage(
          state.manifest,
          pendingPageId.value,
          props.resolvePage,
        );
        if (nextPage) {
          pageState.id = nextPage.id ?? nextPage.slug ?? nextPage.name ?? null;
          pendingPageId.value = pageState.id;
          props.onPageChange?.(pageState.id, nextPage);
          return nextPage;
        }
        pageState.id = null;
        props.onPageChange?.(null, null);
        return null;
      }

      const view = computed(() => {
        const manifest = state.manifest;
        if (!manifest) {
          return {
            grid: null,
            tiles: [],
            viewport: null,
            page: null,
            pages: [],
          };
        }
        const page = resolveManifestPage(
          manifest,
          pageState.id ?? pendingPageId.value,
          props.resolvePage,
        );
        const tiles = (page?.tiles ?? manifest.tiles ?? []).slice();
        const grid = page?.grid ?? manifest.grid ?? null;
        const viewport = page?.viewport ?? manifest.viewport ?? null;
        return {
          grid,
          tiles,
          viewport,
          page: page ?? null,
          pages: Array.isArray(manifest.pages) ? manifest.pages : [],
        };
      });

      const gridStyle = computed(() => {
        const grid = view.value.grid;
        if (!grid) {
          return {};
        }
        const columnCount = grid.columns?.length ?? 1;
        return {
          gridTemplateColumns: `repeat(${columnCount}, minmax(200px, 1fr))`,
          gap: `${grid.gap_y}px ${grid.gap_x}px`,
        };
      });

      const summary = computed(() => {
        const tiles = view.value.tiles ?? [];
        const roles = new Set(tiles.map((tile) => tile.role));
        return {
          tileCount: tiles.length,
          roleCount: roles.size,
        };
      });

      const runtimeTheme = computed(() => {
        const base = normalizeTheme(themeState);
        return mergeTheme(base, view.value.page?.theme);
      });

      const rootClass = computed(() => {
        const classes = ["dashboard"];
        if (runtimeTheme.value.className) {
          runtimeTheme.value.className
            .split(/\s+/)
            .filter(Boolean)
            .forEach((name) => classes.push(name));
        }
        return classes;
      });

      const rootStyle = computed(() => {
        const style = { ...(runtimeTheme.value.style ?? {}) };
        const tokens = runtimeTheme.value.tokens ?? {};
        for (const [token, value] of Object.entries(tokens)) {
          style[`--le-${token}`] = value;
        }
        return style;
      });

      watch(
        () => props.pageId,
        (next) => {
          if (next !== undefined && next !== null) {
            setPage(next);
          }
        },
      );

      watch(
        () => props.initialPageId,
        (next) => {
          if (!pageState.id && next !== undefined && next !== null) {
            setPage(next);
          }
        },
      );

      watch(
        resolvedManifestUrl,
        () => {
          fetchManifest();
        },
        { immediate: true },
      );

      function setTheme(patch, options) {
        applyThemePatch(patch, options);
      }

      expose({
        refresh: fetchManifest,
        state,
        setPage,
        setTheme,
        theme: themeState,
      });

      return {
        state,
        view,
        gridStyle,
        summary,
        mergedComponents,
        rootClass,
        rootStyle,
        runtimeTheme,
        setPage,
        setTheme,
      };
    },
    template: `
      <div :class="rootClass" :style="rootStyle">
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
              Viewport: {{ view.viewport?.width ?? state.manifest?.viewport?.width ?? "—" }}×{{ view.viewport?.height ?? state.manifest?.viewport?.height ?? "—" }}
            </span>
            <span aria-hidden="true">•</span>
            <span>Generated by layout-engine</span>
          </div>
        </header>

        <div v-if="state.loading" class="dashboard__meta">Fetching manifest…</div>
        <div v-else-if="state.error" class="dashboard__meta">
          Failed to load manifest: {{ state.error.message }}
        </div>

        <section
          v-if="state.manifest && !state.error && view.tiles.length"
          class="dashboard-grid"
          :style="gridStyle"
        >
          <TileHost
            v-for="tile in view.tiles"
            :key="tile.id"
            :tile="tile"
            :grid="view.grid"
            :viewport="view.viewport || state.manifest?.viewport"
            :components="mergedComponents"
          />
        </section>

        <div v-else-if="state.manifest && !state.error" class="dashboard__meta">
          No tiles available for the selected page.
        </div>
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
    const onPageChange = userOptions.onPageChange ?? null;
    const resolvePage = userOptions.resolvePage ?? options.pageResolver ?? null;
    const initialPageId = userOptions.initialPageId ?? null;
    const controlledPageId = userOptions.pageId ?? null;
    const themeOption = userOptions.theme ?? null;

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
      theme: themeOption,
      initialPageId,
      pageId: controlledPageId,
      resolvePage,
      onError,
      onReady,
      onPageChange,
    };

    const app = createApp(DashboardApp, props);

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
      setPage(pageId) {
        vm.setPage?.(pageId);
      },
      setTheme(patch, opts) {
        vm.setTheme?.(patch, opts);
      },
      get state() {
        return vm.state;
      },
      get theme() {
        return vm.runtimeTheme;
      },
      unmount() {
        app.unmount();
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
