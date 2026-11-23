// Components Module
// Contains all Vue components for the layout engine

import { computed, defineComponent, h } from "vue";
import {
  useLayoutManifest,
  useAtomRegistry,
  useSiteNavigation,
  useEventContext,
} from "./core.js";
import {
  attachTileEventHandlers,
  attachCardActionHandlers,
  resolveSlotContent,
  ensureTileProps,
} from "./events.js";

// ============================================================================
// LAYOUT ENGINE VIEW COMPONENT
// ============================================================================

/**
 * Main view component that renders tiles from the manifest
 */
const LayoutEngineView = defineComponent({
  name: "LayoutEngineView",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const registry = useAtomRegistry();
    const site = useSiteNavigation(manifest);
    const eventsContext = useEventContext(true);
    const renderTiles = () => {
      if (!manifest.tiles.length) {
        return [];
      }
      const nodes = [];
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
          boxSizing: "border-box",
          padding: "12px",
          display: "flex"
        };
        const componentProps = ensureTileProps(tile);
        const preparedProps = attachTileEventHandlers(
          tile,
          componentProps,
          eventsContext
        );
        const finalProps = attachCardActionHandlers(
          tile,
          preparedProps,
          eventsContext
        );
        const slotContent = resolveSlotContent(tile, finalProps);
        const slotPayload = slotContent
          ? {
            default: () => slotContent,
          }
          : void 0;
        nodes.push(
          h(
            "div",
            { key: tile.id, class: "layout-engine-tile", style },
            [h(entry.component, finalProps, slotPayload)]
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
          components: registry
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
              overflowY: "auto",
              maxHeight: "100vh",
              paddingBottom: "48px"
            }
          },
          renderTiles()
        );
    };
  }
});

// ============================================================================
// LAYOUT ENGINE SHELL COMPONENT
// ============================================================================

/**
 * Shell component with navigation and view
 */
const LayoutEngineShell = defineComponent({
  name: "LayoutEngineShell",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const site = useSiteNavigation(manifest);
    const defaultSlot = slots.default;
    return () => {
      const nav = site.pages.value;
      const current = site.activePage.value;
      return h("div", { class: "layout-engine-shell" }, [
        defaultSlot ? defaultSlot({ site, manifest }) : h(
          "nav",
          { class: "layout-engine-shell__nav" },
          nav.map(
            (page) => h(
              "button",
              {
                class: [
                  "layout-engine-shell__nav-item",
                  page.id === current?.id && "is-active"
                ],
                onClick: () => site.navigate(page.id)
              },
              page.title ?? page.id
            )
          )
        ),
        h(LayoutEngineView)
      ]);
    };
  }
});

// ============================================================================
// NAV LINK COMPONENT
// ============================================================================

/**
 * Navigation link component for page navigation
 */
const LayoutEngineNavLink = defineComponent({
  name: "LayoutEngineNavLink",
  props: {
    pageId: {
      type: String,
      required: true
    }
  },
  setup(props, { slots }) {
    const manifest = useLayoutManifest();
    const site = useSiteNavigation(manifest);
    const page = computed(() => site.pages.value.find((p) => p.id === props.pageId));
    const onClick = () => site.navigate(props.pageId);
    return () => h(
      "button",
      {
        class: [
          "layout-engine-nav-link",
          page.value?.id === site.activePage.value?.id && "is-active"
        ],
        onClick
      },
      slots.default ? slots.default() : page.value?.title ?? props.pageId
    );
  }
});

// Exports
export {
  LayoutEngineView,
  LayoutEngineShell,
  LayoutEngineNavLink,
};
