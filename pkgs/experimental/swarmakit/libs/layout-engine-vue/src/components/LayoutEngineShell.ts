import { defineComponent, h } from "vue";
import LayoutEngineView from "./LayoutEngineView";
import { useLayoutManifest } from "../plugin";
import { useSiteNavigation } from "../site";

export default defineComponent({
  name: "LayoutEngineShell",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const site = useSiteNavigation(manifest);

    const defaultSlot = slots.default;

    return () => {
      const nav = site.pages.value;
      const current = site.activePage.value;

      return h("div", { class: "layout-engine-shell" }, [
        defaultSlot
          ? defaultSlot({ site, manifest })
          : h(
              "nav",
              { class: "layout-engine-shell__nav" },
              nav.map((page) =>
                h(
                  "button",
                  {
                    class: [
                      "layout-engine-shell__nav-item",
                      page.id === current?.id && "is-active",
                    ],
                    onClick: () => site.navigate(page.id),
                  },
                  page.title ?? page.id
                )
              )
            ),
        h(LayoutEngineView),
      ]);
    };
  },
});
