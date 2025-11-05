import { defineComponent, h, type VNode } from "vue";
import { useLayoutManifest, useAtomRegistry } from "../plugin";
import { useSiteNavigation } from "../site";

export default defineComponent({
  name: "LayoutEngineView",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const registry = useAtomRegistry();
    const site = useSiteNavigation(manifest);

    const renderTiles = (): VNode[] => {
      if (!manifest.tiles.length) {
        return [];
      }
      const nodes: VNode[] = [];
      for (const tile of manifest.tiles) {
        const entry = registry.get(tile.role);
        if (!entry) {
          console.warn(`Atom '${tile.role}' not registered in registry`);
          continue;
        }
        const frame = tile.frame ?? { x: 0, y: 0, w: 0, h: 0 };
        const style = {
          position: "absolute",
          left: `${frame.x}px`,
          top: `${frame.y}px`,
          width: `${frame.w}px`,
          height: `${frame.h}px`,
          boxSizing: "border-box" as const,
          padding: "12px",
          display: "flex",
        };
        nodes.push(
          h(
            "div",
            { key: tile.id, class: "layout-engine-tile", style },
            [h(entry.component as any, { ...tile.props })]
          )
        );
      }
      return nodes;
    };

    return () => {
      const viewportWidth = manifest.viewport?.width ?? 0;
      const viewportHeight = manifest.viewport?.height ?? 0;
      if (slots.default) {
        return slots.default({
          manifest,
          site,
          tiles: manifest.tiles,
          components: registry,
        });
      }
      return h(
        "div",
        {
          class: "layout-engine-view",
          style: {
            position: "relative",
            width: viewportWidth ? `${viewportWidth}px` : "100%",
            minHeight: viewportHeight ? `${viewportHeight}px` : "auto",
            margin: "0 auto",
          },
        },
        renderTiles()
      );
    };
  },
});
