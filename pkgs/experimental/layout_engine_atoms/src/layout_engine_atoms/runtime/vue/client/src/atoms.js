import * as Vue from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
import { createAtomRenderers } from "./atom-renderers.js";

export const atomRenderers = createAtomRenderers(Vue);

export default atomRenderers;
