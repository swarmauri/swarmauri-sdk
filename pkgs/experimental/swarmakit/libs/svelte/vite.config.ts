import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

export default defineConfig({
  plugins: [svelte()],
  resolve: {
    alias: {
      '@components': '/src/components',  // Example alias
    },
  },
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'SwarmaKitSvelte',
      formats: ['es', 'cjs'],
      fileName: (format) => `index.${format === 'es' ? 'esm' : 'cjs'}.js`
    },
    rollupOptions: {
      // Keep svelte external to avoid dual runtime instances
      external: ['svelte', 'svelte/internal'],
      output: {
        globals: {
          svelte: 'svelte'
        }
      }
    }
  }
});
