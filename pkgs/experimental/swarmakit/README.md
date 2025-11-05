![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div style="text-align: center;">

[![Hits](https://hits.sh/github.com/swarmauri/swarmakit.svg)](https://hits.sh/github.com/swarmauri/swarmakit/)
![NPM Version](https://img.shields.io/npm/v/swarmakit?label=version)
![npm downloads](https://img.shields.io/npm/dt/swarmakit.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build and Publish Monorepo](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml/badge.svg)](https://github.com/swarmauri/swarmakit/actions/workflows/publish.yml)
</div>

<div style="text-align: center;">

![Static Badge](https://img.shields.io/badge/React-61DBFB?style=for-the-badge&logo=react&labelColor=black)
![Static Badge](https://img.shields.io/badge/Vue-059669?style=for-the-badge&logo=vuedotjs&labelColor=black)
![Static Badge](https://img.shields.io/badge/Svelte-FF3E00?style=for-the-badge&logo=svelte&labelColor=black)
![Static Badge](https://img.shields.io/badge/TypeScript-1D4ED8?style=for-the-badge&logo=typescript&labelColor=black)
</div>

---

# Swarmakit

Swarmakit offers reusable UI components for React, Vue, and Svelte that integrate seamlessly into Vite-powered applications.

Each framework's components are built with TypeScript for type safety and optimized for performance, designed with best practices to take full advantage of Vite's fast development environment.

# Installation

## 1. Prerequisites

To install Swarmakit libraries, ensure npm is installed. Run the following command:

```bash
npm install npm@latest -g
```

## 2. Initialize a Vite Application

To Start a new project with Vite and TypeScript for each framework, use the following commands:

### Vue 3 + TypeScript

```bash
npm create vite@latest my-vue-app -- --latest vue-ts
cd my-vue-app
npm install
```

replacing `my-vue-app` with your project's name

### React + TypeScript

```bash
npm create vite@latest my-react-app -- --latest react-ts
cd my-react-app
npm install
```

replacing `my-react-app` with your project's name

### Svelte + TypeScript

```bash
npm create vite@latest my-svelte-app -- --latest svelte-ts
cd my-svelte-app
npm install
```

replacing `my-svelte-app` with your project's name

## 3. Install Swarmakit Libraries

Install the Swarmakit component libraries for each framework as needed:

```bash
npm install @swarmakit/vue @swarmakit/react @swarmakit/svelte
```

For framework specific setup and best practices please refer to their specific documentation:

1. [React Library Doc](https://github.com/swarmauri/swarmakit/blob/master/libs/react/README.md)
2. [Svelte Library Doc](https://github.com/swarmauri/swarmakit/blob/master/libs/sveltekit/README.md)
3. [Vue Library Doc](https://github.com/swarmauri/swarmakit/blob/master/libs/vue/README.md)

# Want to help?

If you want to contribute to Swarmakit, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmakit/blob/master/CONTRIBUTING.md) that will help you get started.
