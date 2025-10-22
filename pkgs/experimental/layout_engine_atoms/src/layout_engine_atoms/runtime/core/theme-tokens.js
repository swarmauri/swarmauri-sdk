const spacingScale = {
  "space-0": "0px",
  "space-1": "0.25rem", // 4px baseline unit
  "space-2": "0.5rem", // 8px baseline unit
  "space-3": "0.75rem", // 12px (Swiss grid modular increment)
  "space-4": "1rem", // 16px
  "space-5": "1.5rem", // 24px
  "space-6": "2rem", // 32px
  "space-7": "3rem", // 48px
  "space-8": "4rem", // 64px
};

export const SWISS_GRID_THEME = {
  className: "le-theme-swiss-grid",
  tokens: {
    density: 1,
    ...spacingScale,
    "font-family-sans":
      '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    "font-family-mono":
      '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    "font-weight-regular": 400,
    "font-weight-medium": 500,
    "font-weight-semibold": 600,
    "font-size-xs": "clamp(0.72rem, 0.70rem + 0.18vw, 0.8rem)",
    "font-size-sm": "clamp(0.82rem, 0.79rem + 0.22vw, 0.92rem)",
    "font-size-base": "clamp(0.96rem, 0.93rem + 0.28vw, 1.05rem)",
    "font-size-lg": "clamp(1.14rem, 1.08rem + 0.36vw, 1.3rem)",
    "font-size-xl": "clamp(1.36rem, 1.26rem + 0.48vw, 1.7rem)",
    "font-size-xxl": "clamp(1.7rem, 1.54rem + 0.72vw, 2.4rem)",
    "line-height-tight": 1.25,
    "line-height-base": 1.55,
    "radius-sm": "0.5rem",
    "radius-lg": "1rem",
    "color-scheme": "dark",
    "color-surface": "#060b1a",
    "color-surface-elevated": "rgba(16, 24, 50, 0.88)",
    "color-surface-muted": "rgba(10, 15, 32, 0.65)",
    "color-border": "rgba(92, 145, 255, 0.22)",
    "color-border-strong": "rgba(92, 145, 255, 0.35)",
    "color-accent": "#5ab1ff",
    "color-accent-soft": "rgba(90, 177, 255, 0.16)",
    "color-danger-soft": "rgba(246, 102, 118, 0.18)",
    "color-text-primary": "#f6f8ff",
    "color-text-subtle": "rgba(244, 246, 255, 0.78)",
    "color-text-muted": "rgba(244, 246, 255, 0.64)",
    "shadow-elevated": "0 18px 48px -24px rgba(8, 12, 32, 0.6)",
    "backdrop-gradient":
      "radial-gradient(circle at 20% -10%, rgba(65, 96, 210, 0.35), transparent 58%), radial-gradient(circle at 80% 0%, rgba(12, 108, 210, 0.22), transparent 60%)",
    "grid-max-width": "1240px",
    "grid-column-min": "240px",
    "grid-column-gap": "var(--le-space-5)",
    "grid-row-gap": "calc(var(--le-space-5) * 1.1)",
    "grid-row-min": "15rem",
    "viewport-padding-x": "var(--le-space-6)",
    "viewport-padding-y": "var(--le-space-7)",
    "breakpoint-lg": "1280px",
    "breakpoint-md": "960px",
    "breakpoint-sm": "720px",
  },
  style: {
    background: "var(--le-color-surface)",
    color: "var(--le-color-text-primary)",
  },
};
