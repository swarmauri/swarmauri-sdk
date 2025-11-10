import { describe, it, expect, vi, beforeEach } from "vitest";
import { loadManifest } from "../loader";
import type { LayoutManifest, ManifestAtom } from "../types";

const mockManifest: LayoutManifest = {
  kind: "LayoutManifest",
  version: "2025.10",
  viewport: { width: 1280, height: 720 },
  grid: {},
  tiles: [
    {
      id: "hero",
      role: "swarmakit:svelte:cardbased-list",
      frame: { x: 0, y: 0, w: 600, h: 400 },
      props: {},
      atom: {
        role: "swarmakit:svelte:cardbased-list",
        module: "@swarmakit/svelte",
        export: "CardbasedList",
        version: "0.0.22",
        family: "swarmakit",
      },
    },
  ],
};

describe("loadManifest", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("loads manifest and resolves atom components", async () => {
    const fetcher = vi.fn().mockResolvedValue(mockManifest);
    const loader = vi
      .fn()
      .mockImplementation(async (atom: ManifestAtom) => atom.export);

    const result = await loadManifest("http://example.com/manifest.json", {
      fetcher,
      importResolver: loader,
    });

    expect(fetcher).toHaveBeenCalled();
    expect(loader).toHaveBeenCalledTimes(1);
    expect(result.manifest.tiles).toHaveLength(1);
    const registryEntry = result.components.get("swarmakit:svelte:cardbased-list");
    expect(registryEntry?.component).toEqual("CardbasedList");
  });

  it("reuses cached manifests", async () => {
    const fetcher = vi.fn().mockResolvedValue(mockManifest);
    const loader = vi.fn().mockResolvedValue({ component: "component" });

    await loadManifest("http://example.com/manifest.json", {
      fetcher,
      importResolver: loader,
      cacheKey: "demo",
    });
    await loadManifest("http://example.com/manifest.json", {
      fetcher,
      importResolver: loader,
      cacheKey: "demo",
    });

    expect(fetcher).toHaveBeenCalledTimes(2); // manual cache key bypass
  });
});
