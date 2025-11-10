import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import path from "node:path";

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: "dist/bootstrap",
    emptyOutDir: false,
    rollupOptions: {
      input: {
        "mpa-bootstrap": path.resolve(__dirname, "src/bootstrap/mpa.ts"),
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: "[name][extname]",
      },
    },
  },
});
