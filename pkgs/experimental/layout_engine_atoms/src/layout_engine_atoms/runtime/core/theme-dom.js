import { normalizeTheme } from "./theme.js";

export function createDocumentThemeApplier() {
  if (typeof document === "undefined") {
    return () => {};
  }

  const rootEl = document.documentElement;
  const bodyEl = document.body;
  const appliedTokens = new Set();

  return function apply(theme) {
    const normalized = normalizeTheme(theme);
    const tokens = normalized.tokens ?? {};
    const style = normalized.style ?? {};

    for (const token of appliedTokens) {
      if (!(token in tokens)) {
        rootEl.style.removeProperty(`--le-${token}`);
        bodyEl.style.removeProperty(`--le-${token}`);
      }
    }
    appliedTokens.clear();

    for (const [token, value] of Object.entries(tokens)) {
      const cssVar = `--le-${token}`;
      rootEl.style.setProperty(cssVar, String(value));
      bodyEl.style.setProperty(cssVar, String(value));
      appliedTokens.add(token);
    }

    if (tokens["color-surface"]) {
      bodyEl.style.backgroundColor = String(tokens["color-surface"]);
    }
    if (style.background || style.backgroundColor) {
      const background = style.background ?? style.backgroundColor;
      bodyEl.style.background = String(background);
    }
    if (style.color) {
      bodyEl.style.color = String(style.color);
    } else if (tokens["color-text-primary"]) {
      bodyEl.style.color = String(tokens["color-text-primary"]);
    }
    const colorScheme =
      style["color-scheme"] ?? style.colorScheme ?? tokens["color-scheme"];
    if (colorScheme) {
      rootEl.style.setProperty("color-scheme", String(colorScheme));
    }
  };
}
