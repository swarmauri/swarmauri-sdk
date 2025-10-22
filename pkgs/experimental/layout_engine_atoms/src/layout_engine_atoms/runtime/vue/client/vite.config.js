import { defineConfig } from "vite";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));

export default defineConfig(() => ({
  root: rootDir,
  build: {
    outDir: "dist",
    emptyOutDir: true,
    lib: {
      entry: resolve(rootDir, "src/runtime.js"),
      name: "LayoutEngineVue",
      fileName: (format) => `layout-engine-vue.${format}.js`,
      formats: ["es", "umd"],
    },
    // Vue is bundled into the library output so downstream consumers do not need
    // to provide it separately when serving the prebuilt assets.
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
    ],
  },
}));
