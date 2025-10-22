# Swiss Grid Theme Tokens

The Vue runtime ships with a default theme derived from Swiss graphic grid
principles. The theme codifies spacing, typography, and layout values so every
target (HTML, PDF, SVG) can share a unified rhythm.

## Baseline

- **Base unit:** 4 px (0.25 rem) modular scale. All spacing tokens are integer
  multiples of this unit, aligning with Swiss grid gutter patterns.
- **Column structure:** tokenised maximum width (`--le-grid-max-width`) and
  minimum column width (`--le-grid-column-min`) allow 12-column layouts with
  consistent gutters defined via `--le-grid-column-gap` and
  `--le-grid-row-gap`.
- **Typography:** scale values (`--le-font-size-*`) follow a modular ratio to
  maintain harmonious leading across breakpoints. Line heights align to the
  baseline grid (`--le-line-height-base`, `--le-line-height-tight`).

## Token Reference

| Token | Purpose |
| ----- | ------- |
| `--le-space-0…8` | Modular spacing steps (4 px base) used for gutters, padding, and grid rhythm. |
| `--le-font-size-xs…xxl` | Responsive modular scale for headings and body copy. |
| `--le-line-height-tight/base` | Baseline-aligned leading values. |
| `--le-grid-max-width` | Swiss-grid inspired canvas width (approx. 12 columns × 80 px). |
| `--le-grid-column-min` | Minimum column width to maintain column rhythm on narrow viewports. |
| `--le-grid-column-gap` / `--le-grid-row-gap` | Primary gutters, derived from space-5 (24 px) with optical adjustment. |
| `--le-viewport-padding-x/y` | Canvas padding mirroring Swiss margin ratios. |
| `--le-breakpoint-lg/md/sm` | Layout breakpoints matching common Swiss editorial breakpoints. |
| `--le-color-*` | Core palette values (surface, text, accent) tuned for high contrast dashboard displays. |
| `--le-radius-sm/lg` | Soft radius system to echo print-era Swiss rounded forms without breaking grid discipline. |
| `--le-shadow-elevated` | Single elevation preset for tiles, aligned with modern Swiss minimalism. |

These tokens are defined in `runtime/core/theme-tokens.js` and applied
automatically by the runtime. Consumers can extend or override them via theme
patches while preserving the Swiss grid foundation (`setTheme`, manifest page
themes, or wrapper options).
