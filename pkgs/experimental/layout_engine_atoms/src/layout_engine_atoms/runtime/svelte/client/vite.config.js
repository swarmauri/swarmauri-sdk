import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));

export default defineConfig(() => ({
  root: rootDir,
  plugins: [
    svelte({
      emitCss: false,
      compilerOptions: {
        dev: false,
        css: "injected",
        compatibility: {
          componentApi: 4,
        },
      },
    }),
  ],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
    lib: {
      entry: resolve(rootDir, "src/runtime.js"),
      name: "LayoutEngineSvelte",
      fileName: (format) => `layout-engine-svelte.${format}.js`,
      formats: ["es", "umd"],
    },
    rollupOptions: {
      // Keep bundled output self-contained like the Vue runtime.
      external: [],
    },
  },
  server: {
    open: "/index.html",
  },
  resolve: {
    alias: [
      {
        find: "../core/index.js",
        replacement: resolve(rootDir, "../../core/index.js"),
      },
      {
        find: "../../core/index.js",
        replacement: resolve(rootDir, "../../core/index.js"),
      },
    ],
  },
}));
