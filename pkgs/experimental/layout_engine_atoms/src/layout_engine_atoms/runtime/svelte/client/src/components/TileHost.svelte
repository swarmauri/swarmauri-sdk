<script>
  import { computeGridPlacement } from "../../core/index.js";

  export let tile;
  export let grid = null;
  export let viewport = null;
  export let components = {};
  export let baseRenderers = {};

  const componentCache = new Map();
  const dynamicLoaders = {
    "@swarmakit/svelte": () => import("@swarmakit/svelte"),
  };

  function resolveRegistry(base, custom) {
    const merged = {
      ...(base ?? {}),
      ...(custom ?? {}),
    };
    if (!merged.default && base?.default) {
      merged.default = base.default;
    }
    return merged;
  }

  function getFallbackRenderer(registry) {
    return registry?.default ?? baseRenderers?.default ?? null;
  }

  function cacheKey(atom) {
    if (!atom) {
      return null;
    }
    const mod = atom.module ?? "";
    const exp = atom.export ?? "default";
    if (!mod) {
      return null;
    }
    return `${mod}::${exp}`;
  }

  async function loadDynamicComponent(atom) {
    const key = cacheKey(atom);
    if (!key) {
      return null;
    }

    const cached = componentCache.get(key);
    if (cached) {
      if (typeof cached.then === "function") {
        return cached;
      }
      return cached;
    }

    const loaderFn = dynamicLoaders?.[atom.module];
    if (!loaderFn) {
      componentCache.set(key, null);
      return null;
    }

    const loader = (async () => {
      try {
        const mod = await loaderFn();
        const exportName = atom.export ?? "default";
        console.debug("[TileHost] dynamic module loaded", atom.module, Object.keys(mod ?? {}));
        let candidate = mod?.[exportName];
        if (!candidate && mod?.default) {
          if (exportName === "default") {
            candidate = mod.default;
          } else if (mod.default?.[exportName]) {
            candidate = mod.default[exportName];
          }
        }
        console.debug("[TileHost] resolved candidate", exportName, !!candidate);
        const component = candidate ?? null;
        componentCache.set(key, component);
        return component;
      } catch (error) {
        console.warn(
          "[layout-engine-atoms] failed to dynamically import atom module",
          atom.module,
          error,
        );
        componentCache.set(key, null);
        return null;
      }
    })();

    componentCache.set(key, loader);
    return loader;
  }

  $: registry = resolveRegistry(baseRenderers, components);

  let resolvedRenderer = null;
  let loadToken = 0;

  $: {
    const manualRenderer = registry?.[tile?.role];
    const fallbackRenderer = getFallbackRenderer(registry);

    if (manualRenderer) {
      loadToken += 1;
      resolvedRenderer = manualRenderer;
    } else if (!tile?.atom?.module) {
      loadToken += 1;
      resolvedRenderer = fallbackRenderer;
    } else {
      const token = ++loadToken;
      resolvedRenderer = fallbackRenderer;
      Promise.resolve(loadDynamicComponent(tile.atom)).then((component) => {
        if (token !== loadToken) {
          return;
        }
        resolvedRenderer = component ?? fallbackRenderer;
      });
    }
  }

  function styleObjectToString(style) {
    if (!style) {
      return "";
    }
    return Object.entries(style)
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => {
        const kebab = key.replace(/([A-Z])/g, "-$1").toLowerCase();
        return `${kebab}: ${value}`;
      })
      .join("; ");
  }

  $: placementStyle = styleObjectToString(
    computeGridPlacement(tile?.frame, grid, viewport),
  );

  $: componentProps = {
    ...(tile?.props ?? {}),
    tile,
  };
</script>

<div class="tile" style={placementStyle}>
  {#if resolvedRenderer}
    <svelte:component this={resolvedRenderer} {...componentProps} />
  {:else}
    <div class="tile__fallback">
      No renderer registered for role "{tile?.role ?? "unknown"}"
    </div>
  {/if}
</div>
