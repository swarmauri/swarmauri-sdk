import { describe, expect, it, vi } from "vitest";
import { loadManifest } from "../src/loader";
import type { LayoutManifest, ManifestAtom } from "../src/types";

const manifest: LayoutManifest = {
  kind: "layout_manifest",
  version: "2025.10",
  etag: "abc123",
  viewport: { width: 800, height: 600 },
  grid: {},
  tiles: [
    {
      id: "hero",
      role: "swarmakit:vue:hero",
      frame: { x: 0, y: 0, w: 800, h: 300 },
      props: {},
      atom: {
        role: "swarmakit:vue:hero",
        module: "@swarmakit/vue",
        export: "HeroCard",
        version: "0.0.22",
        family: "swarmakit",
      } as ManifestAtom,
    },
  ],
};

describe("loadManifest", () => {
  it("loads manifest and caches components", async () => {
    const fetcher = vi.fn().mockResolvedValue(manifest);
    const resolver = vi.fn().mockResolvedValue({ name: "HeroCard" });

    const result = await loadManifest("test", { fetcher, importResolver: resolver });

    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(resolver).toHaveBeenCalledTimes(1);
    expect(result.components.size).toBe(1);

    resolver.mockClear();

    await loadManifest("test", { fetcher, importResolver: resolver });
    expect(resolver).not.toHaveBeenCalled();
  });
});
