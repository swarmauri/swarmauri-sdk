import { writable, type Readable, type Writable } from "svelte/store";
import type { LayoutManifest } from "./types";

type SiteNavigation = {
  pages: Writable<Array<{ id: string; route: string; title?: string; slots?: unknown[]; meta?: Record<string, unknown> }>>;
  activePageId: Writable<string | null>;
  basePath: Writable<string | undefined>;
  navigate: (pageId: string) => string | null;
};

function normaliseSite(manifest: LayoutManifest) {
  const site = manifest.site;
  if (!site) {
    return { pages: [], activePageId: null, basePath: undefined };
  }
  const pages = Array.isArray(site.pages)
    ? site.pages.map((page) => ({
        id: String(page?.id ?? ""),
        route: String(page?.route ?? "/"),
        title: page?.title ? String(page.title) : undefined,
        slots: Array.isArray(page?.slots) ? (page?.slots as unknown[]) : undefined,
        meta: (page?.meta as Record<string, unknown>) ?? undefined,
      }))
    : [];
  return {
    pages,
    activePageId: (site.active_page ?? (site as Record<string, unknown>)?.["activePage"]) as
      | string
      | null
      | undefined,
    basePath:
      site.navigation && typeof site.navigation === "object"
        ? ((site.navigation as Record<string, unknown>)["base_path"] as string | undefined)
        : undefined,
  };
}

export function createSiteNavigation(manifest: Readable<LayoutManifest>): SiteNavigation {
  const pages = writable<Array<{ id: string; route: string; title?: string; slots?: unknown[]; meta?: Record<string, unknown> }>>([]);
  const activePageId = writable<string | null>(null);
  const basePath = writable<string | undefined>(undefined);

  manifest.subscribe((current) => {
    const next = normaliseSite(current);
    pages.set(next.pages);
    activePageId.set(next.activePageId ?? null);
    basePath.set(next.basePath);
  });

  const navigate = (pageId: string): string | null => {
    let targetRoute: string | null = null;
    pages.update((collection) => {
      const found = collection.find((page) => page.id === pageId);
      if (!found) {
        return collection;
      }
      targetRoute = found.route;
      return collection;
    });
    if (targetRoute) {
      activePageId.set(pageId);
    }
    return targetRoute;
  };

  return {
    pages,
    activePageId,
    basePath,
    navigate,
  };
}
