import { reactive, watch } from "vue";
import type { LayoutManifest } from "./types";
import { useSiteNavigation } from "./site";

export type ShellRoute = {
  currentPath: string;
  params: Record<string, string>;
};

export function createShellRouter(options: {
  manifest: LayoutManifest;
  onNavigate?: (route: string) => void;
}): ShellRoute {
  const state = reactive<ShellRoute>({
    currentPath: window.location.pathname,
    params: {},
  });

  const site = useSiteNavigation(options.manifest);

  const push = (pageId: string) => {
    const route = site.navigate(pageId);
    if (!route) return;
    state.currentPath = route;
    if (options.onNavigate) {
      options.onNavigate(route);
    } else {
      window.history.pushState({}, "", route);
    }
  };

  window.addEventListener("popstate", () => {
    state.currentPath = window.location.pathname;
  });

  watch(
    () => state.currentPath,
    (next) => {
      console.debug("Shell route changed", next);
    }
  );

  return state;
}
