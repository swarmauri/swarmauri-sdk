export function createPluginManager(initial = []) {
  const plugins = new Set();
  for (const plugin of initial) {
    if (plugin && typeof plugin === "object") {
      plugins.add(plugin);
    }
  }

  function runHook(name, context) {
    for (const plugin of plugins) {
      const handler = plugin?.[name];
      if (typeof handler === "function") {
        try {
          handler(context);
        } catch (error) {
          console.error(`[layout-engine] plugin hook "${name}" failed`, error);
        }
      }
    }
  }

  return {
    register(plugin) {
      if (plugin && typeof plugin === "object") {
        plugins.add(plugin);
      }
    },
    unregister(plugin) {
      if (plugin && typeof plugin === "object") {
        plugins.delete(plugin);
      }
    },
    list() {
      return Array.from(plugins);
    },
    runHook,
  };
}
