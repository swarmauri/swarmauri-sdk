import { defineConfig } from "vite";
import { resolve, dirname } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));
const sdkRoot = resolve(rootDir, "../../../../../../");
const swarmakitRoot = resolve(sdkRoot, "swarmakit");

const useSourceBuild = process.env.SWARMKIT_BUNDLE_MODE === "src";

const swarmakitPaths = {
  vue: pickSwarmakitPath("libs/vue/src", "libs/vue/dist/vue.js"),
  svelte: pickSwarmakitPath("libs/svelte/src", "libs/svelte/dist/index.esm.js"),
  react: pickSwarmakitPath("libs/react/src", "libs/react/dist/index.es.js"),
};

function pickSwarmakitPath(sourceRelative, distRelative) {
  const sourcePath = resolve(swarmakitRoot, sourceRelative);
  const distPath = resolve(swarmakitRoot, distRelative);
  if (!useSourceBuild && existsSync(distPath)) {
    return distPath;
  }
  return sourcePath;
}

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
