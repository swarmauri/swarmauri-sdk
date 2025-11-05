# Svelte + TypeScript + Vite

<div style="text-align: center;">

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fswarmauri%2Fswarmakit%2Ftree%2Fmaster%2Flibs%2Fsvelte&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![NPM Version](https://img.shields.io/npm/v/%40swarmakit%2Fsvelte)
![npm downloads](https://img.shields.io/npm/dt/@swarmakit/svelte.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build and Publish Monorepo](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml/badge.svg)](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml)

</div>

<div style="text-align: center;">

![Static Badge](https://img.shields.io/badge/Svelte-FF3E00?style=for-the-badge&logo=svelte&labelColor=black)
![Static Badge](https://img.shields.io/badge/TypeScript-1D4ED8?style=for-the-badge&logo=typescript&labelColor=black)

</div>

This template should help get you started developing with Svelte and TypeScript in Vite.

Everything you need to build a Svelte and TypeScript project, powered by [`Svelte`](https://github.com/sveltejs/kit/tree/main/packages/create-svelte).

## Installation

Install the `@swarmakit/svelte` library through npm:

```bash
npm install @swarmakit/svelte
```

### Prerequisites

Node.js and npm should be installed. You can verify installation with:

```bash
node -v
npm -v
````

### Setting Up a Vite + Svelte Project (If you haven't already)

To initialize a Vite project for Svelte with Typescript, run:

```bash
npm create vite@latest my-svelte-app -- --template svelte-ts
```

replacing `my-svelte-app` with your project name.

Then, navigate to your project folder:

```bash
cd my-svelte-app
```

### Importing Components and Basic Usage in Svelte

1. **Import Components:** To use a component in your Svelte files, import it from the `@swarmakit/svelte` library as shown below:

   ```html
   <script>
     import { ComponentName } from "@swarmakit/svelte";
   </script>
   ```

2. **Example Usage in a Svelte File:** Use the imported component within your Svelte file:

   ```html
   <script>
     import { ComponentName } from "@swarmakit/svelte";

     const exampleProp = "Example text";
   </script>

   <main>
     <ComponentName propName="{exampleProp}" />
   </main>
   ```

> **Available Components:** Swarmakit Sveltekit includes a vast library of components. See the full list in the [components folder on GitHub](https://github.com/swarmauri/swarmakit/tree/master/libs/svelte/src/components).
