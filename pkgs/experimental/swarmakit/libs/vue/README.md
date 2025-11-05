# Vue 3 + TypeScript + Vite

<div style="text-align: center;">

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fswarmauri%2Fswarmakit%2Ftree%2Fmaster%2Flibs%2Fvue&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![NPM Version](https://img.shields.io/npm/v/%40swarmakit%2Fvue)
![npm downloads](https://img.shields.io/npm/dt/@swarmakit/vue.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build and Publish Monorepo](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml/badge.svg)](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml)
</div>

<div style="text-align: center;">

![Static Badge](https://img.shields.io/badge/Vue-%234FC08D?style=for-the-badge&logo=vuedotjs&labelColor=black)
![Static Badge](https://img.shields.io/badge/TypeScript-1D4ED8?style=for-the-badge&logo=typescript&labelColor=black)
</div>

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

## Installation

Install the `@swarmakit/vue` library through npm:

```bash
npm install @swarmakit/vue
```

### Prerequisites

Node.js and npm should be installed. You can verify installation with:

```bash
node -v
npm -v 
````

### Setting Up a Vite + Vue Project (If you haven't already)

To initialize a Vite project for Vue with TypeScript, run:

```bash
npm create vite@latest my-vue-app -- --template vue-ts
```

replacing `my-vue-app` with your project name.

Then, navigate to your project folder:

```bash
cd my-vue-app
```

### Importing Components and Basic Usage in Vue

1. **Import Components:** To use a component in your Vue application, import it from the `@swarmakit/vue` library as shown below:

    ```html
    <script setup>
        import { ComponentName } from '@swarmakit/vue'
    </script>
    ```

2. **Example Usage in your Vue Template:** Use the imported component within your Vue template:

   ```html
   <template>
        <ComponentName :prop1='value' />
   <template>
   ```

>**Available Components:** Swarmakit Vue includes a vast library of components. See the full list in the [components folder on GitHub](https://github.com/swarmauri/swarmakit/tree/master/libs/vue/src/components).
