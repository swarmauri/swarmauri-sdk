import { markRaw } from "vue";
import type {
  LayoutManifest,
  ManifestAtom,
  ManifestLoaderOptions,
  AtomRegistryMap,
} from "./types";

const manifestCache = new Map<string, LayoutManifest>();
const componentCache = new Map<string, AtomRegistryMap>();

async function defaultFetcher(url: string): Promise<LayoutManifest> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch manifest: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as LayoutManifest;
}

async function defaultImportResolver(atom: ManifestAtom): Promise<unknown> {
  if (!atom.module) {
    throw new Error(`Missing module specifier for atom ${atom.role}`);
  }
  const mod = await import(/* @vite-ignore */ atom.module);
  const exportName = atom.export ?? "default";
  if (!(exportName in mod)) {
    throw new Error(`Export '${exportName}' not found in module ${atom.module}`);
  }
  return mod[exportName as keyof typeof mod];
}

function cacheKeyFromManifest(manifest: LayoutManifest, explicit?: string): string {
  if (explicit) return explicit;
  const version = manifest.meta?.atoms && typeof manifest.meta.atoms === "object"
    ? (manifest.meta.atoms as Record<string, unknown>)["revision"]
    : undefined;
  return String(version ?? manifest.etag ?? manifest.version ?? "default");
}

export async function loadManifest(
  manifestUrl: string,
  options: ManifestLoaderOptions = {}
): Promise<{ manifest: LayoutManifest; components: AtomRegistryMap }> {
  const fetcher = options.fetcher ?? defaultFetcher;
  const loader = options.importResolver ?? defaultImportResolver;

  const manifest = await fetcher(manifestUrl);
  const cacheKey = cacheKeyFromManifest(manifest, options.cacheKey);

  if (manifestCache.has(cacheKey)) {
    const cachedManifest = manifestCache.get(cacheKey)!;
    const cachedComponents = componentCache.get(cacheKey) ?? new Map();
    return { manifest: cachedManifest, components: cachedComponents };
  }

  const registry = new Map<string, { component: unknown; atom: ManifestAtom }>();
  const swarmaAtoms = manifest.tiles
    .map((tile) => tile.atom)
    .filter((atom): atom is ManifestAtom => Boolean(atom && atom.family === "swarmakit"));

  for (const atom of swarmaAtoms) {
    if (registry.has(atom.role)) continue;
    const component = await loader(atom);
    registry.set(atom.role, { component: markRaw(component), atom });
  }

  manifestCache.set(cacheKey, manifest);
  componentCache.set(cacheKey, registry);

  return { manifest, components: registry };
}
