import { writable } from "svelte/store";

export type ShellRoute = {
  currentPath: string;
  params: Record<string, string>;
};

export function createShellRouter(options: {
  onNavigate?: (route: string) => void;
}): ShellRoute {
  const state = writable<ShellRoute>({
    currentPath: typeof window !== "undefined" ? window.location.pathname : "/",
    params: {},
  });

  const push = (route: string) => {
    state.update((current) => ({ ...current, currentPath: route }));
    if (options.onNavigate) {
      options.onNavigate(route);
    } else if (typeof window !== "undefined") {
      window.history.pushState({}, "", route);
    }
  };

  if (typeof window !== "undefined") {
    window.addEventListener("popstate", () => {
      state.update((current) => ({ ...current, currentPath: window.location.pathname }));
    });
  }

  return {
    get currentPath() {
      let value = "/";
      state.subscribe((data) => {
        value = data.currentPath;
      })();
      return value;
    },
    get params() {
      let value: Record<string, string> = {};
      state.subscribe((data) => {
        value = data.params;
      })();
      return value;
    },
    push,
  } as unknown as ShellRoute;
}
