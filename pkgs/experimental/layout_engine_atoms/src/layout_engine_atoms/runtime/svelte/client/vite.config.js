import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { resolve, dirname } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));
const sdkRoot = resolve(rootDir, "../../../../../../");
const swarmakitRoot = resolve(sdkRoot, "swarmakit");

const useSourceBuild = process.env.SWARMKIT_BUNDLE_MODE === "src";

function pickSwarmakitPath(sourceRelative, distRelative) {
  const sourcePath = resolve(swarmakitRoot, sourceRelative);
  const distPath = resolve(swarmakitRoot, distRelative);
  if (!useSourceBuild && existsSync(distPath)) {
    return distPath;
  }
  return sourcePath;
}

const swarmakitPaths = {
  vue: pickSwarmakitPath("libs/vue/src", "libs/vue/dist/vue.js"),
  svelte: pickSwarmakitPath("libs/svelte/src", "libs/svelte/dist/index.esm.js"),
  react: pickSwarmakitPath("libs/react/src", "libs/react/dist/index.es.js"),
};

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
      {
        find: "@swarmakit/vue",
        replacement: swarmakitPaths.vue,
      },
      {
        find: "@swarmakit/svelte",
        replacement: swarmakitPaths.svelte,
      },
      {
        find: "@swarmakit/react",
        replacement: swarmakitPaths.react,
      },
    ],
  },
}));
