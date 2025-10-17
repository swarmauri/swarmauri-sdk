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
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
  },
  server: {
    open: "/index.html",
  },
}));
