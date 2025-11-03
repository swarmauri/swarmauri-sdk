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
  vueStyle: pickSwarmakitStyle(),
  svelte: pickSwarmakitPath("libs/svelte/src", "libs/svelte/dist/index.esm.js"),
  react: pickSwarmakitPath("libs/react/src", "libs/react/dist/index.es.js"),
};

const quillPaths = {
  core: pickQuillStyle("quill.core.css"),
  bubble: pickQuillStyle("quill.bubble.css"),
  snow: pickQuillStyle("quill.snow.css"),
};

function pickSwarmakitPath(sourceRelative, distRelative) {
  const sourcePath = resolve(swarmakitRoot, sourceRelative);
  const distPath = resolve(swarmakitRoot, distRelative);
  if (!useSourceBuild && existsSync(distPath)) {
    return distPath;
  }
  return sourcePath;
}

function pickSwarmakitStyle() {
  const candidates = [
    resolve(swarmakitRoot, "libs/vue/dist/style.css"),
    resolve(swarmakitRoot, "libs/vue/src/style.css"),
    resolve(sdkRoot, "node_modules/@swarmakit/vue/dist/style.css"),
  ];
  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return candidates[0];
}

function pickQuillStyle(filename) {
  const candidates = [
    resolve(swarmakitRoot, `libs/vue/node_modules/quill/dist/${filename}`),
    resolve(swarmakitRoot, `node_modules/quill/dist/${filename}`),
    resolve(sdkRoot, `node_modules/quill/dist/${filename}`),
  ];
  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return candidates[0];
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
    rollupOptions: {
      output: {
        exports: "named",
      },
    },
  },
  server: {
    open: "/index.html",
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
    "process.env": "{}",
    global: "window",
  },
  resolve: {
    alias: [
      {
        find: "../core/index.js",
        replacement: resolve(rootDir, "../../core/index.js"),
      },
      {
        find: "@swarmakit/vue/dist/style.css",
        replacement: swarmakitPaths.vueStyle,
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
      {
        find: "quill/dist/quill.core.css",
        replacement: quillPaths.core,
      },
      {
        find: "quill/dist/quill.bubble.css",
        replacement: quillPaths.bubble,
      },
      {
        find: "quill/dist/quill.snow.css",
        replacement: quillPaths.snow,
      },
    ],
  },
}));
