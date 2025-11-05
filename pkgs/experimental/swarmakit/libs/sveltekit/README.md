# create-svelte

<div style="text-align: center;">

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fswarmauri%2Fswarmakit%2Ftree%2Fmaster%2Flibs%2Fsveltekit&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![NPM Version](https://img.shields.io/npm/v/%40swarmakit%2Fsveltekit)
![npm downloads](https://img.shields.io/npm/dt/@swarmakit/sveltekit.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build and Publish Monorepo](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml/badge.svg)](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml)
</div>

<div style="text-align: center;">

![Static Badge](https://img.shields.io/badge/Svelte-FF3E00?style=for-the-badge&logo=svelte&labelColor=black)
![Static Badge](https://img.shields.io/badge/TypeScript-1D4ED8?style=for-the-badge&logo=typescript&labelColor=black)
</div>

Everything you need to build a Svelte project, powered by [`create-svelte`](https://github.com/sveltejs/kit/tree/main/packages/create-svelte).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```bash
# create a new project in the current directory
npm create svelte@latest

# create a new project in my-app
npm create svelte@latest my-app
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.

## Installation

Install the `@swarmakit/sveltekit` library through npm:

```bash
npm install @swarmakit/sveltekit
```

### Prerequisites

Node.js and npm should be installed. You can verify installation with:

```bash
node -v
npm -v 
```

### Importing Components and Basic Usage in Svelte

1. **Import Components:** To use a component in your Svelte files, import it from the `@swarmakit/sveltekit` library as shown below:

    ```html
    <script>
        import { ComponentName } from '@swarmakit/sveltekit'
    </script>
    ```

2. **Example Usage in a Svelte File:** Use the imported component within your Svelte file:

   ```html
    <script>
        import { ComponentName } from '@swarmakit/svelte';

        const exampleProp = "Example text";
    </script>

    <main>
        <ComponentName propName={exampleProp} />
    </main>
   ```

> **Available Components:** Swarmakit Sveltekit includes a vast library of components. See the full list in the [components folder on GitHub](https://github.com/swarmauri/swarmakit/tree/master/libs/sveltekit/src/components).

