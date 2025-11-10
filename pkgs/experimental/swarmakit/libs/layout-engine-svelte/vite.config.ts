import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import path from "node:path";

export default defineConfig({
  plugins: [svelte()],
  build: {
    lib: {
      entry: path.resolve(__dirname, "src/index.ts"),
      name: "LayoutEngineSvelte",
      formats: ["es"],
      fileName: "index",
    },
    rollupOptions: {
      external: ["svelte", "@swarmakit/svelte", "eventemitter3"],
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    include: ["src/__tests__/**/*.spec.ts"],
  },
});
