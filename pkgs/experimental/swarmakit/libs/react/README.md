# React + TypeScript + Vite

<div style="text-align: center;">

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fswarmauri%2Fswarmakit%2Ftree%2Fmaster%2Flibs%2Freact&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![NPM Version](https://img.shields.io/npm/v/%40swarmakit%2Freact)
![npm downloads](https://img.shields.io/npm/dt/@swarmakit/react.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build and Publish Monorepo](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml/badge.svg)](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml)
</div>

<div style="text-align: center;">

![Static Badge](https://img.shields.io/badge/React-61DBFB?style=for-the-badge&logo=react&labelColor=black)
![Static Badge](https://img.shields.io/badge/TypeScript-1D4ED8?style=for-the-badge&logo=typescript&labelColor=black)
</div>

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default tseslint.config({
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

- Replace `tseslint.configs.recommended` to `tseslint.configs.recommendedTypeChecked` or `tseslint.configs.strictTypeChecked`
- Optionally add `...tseslint.configs.stylisticTypeChecked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and update the config:

```js
// eslint.config.js
import react from 'eslint-plugin-react'

export default tseslint.config({
  // Set the react version
  settings: { react: { version: '18.3' } },
  plugins: {
    // Add the react plugin
    react,
  },
  rules: {
    // other rules...
    // Enable its recommended rules
    ...react.configs.recommended.rules,
    ...react.configs['jsx-runtime'].rules,
  },
})
```

## Installation

Install the `@swarmakit/react` library through npm:

```bash
npm install @swarmakit/react
```

### Prerequisites

Node.js and npm should be installed. You can verify installation with:

```bash
node -v
npm -v 
````

### Setting Up a Vite + React Project (If you haven't already)

To initialize a Vite project for React with TypeScript, run:

```bash
npm create vite@latest my-react-app -- --template react-ts
```

replacing `my-react-app` with your project name.

Then, navigate to your project folder:

```bash
cd my-react-app
```

### Importing Components and Basic Usage in React

1. **Import Components:** To use a component in your application, import it from the `@swarmakit/react` library as shown below:

    ```javascript
    import { ComponentName } from '@swarmakit/react'
    ```

2. **Example Usage in JSX:** Use the imported component within your React component:

   ```jsx
   function App() {
    return (
      <div>
        <ComponentName prop1='value' />
      </div>
    )
   }
   ```

> **Available Components:** Swarmakit React includes a vast library of components. See the full list in the [stories folder on GitHub](https://github.com/swarmauri/swarmakit/tree/master/libs/react/src/stories).
