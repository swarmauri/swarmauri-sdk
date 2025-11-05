export type LayoutManifest = {
  kind: string;
  version: string;
  viewport: { width: number; height: number };
  grid: Record<string, unknown>;
  tiles: Array<LayoutTile>;
  etag?: string;
  site?: {
    active_page?: string | null;
    navigation?: Record<string, unknown>;
    pages?: Array<Record<string, unknown>>;
  } | null;
  channels?: Array<ManifestChannel>;
  ws_routes?: Array<ManifestWsRoute>;
  meta?: Record<string, unknown>;
};

export type LayoutTile = {
  id: string;
  role: string;
  frame: { x: number; y: number; w: number; h: number };
  props: Record<string, unknown>;
  atom?: ManifestAtom;
};

export type ManifestAtom = {
  role: string;
  module: string;
  export: string;
  version: string;
  framework?: string;
  package?: string;
  family?: string;
  defaults?: Record<string, unknown>;
  tokens?: Record<string, unknown>;
  registry?: Record<string, unknown>;
};

export type ManifestChannel = {
  id: string;
  scope: string;
  topic: string;
  description?: string;
  payload_schema?: Record<string, unknown>;
  meta?: Record<string, unknown>;
};

export type ManifestWsRoute = {
  path: string;
  channels?: Array<string>;
  description?: string;
  meta?: Record<string, unknown>;
};

export type LoadedComponent = {
  component: unknown;
  atom: ManifestAtom;
};

export type AtomRegistryMap = Map<string, LoadedComponent>;

export type ManifestLoaderOptions = {
  cacheKey?: string;
  fetcher?: (url: string) => Promise<LayoutManifest>;
  importResolver?: (spec: ManifestAtom) => Promise<unknown>;
};
