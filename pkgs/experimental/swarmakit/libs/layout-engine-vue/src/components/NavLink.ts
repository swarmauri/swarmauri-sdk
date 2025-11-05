import { computed, defineComponent, h } from "vue";
import { useLayoutManifest } from "../plugin";
import { useSiteNavigation } from "../site";

export default defineComponent({
  name: "LayoutEngineNavLink",
  props: {
    pageId: {
      type: String,
      required: true,
    },
  },
  setup(props, { slots }) {
    const manifest = useLayoutManifest();
    const site = useSiteNavigation(manifest);
    const page = computed(() => site.pages.value.find((p) => p.id === props.pageId));

    const onClick = () => site.navigate(props.pageId);

    return () =>
      h(
        "button",
        {
          class: [
            "layout-engine-nav-link",
            page.value?.id === site.activePage.value?.id && "is-active",
          ],
          onClick,
        },
        slots.default ? slots.default() : page.value?.title ?? props.pageId
      );
  },
});
