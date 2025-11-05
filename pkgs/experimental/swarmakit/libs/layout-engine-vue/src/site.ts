import { computed, isRef, reactive, toRefs, watchEffect, type Ref } from "vue";
import type { LayoutManifest } from "./types";

export type SiteNavigation = {
  pages: Array<{ id: string; route: string; title?: string; slots?: unknown[] }>;
  activePageId?: string | null;
  basePath?: string;
};

function normaliseSite(manifest: LayoutManifest): SiteNavigation {
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
      }))
    : [];
  return {
    pages,
    activePageId: (site.active_page ?? (site as Record<string, unknown>)?.["activePage"]) as
      | string
      | null
      | undefined,
    basePath: site.navigation && typeof site.navigation === "object"
      ? (site.navigation as Record<string, unknown>)["base_path"] as string | undefined
      : undefined,
  };
}

export function useSiteNavigation(manifest: LayoutManifest | Ref<LayoutManifest>) {
  const getManifest = (): LayoutManifest =>
    isRef<LayoutManifest>(manifest) ? manifest.value : manifest;
  const state = reactive(normaliseSite(getManifest()));

  watchEffect(() => {
    const next = normaliseSite(getManifest());
    state.pages = next.pages;
    state.activePageId = next.activePageId;
    state.basePath = next.basePath;
  });

  const activePage = computed(() =>
    state.pages.find((page) => page.id === state.activePageId) ?? null
  );

  const navigate = (pageId: string): string | null => {
    const page = state.pages.find((p) => p.id === pageId);
    if (!page) return null;
    state.activePageId = page.id;
    return page.route;
  };

  return {
    ...toRefs(state),
    activePage,
    navigate,
  };
}
