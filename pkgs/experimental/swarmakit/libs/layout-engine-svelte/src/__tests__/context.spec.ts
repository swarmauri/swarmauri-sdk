import { describe, it, expect, vi } from "vitest";
import { writable } from "svelte/store";

const contextMap = new Map();
vi.mock("svelte", () => ({
  getContext: (key: symbol) => contextMap.get(key),
  setContext: (key: symbol, value: unknown) => {
    contextMap.set(key, value);
  },
}));

import {
  createLayoutContext,
  useManifestStore,
  useRegistryStore,
} from "../context";
import type { LayoutManifest, AtomRegistryMap } from "../types";

describe("layout context", () => {
  it("provides manifesto and registry stores", () => {
    contextMap.clear();
    const manifestStore = writable<LayoutManifest>({
      kind: "LayoutManifest",
      version: "test",
      viewport: { width: 0, height: 0 },
      grid: {},
      tiles: [],
    });
    const registryStore = writable<AtomRegistryMap>(new Map());

    createLayoutContext({ manifest: manifestStore, registry: registryStore });
    expect(useManifestStore()).toBe(manifestStore);
    expect(useRegistryStore()).toBe(registryStore);
  });
});
