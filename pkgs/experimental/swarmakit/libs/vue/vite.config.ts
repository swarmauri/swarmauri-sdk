import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import dts from 'vite-plugin-dts';
import { resolve } from 'path';


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    dts({
      outDir: 'dist',
      insertTypesEntry: true,
      include: ['src/**/*.ts', 'src/**/*.tsx', 'src/**/*.vue'],
      tsconfigPath: './tsconfig.app.json',
    }),
  ],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'SwarmakitVue',
      formats: ['es', 'umd'],
    },
    rollupOptions: {
      external: ['vue'],
      output: [
        {
          format: 'es',
          entryFileNames: 'vue.js',
          globals: {
            vue: 'Vue',
          },
        },
        {
          format: 'umd',
          name: 'SwarmakitVue',
          entryFileNames: 'vue.umd.cjs',
          globals: {
            vue: 'Vue',
          },
        },
      ],
    },
  },
});
