var Al = Object.defineProperty;
var El = (t, e, s) => e in t ? Al(t, e, { enumerable: !0, configurable: !0, writable: !0, value: s }) : t[e] = s;
var B = (t, e, s) => El(t, typeof e != "symbol" ? e + "" : e, s);
import { defineComponent as C, ref as m, onMounted as Ce, createElementBlock as c, openBlock as d, createElementVNode as f, createCommentVNode as P, toDisplayString as w, normalizeClass as q, renderSlot as ie, Fragment as I, renderList as L, withDirectives as R, vModelText as H, vModelSelect as ye, normalizeStyle as ne, computed as W, watch as fs, createStaticVNode as Sl, onUnmounted as Di, withModifiers as de, withKeys as Rs, vShow as lo, createBlock as uo, Transition as co, withCtx as Ri, createTextVNode as Fe, reactive as li, onBeforeUnmount as Tl, vModelCheckbox as _l, createVNode as fo, TransitionGroup as Nl, vModelRadio as Il, resolveComponent as Ll } from "vue";
const ql = C({
  name: "360DegreeImageViewer",
  props: {
    images: {
      type: Array,
      required: !0
    },
    rotationSpeed: {
      type: Number,
      default: 100
    }
  },
  setup(t) {
    const e = m(0), s = m(!1), r = m(!0), i = m(t.images[e.value]), a = () => {
      s.value = !0, u();
    }, n = () => {
      s.value = !1;
    }, o = () => {
      s.value ? n() : a();
    }, u = () => {
      s.value && setTimeout(() => {
        e.value = (e.value + 1) % t.images.length, i.value = t.images[e.value], u();
      }, t.rotationSpeed);
    }, p = () => {
      const b = document.querySelector(".image-container img");
      b.style.transform = "scale(1.5)";
    }, g = () => {
      const b = document.querySelector(".image-container img");
      b.style.transform = "scale(1)";
    }, k = (b) => {
      b.preventDefault(), n();
    }, y = (b) => {
      b.preventDefault(), n();
    };
    return Ce(() => {
      r.value = !1, a();
    }), { currentImage: i, rotating: s, loading: r, toggleRotation: o, zoomIn: p, zoomOut: g, onMouseDown: k, onTouchStart: y };
  }
}), A = (t, e) => {
  const s = t.__vccOpts || t;
  for (const [r, i] of e)
    s[r] = i;
  return s;
}, Ol = {
  class: "image-viewer",
  role: "region",
  "aria-label": "360-degree image viewer"
}, Pl = ["src"], Dl = {
  key: 0,
  class: "loading-indicator"
};
function Rl(t, e, s, r, i, a) {
  return d(), c("div", Ol, [
    f("div", {
      class: "image-container",
      onMousedown: e[0] || (e[0] = (...n) => t.onMouseDown && t.onMouseDown(...n)),
      onTouchstart: e[1] || (e[1] = (...n) => t.onTouchStart && t.onTouchStart(...n))
    }, [
      f("img", {
        src: t.currentImage,
        alt: "360-degree view"
      }, null, 8, Pl)
    ], 32),
    t.loading ? (d(), c("div", Dl, "Loading...")) : P("", !0),
    f("button", {
      onClick: e[2] || (e[2] = (...n) => t.toggleRotation && t.toggleRotation(...n)),
      class: "control-button"
    }, w(t.rotating ? "Pause" : "Rotate"), 1),
    f("button", {
      onClick: e[3] || (e[3] = (...n) => t.zoomIn && t.zoomIn(...n)),
      class: "control-button"
    }, "Zoom In"),
    f("button", {
      onClick: e[4] || (e[4] = (...n) => t.zoomOut && t.zoomOut(...n)),
      class: "control-button"
    }, "Zoom Out")
  ]);
}
const B5 = /* @__PURE__ */ A(ql, [["render", Rl], ["__scopeId", "data-v-0fbe72d7"]]), Bl = C({
  name: "Accordion",
  props: {
    defaultOpen: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.defaultOpen), s = m(!1);
    return { isOpen: e, toggleAccordion: () => {
      e.value = !e.value;
    }, isHovered: s };
  }
}), Ml = ["aria-expanded"], Fl = {
  key: 0,
  class: "accordion-content"
};
function Ul(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "accordion",
    onMouseenter: e[1] || (e[1] = (n) => t.isHovered = !0),
    onMouseleave: e[2] || (e[2] = (n) => t.isHovered = !1)
  }, [
    f("button", {
      class: q(["accordion-header", { hovered: t.isHovered }]),
      "aria-expanded": t.isOpen,
      onClick: e[0] || (e[0] = (...n) => t.toggleAccordion && t.toggleAccordion(...n))
    }, [
      ie(t.$slots, "header", {}, void 0, !0)
    ], 10, Ml),
    t.isOpen ? (d(), c("div", Fl, [
      ie(t.$slots, "content", {}, void 0, !0)
    ])) : P("", !0)
  ], 32);
}
const M5 = /* @__PURE__ */ A(Bl, [["render", Ul], ["__scopeId", "data-v-062ad5b7"]]), jl = C({
  name: "ActionableList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup() {
    return { hoveredIndex: m(null), triggerAction: (s) => {
      console.log(`Action triggered for item at index: ${s}`);
    } };
  }
}), Vl = {
  class: "actionable-list",
  role: "list"
}, Hl = ["onMouseenter"], zl = ["onClick", "disabled", "aria-disabled"], Gl = {
  key: 1,
  class: "loading-spinner"
};
function Kl(t, e, s, r, i, a) {
  return d(), c("ul", Vl, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("li", {
      key: o,
      class: q(["actionable-list-item", { hovered: t.hoveredIndex === o, disabled: n.disabled, loading: n.loading }]),
      onMouseenter: (u) => t.hoveredIndex = o,
      onMouseleave: e[0] || (e[0] = (u) => t.hoveredIndex = null)
    }, [
      f("span", null, w(n.label), 1),
      !n.disabled && !n.loading ? (d(), c("button", {
        key: 0,
        onClick: (u) => t.triggerAction(o),
        disabled: n.disabled,
        "aria-disabled": n.disabled ? "true" : "false",
        class: "action-button"
      }, w(n.actionLabel), 9, zl)) : P("", !0),
      n.loading ? (d(), c("span", Gl, "Loading...")) : P("", !0)
    ], 42, Hl))), 128))
  ]);
}
const F5 = /* @__PURE__ */ A(jl, [["render", Kl], ["__scopeId", "data-v-4a589b9f"]]), Wl = C({
  name: "ActivityIndicators",
  props: {
    type: {
      type: String,
      default: "loading",
      validator: (t) => ["loading", "success", "error"].includes(t)
    },
    message: {
      type: String,
      default: "Loading..."
    }
  }
}), Zl = {
  key: 0,
  class: "spinner"
}, Xl = { key: 1 };
function Yl(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["activity-indicator", t.type]),
    role: "status",
    "aria-live": "polite"
  }, [
    t.type === "loading" ? (d(), c("span", Zl)) : (d(), c("span", Xl, w(t.message), 1))
  ], 2);
}
const U5 = /* @__PURE__ */ A(Wl, [["render", Yl], ["__scopeId", "data-v-a4d57fae"]]), Ql = C({
  name: "AdminViewScheduler",
  props: {
    feedbackMessage: {
      type: String,
      required: !1,
      default: ""
    },
    addNewEvent: {
      type: Function,
      required: !1,
      default: (t) => {
        console.log("Default addNewEvent function", t);
      }
    },
    editEvent: {
      type: Function,
      required: !1,
      default: (t) => {
        console.log(`Default editEvent function: Editing ${t.title}`);
      }
    },
    deleteEvent: {
      type: Function,
      required: !1,
      default: (t) => {
        console.log(`Default deleteEvent function: Deleting event with id ${t}`);
      }
    }
  },
  setup(t) {
    const e = m([
      { id: 1, title: "Team Meeting", date: "2024-10-21" },
      { id: 2, title: "Project Deadline", date: "2024-10-25" }
    ]), s = m(null), r = m(""), i = m(""), a = m(e.value.length + 1), n = (b) => {
      t.addNewEvent(b), e.value.push(b), a.value++;
    }, o = (b) => {
      const v = e.value.findIndex((E) => E.id === b.id);
      v !== -1 && (e.value[v] = { ...b }, t.editEvent(b));
    }, u = (b) => {
      e.value = e.value.filter((v) => v.id !== b), t.deleteEvent(b);
    }, p = (b) => {
      s.value = b;
      const v = e.value.find((E) => E.id === b);
      v && (r.value = v.title, i.value = v.date);
    }, g = (b) => {
      s.value === b && (o({
        id: b,
        title: r.value,
        date: i.value
      }), s.value = null);
    }, k = () => {
      s.value = null;
    }, y = (b) => s.value === b;
    return {
      events: e,
      newEventId: a,
      editedTitle: r,
      editedDate: i,
      feedbackMessage: t.feedbackMessage,
      handleAddNewEvent: n,
      handleEditEvent: o,
      handleDeleteEvent: u,
      startEdit: p,
      saveEdit: g,
      cancelEdit: k,
      isEditing: y
    };
  }
}), Jl = { key: 0 }, xl = { key: 0 }, eu = ["onClick"], tu = ["onClick"], su = { key: 1 }, nu = ["onClick"];
function ru(t, e, s, r, i, a) {
  return d(), c("div", null, [
    e[4] || (e[4] = f("h2", null, "Event Scheduler", -1)),
    t.feedbackMessage ? (d(), c("p", Jl, w(t.feedbackMessage), 1)) : P("", !0),
    (d(!0), c(I, null, L(t.events, (n) => (d(), c("div", {
      key: n.id,
      class: "event"
    }, [
      t.isEditing(n.id) ? (d(), c("div", su, [
        R(f("input", {
          "onUpdate:modelValue": e[0] || (e[0] = (o) => t.editedTitle = o),
          placeholder: "Edit title"
        }, null, 512), [
          [H, t.editedTitle]
        ]),
        R(f("input", {
          "onUpdate:modelValue": e[1] || (e[1] = (o) => t.editedDate = o),
          type: "date",
          placeholder: "Edit date"
        }, null, 512), [
          [H, t.editedDate]
        ]),
        f("button", {
          onClick: (o) => t.saveEdit(n.id)
        }, "Save", 8, nu),
        f("button", {
          onClick: e[2] || (e[2] = (...o) => t.cancelEdit && t.cancelEdit(...o))
        }, "Cancel")
      ])) : (d(), c("div", xl, [
        f("h3", null, w(n.title), 1),
        f("p", null, w(n.date), 1),
        f("button", {
          onClick: (o) => t.startEdit(n.id)
        }, "Edit", 8, eu),
        f("button", {
          onClick: (o) => t.handleDeleteEvent(n.id)
        }, "Delete", 8, tu)
      ]))
    ]))), 128)),
    f("button", {
      onClick: e[3] || (e[3] = (n) => t.handleAddNewEvent({ id: t.newEventId, title: "New Event", date: "2024-11-01" }))
    }, " Add New Event ")
  ]);
}
const j5 = /* @__PURE__ */ A(Ql, [["render", ru], ["__scopeId", "data-v-acf13d1f"]]), iu = C({
  name: "AudioPlayer",
  props: {
    src: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(null), e = m(!1), s = m(!1), r = m(1);
    return { isPlaying: e, isMuted: s, volume: r, togglePlay: () => {
      const u = t.value;
      u && (e.value ? u.pause() : u.play(), e.value = !e.value);
    }, toggleMute: () => {
      const u = t.value;
      u && (u.muted = !u.muted, s.value = u.muted);
    }, changeVolume: () => {
      const u = t.value;
      u && (u.volume = r.value);
    }, onLoadedData: () => {
      const u = t.value;
      u && (r.value = u.volume);
    } };
  }
}), au = {
  class: "audio-player",
  role: "region",
  "aria-label": "Audio player"
}, ou = ["src"];
function lu(t, e, s, r, i, a) {
  return d(), c("div", au, [
    f("audio", {
      ref: "audioElement",
      src: t.src,
      onLoadeddata: e[0] || (e[0] = (...n) => t.onLoadedData && t.onLoadedData(...n))
    }, null, 40, ou),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.togglePlay && t.togglePlay(...n)),
      class: "control-button",
      "aria-label": "Play/Pause"
    }, w(t.isPlaying ? "Pause" : "Play"), 1),
    f("button", {
      onClick: e[2] || (e[2] = (...n) => t.toggleMute && t.toggleMute(...n)),
      class: "control-button",
      "aria-label": "Mute/Unmute"
    }, w(t.isMuted ? "Unmute" : "Mute"), 1),
    R(f("input", {
      type: "range",
      class: "volume-control",
      min: "0",
      max: "1",
      step: "0.1",
      "onUpdate:modelValue": e[3] || (e[3] = (n) => t.volume = n),
      onInput: e[4] || (e[4] = (...n) => t.changeVolume && t.changeVolume(...n)),
      "aria-label": "Volume control"
    }, null, 544), [
      [H, t.volume]
    ])
  ]);
}
const V5 = /* @__PURE__ */ A(iu, [["render", lu], ["__scopeId", "data-v-f1cd7384"]]), uu = C({
  name: "AudioPlayerAdvanced",
  props: {
    src: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(null), e = m(!1), s = m(!1), r = m(1), i = m(0), a = m(0), n = m(1), o = [0.5, 1, 1.5, 2], u = () => {
      const v = t.value;
      v && (e.value ? v.pause() : v.play(), e.value = !e.value);
    }, p = () => {
      const v = t.value;
      v && (v.muted = !v.muted, s.value = v.muted);
    }, g = () => {
      const v = t.value;
      v && (v.volume = r.value);
    }, k = () => {
      const v = t.value;
      v && (v.currentTime = i.value);
    }, y = () => {
      const v = t.value;
      v && (v.playbackRate = n.value);
    }, b = () => {
      const v = t.value;
      v && (r.value = v.volume, a.value = v.duration);
    };
    return Ce(() => {
      const v = t.value;
      v && v.addEventListener("timeupdate", () => {
        i.value = v.currentTime;
      });
    }), {
      isPlaying: e,
      isMuted: s,
      volume: r,
      currentTime: i,
      duration: a,
      playbackRate: n,
      playbackRates: o,
      togglePlay: u,
      toggleMute: p,
      changeVolume: g,
      seekAudio: k,
      changeSpeed: y,
      onLoadedData: b
    };
  }
}), du = {
  class: "audio-player-advanced",
  role: "region",
  "aria-label": "Advanced audio player"
}, cu = ["src"], fu = ["max"], pu = ["value"];
function hu(t, e, s, r, i, a) {
  return d(), c("div", du, [
    f("audio", {
      ref: "audioElement",
      src: t.src,
      onLoadeddata: e[0] || (e[0] = (...n) => t.onLoadedData && t.onLoadedData(...n))
    }, null, 40, cu),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.togglePlay && t.togglePlay(...n)),
      class: "control-button",
      "aria-label": "Play/Pause"
    }, w(t.isPlaying ? "Pause" : "Play"), 1),
    f("button", {
      onClick: e[2] || (e[2] = (...n) => t.toggleMute && t.toggleMute(...n)),
      class: "control-button",
      "aria-label": "Mute/Unmute"
    }, w(t.isMuted ? "Unmute" : "Mute"), 1),
    R(f("input", {
      type: "range",
      class: "volume-control",
      min: "0",
      max: "1",
      step: "0.1",
      "onUpdate:modelValue": e[3] || (e[3] = (n) => t.volume = n),
      onInput: e[4] || (e[4] = (...n) => t.changeVolume && t.changeVolume(...n)),
      "aria-label": "Volume control"
    }, null, 544), [
      [H, t.volume]
    ]),
    R(f("input", {
      type: "range",
      class: "seek-bar",
      max: t.duration,
      "onUpdate:modelValue": e[5] || (e[5] = (n) => t.currentTime = n),
      onInput: e[6] || (e[6] = (...n) => t.seekAudio && t.seekAudio(...n)),
      "aria-label": "Seek control"
    }, null, 40, fu), [
      [H, t.currentTime]
    ]),
    R(f("select", {
      "onUpdate:modelValue": e[7] || (e[7] = (n) => t.playbackRate = n),
      onChange: e[8] || (e[8] = (...n) => t.changeSpeed && t.changeSpeed(...n)),
      "aria-label": "Playback speed control"
    }, [
      (d(!0), c(I, null, L(t.playbackRates, (n) => (d(), c("option", {
        key: n,
        value: n
      }, w(n) + "x", 9, pu))), 128))
    ], 544), [
      [ye, t.playbackRate]
    ])
  ]);
}
const H5 = /* @__PURE__ */ A(uu, [["render", hu], ["__scopeId", "data-v-4192c021"]]), gu = C({
  name: "AudioPlayerAdvanced",
  props: {
    src: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(null), e = m(!1), s = m(!1), r = m(1), i = m(0), a = m(0), n = m(1), o = [0.5, 1, 1.5, 2], u = () => {
      const v = t.value;
      v && (e.value ? v.pause() : v.play(), e.value = !e.value);
    }, p = () => {
      const v = t.value;
      v && (v.muted = !v.muted, s.value = v.muted);
    }, g = () => {
      const v = t.value;
      v && (v.volume = r.value);
    }, k = () => {
      const v = t.value;
      v && (v.currentTime = i.value);
    }, y = () => {
      const v = t.value;
      v && (v.playbackRate = n.value);
    }, b = () => {
      const v = t.value;
      v && (r.value = v.volume, a.value = v.duration);
    };
    return Ce(() => {
      const v = t.value;
      v && v.addEventListener("timeupdate", () => {
        i.value = v.currentTime;
      });
    }), {
      isPlaying: e,
      isMuted: s,
      volume: r,
      currentTime: i,
      duration: a,
      playbackRate: n,
      playbackRates: o,
      togglePlay: u,
      toggleMute: p,
      changeVolume: g,
      seekAudio: k,
      changeSpeed: y,
      onLoadedData: b
    };
  }
}), mu = {
  class: "audio-player-advanced",
  role: "region",
  "aria-label": "Advanced audio player"
}, vu = ["src"], bu = ["max"], yu = ["value"];
function $u(t, e, s, r, i, a) {
  return d(), c("div", mu, [
    f("audio", {
      ref: "audioElement",
      src: t.src,
      onLoadeddata: e[0] || (e[0] = (...n) => t.onLoadedData && t.onLoadedData(...n))
    }, null, 40, vu),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.togglePlay && t.togglePlay(...n)),
      class: "control-button",
      "aria-label": "Play/Pause"
    }, w(t.isPlaying ? "Pause" : "Play"), 1),
    f("button", {
      onClick: e[2] || (e[2] = (...n) => t.toggleMute && t.toggleMute(...n)),
      class: "control-button",
      "aria-label": "Mute/Unmute"
    }, w(t.isMuted ? "Unmute" : "Mute"), 1),
    R(f("input", {
      type: "range",
      class: "volume-control",
      min: "0",
      max: "1",
      step: "0.1",
      "onUpdate:modelValue": e[3] || (e[3] = (n) => t.volume = n),
      onInput: e[4] || (e[4] = (...n) => t.changeVolume && t.changeVolume(...n)),
      "aria-label": "Volume control"
    }, null, 544), [
      [H, t.volume]
    ]),
    R(f("input", {
      type: "range",
      class: "seek-bar",
      max: t.duration,
      "onUpdate:modelValue": e[5] || (e[5] = (n) => t.currentTime = n),
      onInput: e[6] || (e[6] = (...n) => t.seekAudio && t.seekAudio(...n)),
      "aria-label": "Seek control"
    }, null, 40, bu), [
      [H, t.currentTime]
    ]),
    R(f("select", {
      "onUpdate:modelValue": e[7] || (e[7] = (n) => t.playbackRate = n),
      onChange: e[8] || (e[8] = (...n) => t.changeSpeed && t.changeSpeed(...n)),
      "aria-label": "Playback speed control"
    }, [
      (d(!0), c(I, null, L(t.playbackRates, (n) => (d(), c("option", {
        key: n,
        value: n
      }, w(n) + "x", 9, yu))), 128))
    ], 544), [
      [ye, t.playbackRate]
    ])
  ]);
}
const z5 = /* @__PURE__ */ A(gu, [["render", $u], ["__scopeId", "data-v-81b5aab6"]]), ku = C({
  name: "Avatar",
  props: {
    imageSrc: {
      type: String,
      default: ""
    },
    initials: {
      type: String,
      default: "A"
    },
    ariaLabel: {
      type: String,
      default: "User Avatar"
    }
  }
}), wu = ["aria-label"], Cu = {
  key: 1,
  class: "avatar placeholder"
};
function Au(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "avatar-container",
    role: "img",
    "aria-label": t.ariaLabel
  }, [
    t.imageSrc ? (d(), c("div", {
      key: 0,
      class: "avatar",
      style: ne({ backgroundImage: `url(${t.imageSrc})` })
    }, null, 4)) : (d(), c("div", Cu, w(t.initials), 1))
  ], 8, wu);
}
const G5 = /* @__PURE__ */ A(ku, [["render", Au], ["__scopeId", "data-v-703ea8e3"]]), Eu = C({
  name: "Badge",
  props: {
    type: {
      type: String,
      default: "default"
    }
  },
  setup(t) {
    return { badgeClass: W(() => `badge ${t.type}`) };
  }
});
function Su(t, e, s, r, i, a) {
  return d(), c("span", {
    class: q(t.badgeClass),
    role: "status",
    "aria-live": "polite"
  }, [
    ie(t.$slots, "default", {}, void 0, !0)
  ], 2);
}
const K5 = /* @__PURE__ */ A(Eu, [["render", Su], ["__scopeId", "data-v-373bc344"]]), Tu = C({
  name: "BadgeWithCounts",
  props: {
    count: {
      type: Number,
      default: 0
    }
  },
  setup(t) {
    return { badgeClass: W(() => `badge ${t.count > 0 ? "active" : "zero"}`) };
  }
}), _u = {
  key: 0,
  class: "overflow"
}, Nu = { key: 1 };
function Iu(t, e, s, r, i, a) {
  return d(), c("span", {
    class: q(t.badgeClass),
    role: "status",
    "aria-live": "polite"
  }, [
    t.count > 99 ? (d(), c("span", _u, "99+")) : (d(), c("span", Nu, w(t.count), 1))
  ], 2);
}
const W5 = /* @__PURE__ */ A(Tu, [["render", Iu], ["__scopeId", "data-v-42553945"]]), Lu = C({
  name: "BatteryLevelIndicator",
  props: {
    level: {
      type: Number,
      required: !0
    },
    charging: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    return { batteryState: W(() => t.charging ? "charging" : t.level > 80 ? "full" : t.level > 20 ? "low" : "critical") };
  }
}), qu = ["aria-valuenow"], Ou = {
  key: 0,
  class: "charging-icon"
};
function Pu(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "battery-container",
    role: "progressbar",
    "aria-valuemin": "0",
    "aria-valuemax": "100",
    "aria-valuenow": t.level
  }, [
    f("div", {
      class: q(["battery", t.batteryState]),
      style: ne({ width: `${t.level}%` })
    }, null, 6),
    t.charging ? (d(), c("div", Ou, "⚡")) : P("", !0)
  ], 8, qu);
}
const Z5 = /* @__PURE__ */ A(Lu, [["render", Pu], ["__scopeId", "data-v-b2d4d309"]]), Du = C({
  name: "BetSlider",
  props: {
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      default: 100
    },
    step: {
      type: Number,
      default: 1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.min), s = () => {
      e.value > t.max && (e.value = t.max);
    };
    return fs(e, s), {
      bet: e,
      updateBet: s
    };
  }
}), Ru = {
  class: "bet-slider",
  "aria-label": "Bet Slider"
}, Bu = ["min", "max", "step", "disabled"], Mu = ["min", "max", "disabled"], Fu = {
  key: 0,
  class: "feedback"
};
function Uu(t, e, s, r, i, a) {
  return d(), c("div", Ru, [
    R(f("input", {
      type: "range",
      min: t.min,
      max: t.max,
      step: t.step,
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.bet = n),
      disabled: t.disabled,
      onInput: e[1] || (e[1] = (...n) => t.updateBet && t.updateBet(...n)),
      class: "slider"
    }, null, 40, Bu), [
      [H, t.bet]
    ]),
    R(f("input", {
      type: "number",
      min: t.min,
      max: t.max,
      "onUpdate:modelValue": e[2] || (e[2] = (n) => t.bet = n),
      disabled: t.disabled,
      class: "bet-input",
      onChange: e[3] || (e[3] = (...n) => t.updateBet && t.updateBet(...n))
    }, null, 40, Mu), [
      [
        H,
        t.bet,
        void 0,
        { number: !0 }
      ]
    ]),
    t.bet >= t.max ? (d(), c("div", Fu, "Max Bet Reached")) : P("", !0)
  ]);
}
const X5 = /* @__PURE__ */ A(Du, [["render", Uu], ["__scopeId", "data-v-2449a36a"]]), ju = C({
  name: "BottomNavigationBar",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  methods: {
    onSelect(t) {
      this.$emit("update:items", this.items.map((e) => ({
        ...e,
        selected: e.label === t.label
      })));
    },
    onHover(t) {
      console.log(`${t.label} is hovered`);
    }
  }
}), Vu = {
  class: "bottom-navigation-bar",
  role: "navigation",
  "aria-label": "Bottom Navigation"
}, Hu = { class: "nav-items" }, zu = ["onMouseover", "onClick", "aria-disabled"];
function Gu(t, e, s, r, i, a) {
  return d(), c("nav", Vu, [
    f("ul", Hu, [
      (d(!0), c(I, null, L(t.items, (n) => (d(), c("li", {
        key: n.label,
        class: q({ selected: n.selected, disabled: n.disabled }),
        onMouseover: (o) => n.disabled ? null : t.onHover(n),
        onClick: (o) => n.disabled ? null : t.onSelect(n),
        "aria-disabled": n.disabled,
        tabindex: "0"
      }, [
        f("span", null, w(n.label), 1)
      ], 42, zu))), 128))
    ])
  ]);
}
const Y5 = /* @__PURE__ */ A(ju, [["render", Gu], ["__scopeId", "data-v-6c91e3f1"]]), Ku = C({
  name: "BreadcrumbWithDropdowns",
  props: {
    breadcrumbs: {
      type: Array,
      required: !0
    }
  },
  data() {
    return {
      openDropdownIndex: null
    };
  },
  methods: {
    navigateTo(t) {
      window.location.href = t;
    },
    toggleDropdown(t) {
      this.openDropdownIndex = this.openDropdownIndex === t ? null : t;
    },
    isDropdownOpen(t) {
      return this.openDropdownIndex === t;
    }
  }
}), Wu = {
  "aria-label": "Breadcrumb",
  class: "breadcrumb"
}, Zu = { class: "breadcrumb-list" }, Xu = ["onClick", "aria-current"], Yu = {
  key: 1,
  class: "dropdown"
}, Qu = ["onClick", "aria-expanded"], Ju = {
  key: 0,
  class: "dropdown-menu"
}, xu = ["onClick"];
function ed(t, e, s, r, i, a) {
  return d(), c("nav", Wu, [
    f("ol", Zu, [
      (d(!0), c(I, null, L(t.breadcrumbs, (n, o) => (d(), c("li", {
        key: o,
        class: "breadcrumb-item"
      }, [
        n.dropdown ? (d(), c("div", Yu, [
          f("button", {
            onClick: (u) => t.toggleDropdown(o),
            "aria-expanded": t.isDropdownOpen(o),
            "aria-haspopup": "true"
          }, w(n.name), 9, Qu),
          t.isDropdownOpen(o) ? (d(), c("ul", Ju, [
            (d(!0), c(I, null, L(n.dropdown, (u, p) => (d(), c("li", {
              key: p,
              onClick: (g) => t.navigateTo(u.link)
            }, w(u.name), 9, xu))), 128))
          ])) : P("", !0)
        ])) : (d(), c("span", {
          key: 0,
          class: q({ "breadcrumb-link": n.link }),
          onClick: (u) => n.link ? t.navigateTo(n.link) : null,
          "aria-current": o === t.breadcrumbs.length - 1 ? "page" : void 0
        }, w(n.name), 11, Xu))
      ]))), 128))
    ])
  ]);
}
const Q5 = /* @__PURE__ */ A(Ku, [["render", ed], ["__scopeId", "data-v-00e68632"]]), td = C({
  name: "Breadcrumbs",
  props: {
    breadcrumbs: {
      type: Array,
      required: !0
    },
    activeIndex: {
      type: Number,
      default: 0
    }
  },
  methods: {
    navigateTo(t) {
      t && (window.location.href = t);
    }
  }
}), sd = {
  "aria-label": "Breadcrumb",
  class: "breadcrumbs"
}, nd = { class: "breadcrumbs-list" }, rd = {
  key: 0,
  "aria-current": "page",
  class: "breadcrumbs-link"
}, id = ["onClick"];
function ad(t, e, s, r, i, a) {
  return d(), c("nav", sd, [
    f("ol", nd, [
      (d(!0), c(I, null, L(t.breadcrumbs, (n, o) => (d(), c("li", {
        key: o,
        class: q(["breadcrumbs-item", { active: o === t.activeIndex }])
      }, [
        o === t.activeIndex ? (d(), c("span", rd, w(n.name), 1)) : (d(), c("span", {
          key: 1,
          class: "breadcrumbs-link",
          onClick: (u) => t.navigateTo(n.link)
        }, w(n.name), 9, id))
      ], 2))), 128))
    ])
  ]);
}
const J5 = /* @__PURE__ */ A(td, [["render", ad], ["__scopeId", "data-v-de61de6d"]]), od = C({
  name: "BrushTool",
  setup() {
    const t = m(!1), e = m(5), s = m("#000000"), r = m(1);
    return {
      isActive: t,
      brushSize: e,
      brushColor: s,
      brushOpacity: r,
      toggleActive: () => {
        t.value = !t.value;
      }
    };
  }
}), ld = ["aria-pressed"], ud = {
  key: 0,
  class: "brush-settings"
};
function dd(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["brush-tool", { active: t.isActive }])
  }, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleActive && t.toggleActive(...n)),
      "aria-pressed": t.isActive
    }, "Brush Tool", 8, ld),
    t.isActive ? (d(), c("div", ud, [
      e[4] || (e[4] = f("label", { for: "brushSize" }, "Brush Size", -1)),
      R(f("input", {
        id: "brushSize",
        type: "range",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.brushSize = n),
        min: "1",
        max: "20",
        "aria-valuemin": "1",
        "aria-valuemax": "20",
        "aria-valuenow": "brushSize"
      }, null, 512), [
        [H, t.brushSize]
      ]),
      e[5] || (e[5] = f("label", { for: "brushColor" }, "Brush Color", -1)),
      R(f("input", {
        id: "brushColor",
        type: "color",
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.brushColor = n)
      }, null, 512), [
        [H, t.brushColor]
      ]),
      e[6] || (e[6] = f("label", { for: "brushOpacity" }, "Brush Opacity", -1)),
      R(f("input", {
        id: "brushOpacity",
        type: "range",
        "onUpdate:modelValue": e[3] || (e[3] = (n) => t.brushOpacity = n),
        min: "0.1",
        max: "1",
        step: "0.1",
        "aria-valuemin": "0.1",
        "aria-valuemax": "1",
        "aria-valuenow": "brushOpacity"
      }, null, 512), [
        [H, t.brushOpacity]
      ])
    ])) : P("", !0)
  ], 2);
}
const x5 = /* @__PURE__ */ A(od, [["render", dd], ["__scopeId", "data-v-aa617421"]]), cd = C({
  name: "Button",
  props: {
    type: {
      type: String,
      default: "primary"
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(!1), s = m(!1), r = W(() => t.disabled ? "disabled" : s.value ? "active" : e.value ? "hover" : t.type);
    return {
      isHover: e,
      isActive: s,
      buttonType: r
    };
  }
}), fd = ["aria-disabled", "disabled"];
function pd(t, e, s, r, i, a) {
  return d(), c("button", {
    class: q(["button", t.buttonType, { disabled: t.disabled }]),
    "aria-disabled": t.disabled,
    disabled: t.disabled,
    onMouseover: e[0] || (e[0] = (n) => t.isHover = !0),
    onMouseleave: e[1] || (e[1] = (n) => t.isHover = !1),
    onMousedown: e[2] || (e[2] = (n) => t.isActive = !0),
    onMouseup: e[3] || (e[3] = (n) => t.isActive = !1)
  }, [
    ie(t.$slots, "default", {}, void 0, !0)
  ], 42, fd);
}
const eT = /* @__PURE__ */ A(cd, [["render", pd], ["__scopeId", "data-v-3457f604"]]), hd = C({
  name: "CalendarView",
  props: {
    currentView: {
      type: String,
      required: !0,
      validator: (t) => ["day", "week", "month", "year", "agenda"].includes(t)
    }
  },
  setup(t) {
    const e = m(t.currentView), s = W(() => {
      switch (e.value) {
        case "day":
          return "Day View";
        case "week":
          return "Week View";
        case "month":
          return "Month View";
        case "year":
          return "Year View";
        case "agenda":
          return "Agenda View";
      }
    });
    return {
      currentView: e,
      currentViewTitle: s,
      goToPrevious: () => {
      },
      goToNext: () => {
      }
    };
  }
}), gd = { class: "calendar-view" }, md = {
  class: "calendar-header",
  "aria-label": "Calendar Navigation"
};
function vd(t, e, s, r, i, a) {
  return d(), c("div", gd, [
    f("div", md, [
      f("button", {
        onClick: e[0] || (e[0] = (...n) => t.goToPrevious && t.goToPrevious(...n)),
        "aria-label": "Previous"
      }, "Prev"),
      f("h2", null, w(t.currentViewTitle), 1),
      f("button", {
        onClick: e[1] || (e[1] = (...n) => t.goToNext && t.goToNext(...n)),
        "aria-label": "Next"
      }, "Next"),
      R(f("select", {
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.currentView = n),
        "aria-label": "Change View"
      }, [...e[3] || (e[3] = [
        Sl('<option value="day" data-v-f2b44818>Day</option><option value="week" data-v-f2b44818>Week</option><option value="month" data-v-f2b44818>Month</option><option value="year" data-v-f2b44818>Year</option><option value="agenda" data-v-f2b44818>Agenda</option>', 5)
      ])], 512), [
        [ye, t.currentView]
      ])
    ]),
    e[4] || (e[4] = f("div", {
      class: "calendar-content",
      role: "grid"
    }, null, -1))
  ]);
}
const tT = /* @__PURE__ */ A(hd, [["render", vd], ["__scopeId", "data-v-f2b44818"]]), bd = C({
  name: "CallButton",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  }
}), yd = ["disabled"];
function $d(t, e, s, r, i, a) {
  return d(), c("button", {
    class: "call-button",
    disabled: t.disabled,
    "aria-label": "Call Bet"
  }, " Call ", 8, yd);
}
const sT = /* @__PURE__ */ A(bd, [["render", $d], ["__scopeId", "data-v-cbb8bf14"]]), kd = C({
  name: "Canvas",
  setup() {
    const t = m(null), e = m(window.innerWidth), s = m(window.innerHeight), r = m(5), i = m("#000000");
    let a = !1;
    const n = (g) => {
      a = !0, u(g);
    }, o = () => {
      var k;
      a = !1;
      const g = (k = t.value) == null ? void 0 : k.getContext("2d");
      g && g.beginPath();
    }, u = (g) => {
      if (!a || !t.value) return;
      const k = t.value.getContext("2d");
      if (!k) return;
      const y = t.value.getBoundingClientRect(), b = "touches" in g ? g.touches[0].clientX - y.left : g.clientX - y.left, v = "touches" in g ? g.touches[0].clientY - y.top : g.clientY - y.top;
      k.lineWidth = r.value, k.lineCap = "round", k.strokeStyle = i.value, k.lineTo(b, v), k.stroke(), k.beginPath(), k.moveTo(b, v);
    }, p = () => {
      var k;
      const g = (k = t.value) == null ? void 0 : k.getContext("2d");
      g && g.clearRect(0, 0, e.value, s.value);
    };
    return Ce(() => {
      window.addEventListener("resize", () => {
        e.value = window.innerWidth, s.value = window.innerHeight;
      });
    }), {
      canvas: t,
      canvasWidth: e,
      canvasHeight: s,
      brushSize: r,
      brushColor: i,
      startDrawing: n,
      stopDrawing: o,
      draw: u,
      clearCanvas: p
    };
  }
}), wd = ["width", "height"], Cd = { class: "controls" };
function Ad(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "canvas-container",
    onMousedown: e[3] || (e[3] = (...n) => t.startDrawing && t.startDrawing(...n)),
    onMouseup: e[4] || (e[4] = (...n) => t.stopDrawing && t.stopDrawing(...n)),
    onMousemove: e[5] || (e[5] = (...n) => t.draw && t.draw(...n)),
    onTouchstart: e[6] || (e[6] = (...n) => t.startDrawing && t.startDrawing(...n)),
    onTouchend: e[7] || (e[7] = (...n) => t.stopDrawing && t.stopDrawing(...n)),
    onTouchmove: e[8] || (e[8] = (...n) => t.draw && t.draw(...n))
  }, [
    f("canvas", {
      ref: "canvas",
      width: t.canvasWidth,
      height: t.canvasHeight,
      "aria-label": "Interactive Drawing Canvas"
    }, null, 8, wd),
    f("div", Cd, [
      f("button", {
        onClick: e[0] || (e[0] = (...n) => t.clearCanvas && t.clearCanvas(...n)),
        "aria-label": "Clear Canvas"
      }, "Clear"),
      e[9] || (e[9] = f("label", { for: "brushSize" }, "Brush Size", -1)),
      R(f("input", {
        id: "brushSize",
        type: "range",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.brushSize = n),
        min: "1",
        max: "10",
        "aria-valuemin": "1",
        "aria-valuemax": "10",
        "aria-valuenow": "brushSize"
      }, null, 512), [
        [H, t.brushSize]
      ]),
      e[10] || (e[10] = f("label", { for: "brushColor" }, "Brush Color", -1)),
      R(f("input", {
        id: "brushColor",
        type: "color",
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.brushColor = n)
      }, null, 512), [
        [H, t.brushColor]
      ])
    ])
  ], 32);
}
const nT = /* @__PURE__ */ A(kd, [["render", Ad], ["__scopeId", "data-v-ca98a860"]]), Ed = C({
  name: "Captcha",
  props: {
    captchaText: {
      type: String,
      default: "Please solve the captcha"
    }
  },
  setup(t) {
    const e = m(!1), s = m(!1);
    return {
      isSolved: e,
      hasError: s,
      solveCaptcha: () => {
        t.captchaText === "Please solve the captcha" ? (e.value = !0, s.value = !1) : s.value = !0;
      }
    };
  }
}), Sd = { class: "captcha-container" }, Td = { key: 0 }, _d = { key: 1 }, Nd = ["disabled"];
function Id(t, e, s, r, i, a) {
  return d(), c("div", Sd, [
    f("div", {
      class: q(["captcha", { "captcha--error": t.hasError, "captcha--solved": t.isSolved }])
    }, [
      t.isSolved ? (d(), c("span", _d, "✔ Solved")) : (d(), c("span", Td, w(t.captchaText), 1))
    ], 2),
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.solveCaptcha && t.solveCaptcha(...n)),
      disabled: t.isSolved,
      "aria-label": "solve captcha"
    }, "Solve", 8, Nd)
  ]);
}
const rT = /* @__PURE__ */ A(Ed, [["render", Id], ["__scopeId", "data-v-e6fd93f9"]]), Ld = C({
  name: "CardActions",
  props: {
    actions: {
      type: Array,
      required: !0
    }
  },
  setup() {
    return { hoveredIndex: m(-1) };
  }
}), qd = { class: "card-actions" }, Od = ["disabled", "onMouseover", "onClick"];
function Pd(t, e, s, r, i, a) {
  return d(), c("div", qd, [
    (d(!0), c(I, null, L(t.actions, (n, o) => (d(), c("button", {
      key: o,
      class: q({ hovered: t.hoveredIndex === o, disabled: n.disabled }),
      disabled: n.disabled,
      onMouseover: (u) => t.hoveredIndex = o,
      onMouseleave: e[0] || (e[0] = (u) => t.hoveredIndex = -1),
      onClick: n.onClick
    }, w(n.label), 43, Od))), 128))
  ]);
}
const iT = /* @__PURE__ */ A(Ld, [["render", Pd], ["__scopeId", "data-v-10a84f95"]]), Dd = C({
  name: "CardBadge",
  props: {
    content: {
      type: [String, Number],
      required: !0
    },
    status: {
      type: String,
      default: "default"
    }
  },
  setup(t) {
    const e = m(!1);
    return { statusClass: W(() => ({
      default: "badge-default",
      active: "badge-active",
      inactive: "badge-inactive",
      hovered: e.value ? "badge-hovered" : ""
    })[t.status]), isHovered: e };
  }
});
function Rd(t, e, s, r, i, a) {
  return d(), c("span", {
    class: q(["card-badge", t.statusClass]),
    onMouseover: e[0] || (e[0] = (n) => t.isHovered = !0),
    onMouseleave: e[1] || (e[1] = (n) => t.isHovered = !1)
  }, w(t.content), 35);
}
const aT = /* @__PURE__ */ A(Dd, [["render", Rd], ["__scopeId", "data-v-f22b6cfb"]]), Bd = C({
  name: "CardBody",
  props: {
    expanded: {
      type: Boolean,
      default: !0
    },
    collapsible: {
      type: Boolean,
      default: !1
    },
    ariaLabel: {
      type: String,
      default: "Card Body"
    }
  },
  setup(t) {
    const e = m(t.expanded);
    return { isExpanded: e, toggleExpand: () => {
      e.value = !e.value;
    } };
  }
}), Md = ["aria-expanded", "aria-label"];
function Fd(t, e, s, r, i, a) {
  return d(), c("section", {
    class: "card-body",
    "aria-expanded": t.expanded,
    "aria-label": t.ariaLabel
  }, [
    f("div", {
      class: q(["card-body__content", { "card-body__content--collapsed": !t.expanded }])
    }, [
      ie(t.$slots, "default", {}, void 0, !0)
    ], 2),
    t.collapsible ? (d(), c("button", {
      key: 0,
      class: "card-body__toggle",
      onClick: e[0] || (e[0] = (...n) => t.toggleExpand && t.toggleExpand(...n)),
      "aria-controls": "card-body-content"
    }, w(t.expanded ? "Collapse" : "Expand"), 1)) : P("", !0)
  ], 8, Md);
}
const oT = /* @__PURE__ */ A(Bd, [["render", Fd], ["__scopeId", "data-v-b7b4641a"]]), Ud = C({
  name: "CardFooter",
  props: {
    alignment: {
      type: String,
      default: "flex-start"
    }
  }
});
function jd(t, e, s, r, i, a) {
  return d(), c("footer", {
    class: "card-footer",
    style: ne({ justifyContent: t.alignment })
  }, [
    ie(t.$slots, "default", {}, void 0, !0)
  ], 4);
}
const lT = /* @__PURE__ */ A(Ud, [["render", jd], ["__scopeId", "data-v-7d9792f3"]]), Vd = C({
  name: "CardHeader",
  props: {
    title: {
      type: String,
      required: !0
    },
    subtitle: {
      type: String,
      default: ""
    },
    image: {
      type: String,
      default: ""
    },
    icon: {
      type: String,
      default: ""
    },
    ariaLabel: {
      type: String,
      default: "Card Header"
    }
  }
}), Hd = ["aria-label"], zd = ["src"], Gd = { class: "card-header__text" }, Kd = { class: "card-header__title" }, Wd = { class: "card-header__subtitle" };
function Zd(t, e, s, r, i, a) {
  return d(), c("header", {
    class: "card-header",
    "aria-label": t.ariaLabel
  }, [
    t.image ? (d(), c("img", {
      key: 0,
      src: t.image,
      alt: "",
      class: "card-header__image"
    }, null, 8, zd)) : P("", !0),
    t.icon ? (d(), c("i", {
      key: 1,
      class: q(`card-header__icon ${t.icon}`),
      "aria-hidden": "true"
    }, null, 2)) : P("", !0),
    f("div", Gd, [
      f("h1", Kd, w(t.title), 1),
      f("h2", Wd, w(t.subtitle), 1)
    ])
  ], 8, Hd);
}
const uT = /* @__PURE__ */ A(Vd, [["render", Zd], ["__scopeId", "data-v-4b83e7e6"]]), Xd = C({
  name: "CardImage",
  props: {
    src: {
      type: String,
      required: !0
    },
    caption: {
      type: String,
      default: ""
    },
    overlay: {
      type: String,
      default: ""
    }
  },
  setup() {
    return { hover: m(!1) };
  }
}), Yd = {
  key: 0,
  class: "caption"
}, Qd = {
  key: 1,
  class: "overlay"
};
function Jd(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "card-image",
    style: ne({ backgroundImage: `url(${t.src})` }),
    onMouseover: e[0] || (e[0] = (n) => t.hover = !0),
    onMouseleave: e[1] || (e[1] = (n) => t.hover = !1)
  }, [
    t.caption ? (d(), c("div", Yd, w(t.caption), 1)) : P("", !0),
    t.hover && t.overlay ? (d(), c("div", Qd, w(t.overlay), 1)) : P("", !0)
  ], 36);
}
const dT = /* @__PURE__ */ A(Xd, [["render", Jd], ["__scopeId", "data-v-62e35ada"]]), xd = C({
  name: "CardbasedList",
  props: {
    cards: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    const e = m(null), s = m(null);
    return { hoveredIndex: e, selectedIndex: s, selectCard: (i) => {
      t.cards[i].disabled && (s.value = i);
    } };
  }
}), ec = {
  class: "cardbased-list",
  role: "list"
}, tc = ["onMouseenter", "onClick", "aria-disabled"], sc = { class: "card-content" };
function nc(t, e, s, r, i, a) {
  return d(), c("div", ec, [
    (d(!0), c(I, null, L(t.cards, (n, o) => (d(), c("div", {
      key: o,
      class: q(["card", { hovered: t.hoveredIndex === o, selected: t.selectedIndex === o, disabled: n.disabled }]),
      onMouseenter: (u) => t.hoveredIndex = o,
      onMouseleave: e[0] || (e[0] = (u) => t.hoveredIndex = null),
      onClick: (u) => t.selectCard(o),
      "aria-disabled": n.disabled ? "true" : "false"
    }, [
      f("div", sc, [
        f("h3", null, w(n.title), 1),
        f("p", null, w(n.description), 1)
      ])
    ], 42, tc))), 128))
  ]);
}
const cT = /* @__PURE__ */ A(xd, [["render", nc], ["__scopeId", "data-v-342a232d"]]), rc = C({
  name: "Carousel",
  props: {
    slides: {
      type: Array,
      required: !0
    },
    interval: {
      type: Number,
      default: 3e3
    }
  },
  setup(t) {
    const e = m(0);
    let s = null;
    const r = () => {
      e.value = (e.value + 1) % t.slides.length;
    }, i = () => {
      e.value = (e.value - 1 + t.slides.length) % t.slides.length;
    }, a = () => {
      s = window.setInterval(r, t.interval);
    }, n = () => {
      s !== null && (clearInterval(s), s = null);
    };
    return Ce(a), Di(n), {
      currentIndex: e,
      nextSlide: r,
      prevSlide: i,
      autoPlay: a,
      pause: n
    };
  }
}), ic = {
  class: "carousel",
  role: "region",
  "aria-label": "Image carousel"
}, ac = ["aria-hidden"], oc = ["src", "alt"];
function lc(t, e, s, r, i, a) {
  return d(), c("div", ic, [
    f("div", {
      class: "carousel-inner",
      onMouseenter: e[0] || (e[0] = (...n) => t.pause && t.pause(...n)),
      onMouseleave: e[1] || (e[1] = (...n) => t.autoPlay && t.autoPlay(...n))
    }, [
      (d(!0), c(I, null, L(t.slides, (n, o) => (d(), c("div", {
        key: o,
        class: q(["carousel-item", { active: o === t.currentIndex }]),
        "aria-hidden": o !== t.currentIndex
      }, [
        f("img", {
          src: n.src,
          alt: n.alt
        }, null, 8, oc)
      ], 10, ac))), 128))
    ], 32),
    f("button", {
      class: "carousel-control prev",
      onClick: e[2] || (e[2] = (...n) => t.prevSlide && t.prevSlide(...n)),
      "aria-label": "Previous slide"
    }, "‹"),
    f("button", {
      class: "carousel-control next",
      onClick: e[3] || (e[3] = (...n) => t.nextSlide && t.nextSlide(...n)),
      "aria-label": "Next slide"
    }, "›")
  ]);
}
const fT = /* @__PURE__ */ A(rc, [["render", lc], ["__scopeId", "data-v-0a83c48d"]]), uc = C({
  name: "ChatBubble",
  props: {
    read: {
      type: Boolean,
      default: !1
    },
    unread: {
      type: Boolean,
      default: !1
    },
    active: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    return { isHovered: m(!1) };
  }
});
function dc(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["chat-bubble", { read: t.read, unread: t.unread, hover: t.isHovered, active: t.active }]),
    role: "alert",
    "aria-live": "polite",
    onMouseover: e[0] || (e[0] = (n) => t.isHovered = !0),
    onMouseleave: e[1] || (e[1] = (n) => t.isHovered = !1)
  }, [
    ie(t.$slots, "default", {}, void 0, !0)
  ], 34);
}
const pT = /* @__PURE__ */ A(uc, [["render", dc], ["__scopeId", "data-v-5ed7d014"]]), cc = C({
  name: "CheckList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    return { toggleCheck: (s) => {
      const r = t.items[s];
      r.disabled || (r.checked = !r.checked, r.indeterminate && (r.indeterminate = !1));
    } };
  }
}), fc = {
  class: "checklist",
  role: "group"
}, pc = ["id", "checked", ".indeterminate", "disabled", "onChange"], hc = ["for"];
function gc(t, e, s, r, i, a) {
  return d(), c("div", fc, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("div", {
      key: o,
      class: q(["checklist-item", { checked: n.checked, indeterminate: n.indeterminate, disabled: n.disabled }])
    }, [
      f("input", {
        type: "checkbox",
        id: "checkbox-" + o,
        checked: n.checked,
        ".indeterminate": n.indeterminate,
        disabled: n.disabled,
        onChange: (u) => t.toggleCheck(o)
      }, null, 40, pc),
      f("label", {
        for: "checkbox-" + o
      }, w(n.label), 9, hc)
    ], 2))), 128))
  ]);
}
const hT = /* @__PURE__ */ A(cc, [["render", gc], ["__scopeId", "data-v-daf9afeb"]]), mc = C({
  name: "Checkbox",
  props: {
    checked: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  }
}), vc = { class: "checkbox-container" }, bc = ["checked", "disabled", "aria-checked", "aria-disabled"];
function yc(t, e, s, r, i, a) {
  return d(), c("div", vc, [
    f("input", {
      type: "checkbox",
      checked: t.checked,
      disabled: t.disabled,
      onChange: e[0] || (e[0] = (n) => t.$emit("update:checked", n.target.checked)),
      "aria-checked": t.checked,
      "aria-disabled": t.disabled
    }, null, 40, bc),
    f("label", {
      class: q({ "checkbox--disabled": t.disabled })
    }, [
      ie(t.$slots, "default", {}, void 0, !0)
    ], 2)
  ]);
}
const gT = /* @__PURE__ */ A(mc, [["render", yc], ["__scopeId", "data-v-7926a921"]]), $c = C({
  name: "Chips",
  props: {
    selectable: {
      type: Boolean,
      default: !1
    },
    removable: {
      type: Boolean,
      default: !1
    },
    grouped: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    const t = m([
      { label: "Chip 1", selected: !1 },
      { label: "Chip 2", selected: !1 },
      { label: "Chip 3", selected: !1 }
    ]);
    return { chips: t, toggleSelect: (r) => {
      t.value[r].selected = !t.value[r].selected;
    }, removeChip: (r) => {
      t.value.splice(r, 1);
    } };
  }
}), kc = {
  class: "chip-container",
  role: "list"
}, wc = ["onClick", "aria-pressed"], Cc = ["onClick"];
function Ac(t, e, s, r, i, a) {
  return d(), c("div", kc, [
    (d(!0), c(I, null, L(t.chips, (n, o) => (d(), c("div", {
      key: o,
      class: q(["chip", { selectable: t.selectable, removable: t.removable }]),
      onClick: (u) => t.toggleSelect(o),
      role: "listitem",
      tabindex: "0",
      "aria-pressed": n.selected
    }, [
      f("span", null, w(n.label), 1),
      t.removable ? (d(), c("button", {
        key: 0,
        class: "remove-button",
        "aria-label": "Remove chip",
        onClick: de((u) => t.removeChip(o), ["stop"])
      }, " × ", 8, Cc)) : P("", !0)
    ], 10, wc))), 128))
  ]);
}
const mT = /* @__PURE__ */ A($c, [["render", Ac], ["__scopeId", "data-v-8a744eae"]]), Ec = C({
  name: "CollapsibleMenuList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    return { toggleExpand: (i) => {
      t.items[i].expanded = !t.items[i].expanded;
    }, hoverItem: (i) => {
      t.items[i].active = !0;
    }, unhoverItem: (i) => {
      t.items[i].active = !1;
    } };
  }
}), Sc = {
  class: "collapsible-menu-list",
  role: "menu"
}, Tc = ["onMouseenter", "onMouseleave"], _c = ["aria-expanded", "onClick"], Nc = {
  key: 0,
  class: "submenu",
  role: "menu"
};
function Ic(t, e, s, r, i, a) {
  return d(), c("ul", Sc, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("li", {
      key: o,
      class: q(["menu-item", { expanded: n.expanded, active: n.active }]),
      onMouseenter: (u) => t.hoverItem(o),
      onMouseleave: (u) => t.unhoverItem(o)
    }, [
      f("button", {
        class: "menu-button",
        "aria-expanded": n.expanded,
        onClick: (u) => t.toggleExpand(o)
      }, w(n.label), 9, _c),
      n.expanded ? (d(), c("ul", Nc, [
        (d(!0), c(I, null, L(n.subItems, (u, p) => (d(), c("li", {
          key: p,
          role: "menuitem"
        }, w(u), 1))), 128))
      ])) : P("", !0)
    ], 42, Tc))), 128))
  ]);
}
const vT = /* @__PURE__ */ A(Ec, [["render", Ic], ["__scopeId", "data-v-e135c15d"]]), Lc = C({
  name: "ColorPicker",
  setup() {
    const t = m(!1), e = m("#000000"), s = m(e.value), r = m(50), i = m(1), a = m([]), n = () => {
      t.value = !t.value;
    }, o = () => {
      /^#[0-9A-F]{6}$/i.test(s.value) && (e.value = s.value, u(s.value));
    }, u = (g) => {
      a.value.includes(g) || (a.value.push(g), a.value.length > 5 && a.value.shift());
    }, p = (g) => {
      e.value = g, s.value = g;
    };
    return fs(e, (g) => {
      s.value = g, u(g);
    }), {
      isActive: t,
      selectedColor: e,
      hexCode: s,
      brightness: r,
      opacity: i,
      colorHistory: a,
      toggleActive: n,
      updateColorFromHex: o,
      selectColorFromHistory: p
    };
  }
}), qc = ["aria-pressed"], Oc = {
  key: 0,
  class: "color-settings"
}, Pc = {
  class: "color-history",
  "aria-label": "Color History"
}, Dc = ["onClick"];
function Rc(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["color-picker", { active: t.isActive }])
  }, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleActive && t.toggleActive(...n)),
      "aria-pressed": t.isActive,
      class: "color-button"
    }, "Color Picker", 8, qc),
    t.isActive ? (d(), c("div", Oc, [
      R(f("input", {
        type: "color",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.selectedColor = n),
        "aria-label": "Select Color"
      }, null, 512), [
        [H, t.selectedColor]
      ]),
      e[6] || (e[6] = f("label", { for: "hexCode" }, "Hex Code", -1)),
      R(f("input", {
        id: "hexCode",
        type: "text",
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.hexCode = n),
        onInput: e[3] || (e[3] = (...n) => t.updateColorFromHex && t.updateColorFromHex(...n)),
        "aria-live": "polite"
      }, null, 544), [
        [H, t.hexCode]
      ]),
      e[7] || (e[7] = f("label", { for: "brightness" }, "Brightness", -1)),
      R(f("input", {
        id: "brightness",
        type: "range",
        "onUpdate:modelValue": e[4] || (e[4] = (n) => t.brightness = n),
        min: "0",
        max: "100",
        "aria-valuemin": "0",
        "aria-valuemax": "100",
        "aria-valuenow": "brightness"
      }, null, 512), [
        [H, t.brightness]
      ]),
      e[8] || (e[8] = f("label", { for: "opacity" }, "Opacity", -1)),
      R(f("input", {
        id: "opacity",
        type: "range",
        "onUpdate:modelValue": e[5] || (e[5] = (n) => t.opacity = n),
        min: "0",
        max: "1",
        step: "0.01",
        "aria-valuemin": "0",
        "aria-valuemax": "1",
        "aria-valuenow": "opacity"
      }, null, 512), [
        [H, t.opacity]
      ]),
      f("div", Pc, [
        (d(!0), c(I, null, L(t.colorHistory, (n) => (d(), c("span", {
          key: n,
          style: ne({ backgroundColor: n }),
          class: "color-swatch",
          onClick: (o) => t.selectColorFromHistory(n)
        }, null, 12, Dc))), 128))
      ])
    ])) : P("", !0)
  ], 2);
}
const bT = /* @__PURE__ */ A(Lc, [["render", Rc], ["__scopeId", "data-v-bef9cfe2"]]), Bc = C({
  name: "ColumnVisibilityToggle",
  props: {
    columns: {
      type: Array,
      default: () => []
    }
  },
  setup(t, { emit: e }) {
    return {
      toggleColumnVisibility: (r) => {
        t.columns[r].visible = !t.columns[r].visible, e("update:columns", t.columns);
      }
    };
  }
}), Mc = { class: "column-visibility-toggle" }, Fc = ["onClick", "aria-pressed"];
function Uc(t, e, s, r, i, a) {
  return d(), c("div", Mc, [
    f("ul", null, [
      (d(!0), c(I, null, L(t.columns, (n, o) => (d(), c("li", {
        key: n.name
      }, [
        f("button", {
          onClick: (u) => t.toggleColumnVisibility(o),
          "aria-pressed": n.visible
        }, w(n.visible ? "Hide" : "Show") + " " + w(n.name), 9, Fc)
      ]))), 128))
    ])
  ]);
}
const yT = /* @__PURE__ */ A(Bc, [["render", Uc], ["__scopeId", "data-v-b2e7ed29"]]), jc = C({
  name: "CommandPalette",
  props: {
    isOpen: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    const t = m(""), e = m([
      { id: 1, name: "Command 1" },
      { id: 2, name: "Command 2" },
      { id: 3, name: "Command 3" }
    ]), s = m(0), r = W(
      () => e.value.filter(
        (o) => o.name.toLowerCase().includes(t.value.toLowerCase())
      )
    ), i = () => {
      s.value < r.value.length - 1 && s.value++;
    }, a = () => {
      s.value > 0 && s.value--;
    }, n = (o) => {
      console.log("Selected command:", o.name);
    };
    return Ce(() => {
      r.value.length > 0 && (s.value = 0);
    }), { searchQuery: t, filteredCommands: r, activeIndex: s, focusNext: i, focusPrev: a, selectCommand: n };
  }
}), Vc = {
  class: "command-palette",
  role: "dialog",
  "aria-modal": "true",
  "aria-labelledby": "command-palette-title"
}, Hc = { class: "command-palette-content" }, zc = {
  id: "command-list",
  class: "command-list",
  role: "listbox"
}, Gc = ["onClick", "onKeydown"];
function Kc(t, e, s, r, i, a) {
  return R((d(), c("div", Vc, [
    f("div", Hc, [
      R(f("input", {
        type: "text",
        "onUpdate:modelValue": e[0] || (e[0] = (n) => t.searchQuery = n),
        class: "command-palette-input",
        placeholder: "Type a command...",
        "aria-controls": "command-list",
        onKeydown: [
          e[1] || (e[1] = Rs(de((...n) => t.focusNext && t.focusNext(...n), ["prevent"]), ["arrow-down"])),
          e[2] || (e[2] = Rs(de((...n) => t.focusPrev && t.focusPrev(...n), ["prevent"]), ["arrow-up"]))
        ]
      }, null, 544), [
        [H, t.searchQuery]
      ]),
      f("ul", zc, [
        (d(!0), c(I, null, L(t.filteredCommands, (n, o) => (d(), c("li", {
          key: n.id,
          class: q({ active: o === t.activeIndex }),
          role: "option",
          tabindex: "0",
          onClick: (u) => t.selectCommand(n),
          onKeydown: [
            Rs(de((u) => t.selectCommand(n), ["prevent"]), ["enter"]),
            Rs(de((u) => t.selectCommand(n), ["prevent"]), ["space"])
          ]
        }, w(n.name), 43, Gc))), 128))
      ])
    ])
  ], 512)), [
    [lo, t.isOpen]
  ]);
}
const $T = /* @__PURE__ */ A(jc, [["render", Kc], ["__scopeId", "data-v-a21814e7"]]), Wc = C({
  name: "CommunityCards",
  props: {
    cards: {
      type: Array,
      required: !0
    }
  }
}), Zc = {
  class: "community-cards",
  role: "group",
  "aria-label": "Community Cards"
}, Xc = {
  key: 0,
  x: "50",
  y: "75",
  "text-anchor": "middle",
  class: "card-text"
};
function Yc(t, e, s, r, i, a) {
  return d(), c("div", Zc, [
    (d(!0), c(I, null, L(t.cards, (n) => (d(), c("svg", {
      key: n.id,
      class: q("card " + n.state),
      viewBox: "0 0 100 150",
      xmlns: "http://www.w3.org/2000/svg",
      "aria-hidden": "true"
    }, [
      e[0] || (e[0] = f("rect", {
        width: "100",
        height: "150",
        rx: "10",
        ry: "10",
        class: "card-background"
      }, null, -1)),
      n.state === "revealed" ? (d(), c("text", Xc, w(n.label), 1)) : P("", !0)
    ], 2))), 128))
  ]);
}
const kT = /* @__PURE__ */ A(Wc, [["render", Yc], ["__scopeId", "data-v-5f3f241e"]]), Qc = C({
  name: "ContextualList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    return { triggerAction: (r) => {
      t.items[r].actionTriggered = !0;
    }, dismissItem: (r) => {
      t.items[r].dismissed = !0;
    } };
  }
}), Jc = {
  class: "contextual-list",
  role: "list"
}, xc = ["onClick"], ef = ["onClick"];
function tf(t, e, s, r, i, a) {
  return d(), c("div", Jc, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("div", {
      key: o,
      class: q(["list-item", { actionTriggered: n.actionTriggered, dismissed: n.dismissed }])
    }, [
      f("span", null, w(n.label), 1),
      f("button", {
        onClick: (u) => t.triggerAction(o)
      }, "Action", 8, xc),
      f("button", {
        onClick: (u) => t.dismissItem(o)
      }, "Dismiss", 8, ef)
    ], 2))), 128))
  ]);
}
const wT = /* @__PURE__ */ A(Qc, [["render", tf], ["__scopeId", "data-v-85d407db"]]), sf = C({
  name: "ContextualNavigation",
  props: {
    menuItems: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m(!1);
    return {
      isVisible: t,
      toggleMenu: () => {
        t.value = !t.value;
      }
    };
  }
}), nf = ["aria-hidden"], rf = ["aria-expanded"], af = { key: 0 }, of = { key: 1 }, lf = {
  key: 0,
  class: "contextual-menu",
  role: "menu"
}, uf = ["href"];
function df(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "contextual-navigation",
    "aria-hidden": !t.isVisible
  }, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleMenu && t.toggleMenu(...n)),
      class: "contextual-toggle",
      "aria-expanded": t.isVisible
    }, [
      t.isVisible ? (d(), c("span", af, "Close Menu")) : (d(), c("span", of, "Open Menu"))
    ], 8, rf),
    t.isVisible ? (d(), c("div", lf, [
      f("ul", null, [
        (d(!0), c(I, null, L(t.menuItems, (n, o) => (d(), c("li", {
          key: o,
          role: "menuitem"
        }, [
          f("a", {
            href: n.link
          }, w(n.name), 9, uf)
        ]))), 128))
      ])
    ])) : P("", !0)
  ], 8, nf);
}
const CT = /* @__PURE__ */ A(sf, [["render", df], ["__scopeId", "data-v-12a7fc2e"]]), cf = C({
  name: "CountdownTimer",
  props: {
    duration: {
      type: Number,
      required: !0
    }
  },
  setup(t) {
    const e = m(t.duration), s = m(!1), r = m(null), i = W(() => {
      const p = Math.floor(e.value / 60).toString().padStart(2, "0"), g = (e.value % 60).toString().padStart(2, "0");
      return `${p}:${g}`;
    }), a = W(() => e.value <= 0 ? "completed" : s.value ? "paused" : "running"), n = W(() => e.value <= 0), o = () => {
      n.value || (s.value = !s.value, s.value || u());
    }, u = () => {
      r.value !== null && clearInterval(r.value), r.value = window.setInterval(() => {
        !s.value && e.value > 0 && (e.value -= 1);
      }, 1e3);
    };
    return Ce(() => {
      u();
    }), Di(() => {
      r.value !== null && clearInterval(r.value);
    }), { formattedTime: i, timerState: a, isPaused: s, togglePause: o, isCompleted: n };
  }
}), ff = ["aria-live"];
function pf(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "countdown-timer",
    role: "timer",
    "aria-live": t.isCompleted ? "off" : "assertive"
  }, [
    f("span", {
      class: q(t.timerState)
    }, w(t.formattedTime), 3),
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.togglePause && t.togglePause(...n)),
      "aria-label": "Pause or resume countdown"
    }, w(t.isPaused ? "Resume" : "Pause"), 1)
  ], 8, ff);
}
const AT = /* @__PURE__ */ A(cf, [["render", pf], ["__scopeId", "data-v-c87bdf2c"]]), hf = C({
  name: "DarkModeToggle",
  setup() {
    const t = m(!1);
    return { isDarkMode: t, toggleMode: () => {
      t.value = !t.value, document.documentElement.setAttribute("data-theme", t.value ? "dark" : "light");
    } };
  }
}), gf = ["aria-pressed"], mf = {
  key: 0,
  "aria-hidden": "true"
}, vf = {
  key: 1,
  "aria-hidden": "true"
}, bf = { class: "sr-only" };
function yf(t, e, s, r, i, a) {
  return d(), c("button", {
    class: "dark-mode-toggle",
    "aria-pressed": t.isDarkMode,
    onClick: e[0] || (e[0] = (...n) => t.toggleMode && t.toggleMode(...n))
  }, [
    t.isDarkMode ? (d(), c("span", mf, "🌙")) : (d(), c("span", vf, "☀️")),
    f("span", bf, w(t.isDarkMode ? "Switch to light mode" : "Switch to dark mode"), 1)
  ], 8, gf);
}
const ET = /* @__PURE__ */ A(hf, [["render", yf], ["__scopeId", "data-v-744ba664"]]), $f = C({
  name: "DataExportButton",
  props: {
    availableFormats: {
      type: Array,
      default: () => ["csv", "excel", "pdf"]
    },
    dataAvailable: {
      type: Boolean,
      default: !0
    }
  },
  setup(t) {
    const e = m(!1);
    return {
      isExporting: e,
      startExport: async (r) => {
        if (!(!t.dataAvailable || e.value)) {
          console.log(r), e.value = !0;
          try {
            await new Promise((i) => setTimeout(i, 2e3));
          } finally {
            e.value = !1;
          }
        }
      }
    };
  }
}), kf = { class: "data-export-button" }, wf = ["onClick", "disabled"], Cf = {
  key: 0,
  class: "loading-indicator"
};
function Af(t, e, s, r, i, a) {
  return d(), c("div", kf, [
    (d(!0), c(I, null, L(t.availableFormats, (n) => (d(), c("button", {
      key: n,
      onClick: (o) => t.startExport(n),
      disabled: !t.dataAvailable || t.isExporting
    }, " Export as " + w(n.toUpperCase()), 9, wf))), 128)),
    t.isExporting ? (d(), c("div", Cf, "Exporting...")) : P("", !0)
  ]);
}
const ST = /* @__PURE__ */ A($f, [["render", Af], ["__scopeId", "data-v-0af20d1b"]]), Ef = C({
  name: "DataFilterPanel",
  props: {
    filters: {
      type: Array,
      required: !0
    },
    disabled: Boolean
  },
  setup(t) {
    const e = m([...t.filters]), s = m(!0), r = () => {
      s.value = !s.value;
    }, i = () => {
    }, a = () => {
      e.value = t.filters.map((n) => ({ ...n, value: null }));
    };
    return fs(e, i, { deep: !0 }), {
      activeFilters: e,
      isPanelCollapsed: s,
      togglePanel: r,
      clearFilters: a
    };
  }
}), Sf = {
  key: 0,
  class: "filters"
}, Tf = { key: 0 }, _f = ["onUpdate:modelValue", "disabled"], Nf = { key: 1 }, If = ["onUpdate:modelValue", "disabled"], Lf = ["value"], qf = { key: 2 }, Of = ["onUpdate:modelValue", "disabled"], Pf = ["disabled"];
function Df(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["data-filter-panel", { disabled: t.disabled }])
  }, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.togglePanel && t.togglePanel(...n))
    }, w(t.isPanelCollapsed ? "Show Filters" : "Hide Filters"), 1),
    t.isPanelCollapsed ? P("", !0) : (d(), c("div", Sf, [
      (d(!0), c(I, null, L(t.activeFilters, (n, o) => (d(), c("div", {
        key: o,
        class: "filter"
      }, [
        f("label", null, w(n.label), 1),
        n.type === "text" ? (d(), c("div", Tf, [
          R(f("input", {
            type: "text",
            "onUpdate:modelValue": (u) => n.value = u,
            disabled: t.disabled
          }, null, 8, _f), [
            [H, n.value]
          ])
        ])) : n.type === "dropdown" ? (d(), c("div", Nf, [
          R(f("select", {
            "onUpdate:modelValue": (u) => n.value = u,
            disabled: t.disabled
          }, [
            (d(!0), c(I, null, L(n.options, (u) => (d(), c("option", {
              key: u,
              value: u
            }, w(u), 9, Lf))), 128))
          ], 8, If), [
            [ye, n.value]
          ])
        ])) : n.type === "date" ? (d(), c("div", qf, [
          R(f("input", {
            type: "date",
            "onUpdate:modelValue": (u) => n.value = u,
            disabled: t.disabled
          }, null, 8, Of), [
            [H, n.value]
          ])
        ])) : P("", !0)
      ]))), 128)),
      f("button", {
        onClick: e[1] || (e[1] = (...n) => t.clearFilters && t.clearFilters(...n)),
        disabled: t.disabled
      }, "Clear Filters", 8, Pf)
    ]))
  ], 2);
}
const TT = /* @__PURE__ */ A(Ef, [["render", Df], ["__scopeId", "data-v-2739f835"]]), Rf = C({
  name: "DataGrid",
  props: {
    headers: {
      type: Array,
      required: !0
    },
    data: {
      type: Array,
      required: !0
    },
    paginationEnabled: {
      type: Boolean,
      default: !1
    },
    searchEnabled: {
      type: Boolean,
      default: !1
    },
    resizable: {
      type: Boolean,
      default: !1
    },
    itemsPerPage: {
      type: Number,
      default: 10
    }
  },
  setup(t) {
    const e = m(1), s = m(""), r = W(() => {
      let o = t.data;
      if (t.searchEnabled && s.value && (o = o.filter(
        (u) => u.some((p) => p.toLowerCase().includes(s.value.toLowerCase()))
      )), t.paginationEnabled) {
        const u = (e.value - 1) * t.itemsPerPage;
        return o.slice(u, u + t.itemsPerPage);
      }
      return o;
    }), i = W(() => Math.ceil(t.data.length / t.itemsPerPage));
    return { page: e, searchQuery: s, filteredData: r, totalPages: i, prevPage: () => {
      e.value > 1 && (e.value -= 1);
    }, nextPage: () => {
      e.value < i.value && (e.value += 1);
    } };
  }
}), Bf = {
  class: "data-grid",
  role: "grid"
}, Mf = {
  key: 0,
  class: "search-bar"
}, Ff = {
  key: 1,
  class: "pagination"
}, Uf = ["disabled"], jf = ["disabled"];
function Vf(t, e, s, r, i, a) {
  return d(), c("div", Bf, [
    t.searchEnabled ? (d(), c("div", Mf, [
      R(f("input", {
        type: "text",
        "onUpdate:modelValue": e[0] || (e[0] = (n) => t.searchQuery = n),
        placeholder: "Search...",
        "aria-label": "Search Data Grid"
      }, null, 512), [
        [H, t.searchQuery]
      ])
    ])) : P("", !0),
    f("table", null, [
      f("thead", null, [
        f("tr", null, [
          (d(!0), c(I, null, L(t.headers, (n, o) => (d(), c("th", {
            key: o,
            style: ne({ width: t.resizable ? "auto" : "initial" })
          }, w(n), 5))), 128))
        ])
      ]),
      f("tbody", null, [
        (d(!0), c(I, null, L(t.filteredData, (n, o) => (d(), c("tr", { key: o }, [
          (d(!0), c(I, null, L(n, (u, p) => (d(), c("td", { key: p }, w(u), 1))), 128))
        ]))), 128))
      ])
    ]),
    t.paginationEnabled ? (d(), c("div", Ff, [
      f("button", {
        onClick: e[1] || (e[1] = (...n) => t.prevPage && t.prevPage(...n)),
        disabled: t.page === 1,
        "aria-label": "Previous Page"
      }, "Previous", 8, Uf),
      f("span", null, "Page " + w(t.page) + " of " + w(t.totalPages), 1),
      f("button", {
        onClick: e[2] || (e[2] = (...n) => t.nextPage && t.nextPage(...n)),
        disabled: t.page === t.totalPages,
        "aria-label": "Next Page"
      }, "Next", 8, jf)
    ])) : P("", !0)
  ]);
}
const _T = /* @__PURE__ */ A(Rf, [["render", Vf], ["__scopeId", "data-v-804b97db"]]), Hf = C({
  name: "DataImportDialog",
  setup() {
    const t = m(null), e = m(!1), s = m(!1), r = m(null);
    return {
      file: t,
      importing: e,
      success: s,
      error: r,
      onFileChange: (n) => {
        const o = n.target;
        o.files && (t.value = o.files[0]);
      },
      importData: async () => {
        if (!t.value) {
          r.value = "No file selected";
          return;
        }
        e.value = !0, r.value = null;
        try {
          await new Promise((n) => setTimeout(n, 2e3)), s.value = !0;
        } catch {
          r.value = "Import failed";
        } finally {
          e.value = !1;
        }
      }
    };
  }
}), zf = {
  class: "data-import-dialog",
  role: "dialog",
  "aria-labelledby": "dialog-title"
}, Gf = ["disabled"], Kf = {
  key: 0,
  class: "progress-indicator",
  "aria-live": "polite"
}, Wf = {
  key: 1,
  class: "success-message",
  "aria-live": "polite"
}, Zf = {
  key: 2,
  class: "error-message",
  "aria-live": "assertive"
};
function Xf(t, e, s, r, i, a) {
  return d(), c("div", zf, [
    e[2] || (e[2] = f("h2", { id: "dialog-title" }, "Import Data", -1)),
    f("input", {
      type: "file",
      onChange: e[0] || (e[0] = (...n) => t.onFileChange && t.onFileChange(...n)),
      accept: ".csv, .xls, .xlsx",
      "aria-label": "File upload"
    }, null, 32),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.importData && t.importData(...n)),
      disabled: t.importing || !t.file
    }, " Import ", 8, Gf),
    t.importing ? (d(), c("div", Kf, " Importing... ")) : P("", !0),
    t.success ? (d(), c("div", Wf, " Import successful! ")) : P("", !0),
    t.error ? (d(), c("div", Zf, w(t.error), 1)) : P("", !0)
  ]);
}
const NT = /* @__PURE__ */ A(Hf, [["render", Xf], ["__scopeId", "data-v-520df743"]]), Yf = C({
  name: "DataSummary",
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  setup(t) {
    const e = m(null), s = m(null), r = m(null), i = m(null);
    return fs(() => t.data, () => {
      try {
        if (!t.data.length) throw new Error("No data available");
        e.value = t.data.reduce((n, o) => n + o, 0), s.value = e.value / t.data.length, r.value = t.data.length, i.value = null;
      } catch (n) {
        i.value = n.message, e.value = null, s.value = null, r.value = null;
      }
    }, { immediate: !0 }), {
      total: e,
      average: s,
      count: r,
      error: i
    };
  }
}), Qf = { class: "data-summary" }, Jf = {
  key: 0,
  class: "error-message",
  role: "alert"
}, xf = { key: 1 };
function ep(t, e, s, r, i, a) {
  return d(), c("div", Qf, [
    t.error ? (d(), c("div", Jf, w(t.error), 1)) : (d(), c("div", xf, [
      f("div", null, "Total: " + w(t.total), 1),
      f("div", null, "Average: " + w(t.average), 1),
      f("div", null, "Count: " + w(t.count), 1)
    ]))
  ]);
}
const IT = /* @__PURE__ */ A(Yf, [["render", ep], ["__scopeId", "data-v-e55471fe"]]), tp = C({
  name: "DataTable",
  props: {
    columns: {
      type: Array,
      required: !0
    },
    rows: {
      type: Array,
      required: !0
    },
    loading: Boolean,
    pagination: Boolean,
    itemsPerPage: {
      type: Number,
      default: 10
    }
  },
  setup(t) {
    const e = m(1);
    return {
      paginatedRows: W(() => {
        if (!t.pagination) return t.rows;
        const i = (e.value - 1) * t.itemsPerPage, a = e.value * t.itemsPerPage;
        return t.rows.slice(i, a);
      }),
      currentPage: e,
      toggleSort: (i) => {
        console.log(i);
      }
    };
  }
}), sp = ["aria-busy"], np = ["onClick"], rp = { key: 1 }, ip = {
  key: 0,
  class: "pagination-controls"
}, ap = ["disabled"], op = ["disabled"];
function lp(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "data-table",
    "aria-busy": t.loading
  }, [
    f("table", null, [
      f("thead", null, [
        f("tr", null, [
          (d(!0), c(I, null, L(t.columns, (n) => (d(), c("th", {
            key: n.key,
            style: ne({ width: n.width, textAlign: n.align })
          }, [
            n.sortable ? (d(), c("button", {
              key: 0,
              onClick: (o) => t.toggleSort(n.key)
            }, w(n.label), 9, np)) : (d(), c("span", rp, w(n.label), 1))
          ], 4))), 128))
        ])
      ]),
      f("tbody", null, [
        (d(!0), c(I, null, L(t.paginatedRows, (n) => (d(), c("tr", {
          key: n.id
        }, [
          (d(!0), c(I, null, L(t.columns, (o) => (d(), c("td", {
            key: o.key
          }, w(n[o.key]), 1))), 128))
        ]))), 128))
      ])
    ]),
    t.pagination ? (d(), c("div", ip, [
      f("button", {
        onClick: e[0] || (e[0] = (n) => t.currentPage--),
        disabled: t.currentPage === 1
      }, "Previous", 8, ap),
      f("button", {
        onClick: e[1] || (e[1] = (n) => t.currentPage++),
        disabled: t.currentPage * t.itemsPerPage >= t.rows.length
      }, "Next", 8, op)
    ])) : P("", !0)
  ], 8, sp);
}
const LT = /* @__PURE__ */ A(tp, [["render", lp], ["__scopeId", "data-v-c061f510"]]), up = C({
  name: "DateAndTimePicker",
  props: {
    selectedDate: {
      type: String,
      default: ""
    },
    selectedTime: {
      type: String,
      default: ""
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  methods: {
    updateDate(t) {
      const e = t.target;
      this.$emit("update:selectedDate", e.value);
    },
    updateTime(t) {
      const e = t.target;
      this.$emit("update:selectedTime", e.value);
    }
  }
}), dp = { class: "date-time-picker-container" }, cp = ["value", "disabled", "aria-disabled"], fp = ["value", "disabled", "aria-disabled"];
function pp(t, e, s, r, i, a) {
  return d(), c("div", dp, [
    f("input", {
      type: "date",
      value: t.selectedDate,
      disabled: t.disabled,
      onInput: e[0] || (e[0] = (...n) => t.updateDate && t.updateDate(...n)),
      "aria-label": "Select Date",
      "aria-disabled": t.disabled
    }, null, 40, cp),
    f("input", {
      type: "time",
      value: t.selectedTime,
      disabled: t.disabled,
      onInput: e[1] || (e[1] = (...n) => t.updateTime && t.updateTime(...n)),
      "aria-label": "Select Time",
      "aria-disabled": t.disabled
    }, null, 40, fp)
  ]);
}
const qT = /* @__PURE__ */ A(up, [["render", pp], ["__scopeId", "data-v-5121df4f"]]), hp = C({
  name: "DatePicker",
  props: {
    startDate: {
      type: String,
      default: ""
    },
    endDate: {
      type: String,
      default: ""
    },
    selectedTime: {
      type: String,
      default: ""
    },
    isDateRange: {
      type: Boolean,
      default: !1
    },
    isTimePicker: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  methods: {
    updateStartDate(t) {
      const e = t.target;
      this.$emit("update:startDate", e.value);
    },
    updateEndDate(t) {
      const e = t.target;
      this.$emit("update:endDate", e.value);
    },
    updateTime(t) {
      const e = t.target;
      this.$emit("update:selectedTime", e.value);
    }
  }
}), gp = { class: "date-picker-container" }, mp = ["value", "disabled", "aria-disabled"], vp = ["value", "disabled", "aria-disabled"], bp = ["value", "disabled", "aria-disabled"];
function yp(t, e, s, r, i, a) {
  return d(), c("div", gp, [
    f("input", {
      type: "date",
      value: t.startDate,
      disabled: t.disabled,
      onInput: e[0] || (e[0] = (...n) => t.updateStartDate && t.updateStartDate(...n)),
      "aria-label": "Start Date",
      "aria-disabled": t.disabled
    }, null, 40, mp),
    t.isDateRange ? (d(), c("input", {
      key: 0,
      type: "date",
      value: t.endDate,
      disabled: t.disabled,
      onInput: e[1] || (e[1] = (...n) => t.updateEndDate && t.updateEndDate(...n)),
      "aria-label": "End Date",
      "aria-disabled": t.disabled
    }, null, 40, vp)) : P("", !0),
    t.isTimePicker ? (d(), c("input", {
      key: 1,
      type: "time",
      value: t.selectedTime,
      disabled: t.disabled,
      onInput: e[2] || (e[2] = (...n) => t.updateTime && t.updateTime(...n)),
      "aria-label": "Time Picker",
      "aria-disabled": t.disabled
    }, null, 40, bp)) : P("", !0)
  ]);
}
const OT = /* @__PURE__ */ A(hp, [["render", yp], ["__scopeId", "data-v-e00e68cd"]]), $p = C({
  name: "DealerButton",
  props: {
    state: {
      type: String,
      default: "default",
      validator: (t) => ["default", "moving", "hovered"].includes(t)
    }
  },
  computed: {
    stateClass() {
      return this.state;
    }
  }
});
function kp(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["dealer-button", t.stateClass]),
    "aria-label": "Dealer Button"
  }, " D ", 2);
}
const PT = /* @__PURE__ */ A($p, [["render", kp], ["__scopeId", "data-v-66f3c7ea"]]), wp = C({
  name: "DeckOfCards",
  props: {
    cards: {
      type: Array,
      required: !0
    },
    overlap: {
      type: Number,
      default: 10
    }
  },
  setup(t) {
    const e = m(null);
    return { onDragStart: (i) => {
      e.value = i;
    }, onDrop: (i) => {
      if (e.value !== null && e.value !== i) {
        const [a] = t.cards.splice(e.value, 1);
        t.cards.splice(i, 0, a);
      }
      e.value = null;
    } };
  }
}), Cp = {
  class: "deck",
  role: "list",
  "aria-label": "Deck of Cards"
}, Ap = ["onDragstart", "onDrop"];
function Ep(t, e, s, r, i, a) {
  return d(), c("div", Cp, [
    (d(!0), c(I, null, L(t.cards, (n, o) => (d(), c("div", {
      key: n.id,
      class: "card",
      style: ne({ zIndex: o, transform: `translateY(${o * t.overlap}px)` }),
      role: "listitem",
      "aria-label": "Card",
      draggable: "true",
      onDragstart: (u) => t.onDragStart(o),
      onDragover: e[0] || (e[0] = de(() => {
      }, ["prevent"])),
      onDrop: (u) => t.onDrop(o)
    }, [
      ie(t.$slots, "default", { card: n }, void 0, !0)
    ], 44, Ap))), 128))
  ]);
}
const DT = /* @__PURE__ */ A(wp, [["render", Ep], ["__scopeId", "data-v-4591d50a"]]), Sp = C({
  name: "DiscardPile",
  props: {
    cards: {
      type: Array,
      required: !0
    },
    maxCards: {
      type: Number,
      default: 10
    },
    overlapOffset: {
      type: Number,
      default: 5
    }
  },
  setup(t) {
    const e = m([...t.cards]), s = m(!1), r = W(() => e.value.length === 0), i = W(() => e.value.length >= t.maxCards);
    return {
      cards: e,
      isEmpty: r,
      isFull: i,
      isHovered: s,
      handleDragOver: () => {
        s.value = !0;
      },
      handleDragLeave: () => {
        s.value = !1;
      }
    };
  }
}), Tp = {
  key: 0,
  class: "empty-notification"
}, _p = {
  key: 1,
  class: "full-notification"
};
function Np(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["discard-pile", { empty: t.isEmpty, full: t.isFull, hovered: t.isHovered }]),
    onDragover: e[0] || (e[0] = de((...n) => t.handleDragOver && t.handleDragOver(...n), ["prevent"])),
    onDragleave: e[1] || (e[1] = (...n) => t.handleDragLeave && t.handleDragLeave(...n))
  }, [
    (d(!0), c(I, null, L(t.cards, (n, o) => (d(), c("div", {
      key: n.id,
      class: "card",
      style: ne({ top: `${o * t.overlapOffset}px`, left: `${o * t.overlapOffset}px` })
    }, [
      ie(t.$slots, "card", { card: n }, void 0, !0)
    ], 4))), 128)),
    t.isEmpty ? (d(), c("div", Tp, "Pile is empty")) : P("", !0),
    t.isFull ? (d(), c("div", _p, "Pile is full")) : P("", !0)
  ], 34);
}
const RT = /* @__PURE__ */ A(Sp, [["render", Np], ["__scopeId", "data-v-d1a5b2af"]]), Ip = C({
  name: "DragAndDropScheduler",
  props: {
    events: {
      type: Array,
      requried: !0,
      default: [
        { id: 1, title: "Default Meeting", position: 0, duration: 60, isDragging: !1 }
      ]
    }
  },
  setup() {
    const t = Array.from({ length: 24 }, (i, a) => a), e = m([
      { id: 1, title: "Meeting", position: 0, duration: 60, isDragging: !1 }
      // More events...
    ]);
    return {
      timeSlots: t,
      events: e,
      onDragStart: (i) => {
        i.isDragging = !0;
      },
      onDragEnd: (i) => {
        i.isDragging = !1;
      }
    };
  }
}), Lp = {
  class: "scheduler",
  role: "application",
  "aria-label": "Drag and Drop Scheduler"
}, qp = ["onDragstart", "onDragend"];
function Op(t, e, s, r, i, a) {
  return d(), c("div", Lp, [
    (d(!0), c(I, null, L(t.timeSlots, (n) => (d(), c("div", {
      class: "time-slot",
      key: n,
      "aria-label": "Time Slot"
    }, [
      (d(!0), c(I, null, L(t.events, (o) => (d(), c("div", {
        key: o.id,
        class: q(["event", { dragging: o.isDragging }]),
        style: ne({ top: o.position + "px", height: o.duration + "px" }),
        draggable: "true",
        onDragstart: (u) => t.onDragStart(o),
        onDragend: (u) => t.onDragEnd(o)
      }, w(o.title), 47, qp))), 128))
    ]))), 128))
  ]);
}
const BT = /* @__PURE__ */ A(Ip, [["render", Op], ["__scopeId", "data-v-25e365d3"]]), Pp = C({
  name: "DropdownMenu",
  props: {
    menuItems: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m(!1), e = m(null);
    return {
      isExpanded: t,
      toggleDropdown: () => {
        t.value = !t.value;
      },
      activeIndex: e,
      hoverItem: (a) => {
        e.value = a;
      },
      leaveItem: () => {
        e.value = null;
      }
    };
  }
}), Dp = { class: "dropdown-menu" }, Rp = ["aria-expanded"], Bp = {
  key: 0,
  role: "menu",
  class: "dropdown-list"
}, Mp = ["href", "onMouseover"];
function Fp(t, e, s, r, i, a) {
  return d(), c("div", Dp, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleDropdown && t.toggleDropdown(...n)),
      class: "dropdown-toggle",
      "aria-expanded": t.isExpanded
    }, " Menu ", 8, Rp),
    t.isExpanded ? (d(), c("ul", Bp, [
      (d(!0), c(I, null, L(t.menuItems, (n, o) => (d(), c("li", {
        key: o,
        role: "menuitem"
      }, [
        f("a", {
          href: n.link,
          onMouseover: (u) => t.hoverItem(o),
          onMouseleave: e[1] || (e[1] = (...u) => t.leaveItem && t.leaveItem(...u)),
          class: q({ active: t.activeIndex === o })
        }, w(n.name), 43, Mp)
      ]))), 128))
    ])) : P("", !0)
  ]);
}
const MT = /* @__PURE__ */ A(Pp, [["render", Fp], ["__scopeId", "data-v-f56e06f8"]]), Up = C({
  name: "EditableDataTable",
  props: {
    columns: {
      type: Array,
      required: !0
    },
    rows: {
      type: Array,
      required: !0
    },
    pagination: Boolean,
    itemsPerPage: {
      type: Number,
      default: 10
    }
  },
  setup(t) {
    const e = m(1), s = m(null), r = m([...t.rows]), i = W(() => {
      if (!t.pagination) return r.value;
      const u = (e.value - 1) * t.itemsPerPage, p = e.value * t.itemsPerPage;
      return r.value.slice(u, p);
    }), a = (u) => {
      s.value = s.value === u ? null : u;
    };
    return {
      paginatedRows: i,
      currentPage: e,
      editingRow: s,
      toggleEditRow: a,
      saveRow: (u) => {
        a(u);
      },
      deleteRow: (u) => {
        r.value.splice(u, 1);
      },
      editedRows: r
    };
  }
}), jp = { class: "editable-data-table" }, Vp = { key: 0 }, Hp = ["onUpdate:modelValue"], zp = ["onUpdate:modelValue"], Gp = { key: 1 }, Kp = ["onClick"], Wp = ["onClick"], Zp = ["onClick"], Xp = {
  key: 0,
  class: "pagination-controls"
}, Yp = ["disabled"], Qp = ["disabled"];
function Jp(t, e, s, r, i, a) {
  return d(), c("div", jp, [
    f("table", null, [
      f("thead", null, [
        f("tr", null, [
          (d(!0), c(I, null, L(t.columns, (n) => (d(), c("th", {
            key: n.key,
            style: ne({ width: n.width, textAlign: n.align })
          }, w(n.label), 5))), 128)),
          e[2] || (e[2] = f("th", null, "Actions", -1))
        ])
      ]),
      f("tbody", null, [
        (d(!0), c(I, null, L(t.paginatedRows, (n, o) => (d(), c("tr", {
          key: n.id,
          class: q({ editing: t.editingRow === o })
        }, [
          (d(!0), c(I, null, L(t.columns, (u) => (d(), c("td", {
            key: u.key
          }, [
            t.editingRow === o && u.editable ? (d(), c("div", Vp, [
              u.multiline ? R((d(), c("textarea", {
                key: 1,
                "onUpdate:modelValue": (p) => n[u.key] = p
              }, null, 8, zp)), [
                [H, n[u.key]]
              ]) : R((d(), c("input", {
                key: 0,
                type: "text",
                "onUpdate:modelValue": (p) => n[u.key] = p
              }, null, 8, Hp)), [
                [H, n[u.key]]
              ])
            ])) : (d(), c("div", Gp, w(n[u.key]), 1))
          ]))), 128)),
          f("td", null, [
            t.editingRow !== o ? (d(), c("button", {
              key: 0,
              onClick: (u) => t.toggleEditRow(o)
            }, "Edit", 8, Kp)) : P("", !0),
            t.editingRow === o ? (d(), c("button", {
              key: 1,
              onClick: (u) => t.saveRow(o)
            }, "Save", 8, Wp)) : P("", !0),
            f("button", {
              onClick: (u) => t.deleteRow(o)
            }, "Delete", 8, Zp)
          ])
        ], 2))), 128))
      ])
    ]),
    t.pagination ? (d(), c("div", Xp, [
      f("button", {
        onClick: e[0] || (e[0] = (n) => t.currentPage--),
        disabled: t.currentPage === 1
      }, "Previous", 8, Yp),
      f("button", {
        onClick: e[1] || (e[1] = (n) => t.currentPage++),
        disabled: t.currentPage * t.itemsPerPage >= t.editedRows.length
      }, "Next", 8, Qp)
    ])) : P("", !0)
  ]);
}
const FT = /* @__PURE__ */ A(Up, [["render", Jp], ["__scopeId", "data-v-f7a88ca4"]]), xp = C({
  name: "EmbeddedMediaIframe",
  props: {
    src: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(!1), e = m(!0);
    return {
      isFullscreen: t,
      isBuffering: e,
      toggleFullscreen: () => {
        t.value = !t.value;
      },
      handleLoad: () => {
        e.value = !1;
      }
    };
  }
}), eh = ["src", "aria-busy"];
function th(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["embedded-media-iframe", { fullscreen: t.isFullscreen }])
  }, [
    f("iframe", {
      ref: "iframe",
      src: t.src,
      frameborder: "0",
      allowfullscreen: "",
      "aria-busy": t.isBuffering,
      onLoad: e[0] || (e[0] = (...n) => t.handleLoad && t.handleLoad(...n))
    }, null, 40, eh),
    t.isFullscreen ? (d(), c("button", {
      key: 1,
      onClick: e[2] || (e[2] = (...n) => t.toggleFullscreen && t.toggleFullscreen(...n)),
      "aria-label": "Exit fullscreen",
      class: "fullscreen-btn"
    }, "⤡")) : (d(), c("button", {
      key: 0,
      onClick: e[1] || (e[1] = (...n) => t.toggleFullscreen && t.toggleFullscreen(...n)),
      "aria-label": "Enter fullscreen",
      class: "fullscreen-btn"
    }, "⤢"))
  ], 2);
}
const UT = /* @__PURE__ */ A(xp, [["render", th], ["__scopeId", "data-v-df79aece"]]), sh = C({
  name: "EmojiReactionPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    emojis: {
      type: Array,
      default: () => ["😀", "😐", "😢"]
    },
    initialSelection: {
      type: Number,
      default: null
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialSelection);
    return {
      selectedEmoji: e,
      selectEmoji: (r) => {
        t.isDisabled || (e.value = r);
      }
    };
  }
}), nh = {
  class: "emoji-reaction-poll",
  role: "radiogroup",
  "aria-labelledby": "poll-question"
}, rh = { id: "poll-question" }, ih = { class: "emojis" }, ah = ["aria-checked", "disabled", "onClick"];
function oh(t, e, s, r, i, a) {
  return d(), c("div", nh, [
    f("p", rh, w(t.question), 1),
    f("div", ih, [
      (d(!0), c(I, null, L(t.emojis, (n, o) => (d(), c("button", {
        key: o,
        "aria-checked": o === t.selectedEmoji,
        disabled: t.isDisabled,
        onClick: (u) => t.selectEmoji(o),
        class: q(["emoji", { selected: o === t.selectedEmoji }]),
        role: "radio"
      }, w(n), 11, ah))), 128))
    ])
  ]);
}
const jT = /* @__PURE__ */ A(sh, [["render", oh], ["__scopeId", "data-v-d06ec7ef"]]), lh = C({
  name: "EraserTool",
  setup() {
    const t = m(!1), e = m(10);
    return {
      isActive: t,
      eraserSize: e,
      toggleActive: () => {
        t.value = !t.value;
      }
    };
  }
}), uh = ["aria-pressed"], dh = {
  key: 0,
  class: "eraser-settings"
};
function ch(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["eraser-tool", { active: t.isActive }])
  }, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleActive && t.toggleActive(...n)),
      "aria-pressed": t.isActive,
      class: "eraser-button"
    }, "Eraser Tool", 8, uh),
    t.isActive ? (d(), c("div", dh, [
      e[2] || (e[2] = f("label", { for: "eraserSize" }, "Eraser Size", -1)),
      R(f("input", {
        id: "eraserSize",
        type: "range",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.eraserSize = n),
        min: "1",
        max: "50",
        "aria-valuemin": "1",
        "aria-valuemax": "50",
        "aria-valuenow": "eraserSize"
      }, null, 512), [
        [H, t.eraserSize]
      ])
    ])) : P("", !0)
  ], 2);
}
const VT = /* @__PURE__ */ A(lh, [["render", ch], ["__scopeId", "data-v-022c39bc"]]), fh = C({
  name: "EventDetailsDialog",
  props: {
    event: {
      type: Object,
      required: !0
    },
    isOpen: {
      type: Boolean,
      default: !1
    },
    isLoading: {
      type: Boolean,
      default: !1
    },
    error: {
      type: String,
      default: ""
    }
  },
  setup() {
    return {
      editEvent: () => {
      },
      deleteEvent: () => {
      },
      duplicateEvent: () => {
      },
      closeDialog: () => {
      }
    };
  }
}), ph = {
  key: 0,
  class: "dialog",
  role: "dialog",
  "aria-labelledby": "dialog-title",
  "aria-describedby": "dialog-description"
}, hh = { class: "dialog-content" }, gh = { id: "dialog-title" }, mh = { id: "dialog-description" }, vh = { class: "dialog-actions" }, bh = ["disabled"], yh = ["disabled"], $h = ["disabled"], kh = {
  key: 0,
  class: "loading"
}, wh = {
  key: 1,
  class: "error"
};
function Ch(t, e, s, r, i, a) {
  return d(), uo(co, { name: "fade" }, {
    default: Ri(() => [
      t.isOpen ? (d(), c("div", ph, [
        f("div", hh, [
          f("h2", gh, w(t.event.title), 1),
          f("p", mh, w(t.event.description), 1),
          f("ul", null, [
            f("li", null, [
              e[4] || (e[4] = f("strong", null, "Participants:", -1)),
              Fe(" " + w(t.event.participants.join(", ")), 1)
            ]),
            f("li", null, [
              e[5] || (e[5] = f("strong", null, "Location:", -1)),
              Fe(" " + w(t.event.location), 1)
            ]),
            f("li", null, [
              e[6] || (e[6] = f("strong", null, "Time:", -1)),
              Fe(" " + w(t.event.time), 1)
            ])
          ]),
          f("div", vh, [
            f("button", {
              onClick: e[0] || (e[0] = (...n) => t.editEvent && t.editEvent(...n)),
              disabled: t.isLoading
            }, "Edit", 8, bh),
            f("button", {
              onClick: e[1] || (e[1] = (...n) => t.deleteEvent && t.deleteEvent(...n)),
              disabled: t.isLoading
            }, "Delete", 8, yh),
            f("button", {
              onClick: e[2] || (e[2] = (...n) => t.duplicateEvent && t.duplicateEvent(...n)),
              disabled: t.isLoading
            }, "Duplicate", 8, $h)
          ]),
          f("button", {
            class: "close-button",
            onClick: e[3] || (e[3] = (...n) => t.closeDialog && t.closeDialog(...n)),
            "aria-label": "Close dialog"
          }, "×")
        ]),
        t.isLoading ? (d(), c("div", kh, "Loading...")) : P("", !0),
        t.error ? (d(), c("div", wh, w(t.error), 1)) : P("", !0)
      ])) : P("", !0)
    ]),
    _: 1
  });
}
const HT = /* @__PURE__ */ A(fh, [["render", Ch], ["__scopeId", "data-v-8ed5c1ba"]]), Ah = C({
  name: "EventFilterBar",
  setup() {
    const t = m(["Conference", "Meetup", "Workshop"]), e = m({
      category: "",
      startDate: "",
      endDate: "",
      location: "",
      participants: 1
    }), s = W(() => Object.entries(e.value).filter(([, a]) => a).map(([a, n]) => `${a}: ${n}`).join(", "));
    return {
      categories: t,
      filters: e,
      activeFilters: s,
      applyFilters: () => {
        console.log("Filters applied:", e.value);
      },
      clearFilters: () => {
        e.value = {
          category: "",
          startDate: "",
          endDate: "",
          location: "",
          participants: 1
        };
      }
    };
  }
}), Eh = {
  class: "event-filter-bar",
  role: "toolbar",
  "aria-label": "Event Filter Bar"
}, Sh = { class: "filter-group" }, Th = ["value"], _h = { class: "filter-group" }, Nh = { class: "filter-group" }, Ih = { class: "filter-group" }, Lh = { class: "filter-buttons" }, qh = {
  key: 0,
  class: "active-filters"
};
function Oh(t, e, s, r, i, a) {
  return d(), c("div", Eh, [
    f("form", {
      onSubmit: e[6] || (e[6] = de((...n) => t.applyFilters && t.applyFilters(...n), ["prevent"]))
    }, [
      f("div", Sh, [
        e[8] || (e[8] = f("label", { for: "category" }, "Category", -1)),
        R(f("select", {
          id: "category",
          "onUpdate:modelValue": e[0] || (e[0] = (n) => t.filters.category = n)
        }, [
          e[7] || (e[7] = f("option", { value: "" }, "All Categories", -1)),
          (d(!0), c(I, null, L(t.categories, (n) => (d(), c("option", {
            key: n,
            value: n
          }, w(n), 9, Th))), 128))
        ], 512), [
          [ye, t.filters.category]
        ])
      ]),
      f("div", _h, [
        e[9] || (e[9] = f("label", { for: "date-range" }, "Date Range", -1)),
        R(f("input", {
          type: "date",
          id: "start-date",
          "onUpdate:modelValue": e[1] || (e[1] = (n) => t.filters.startDate = n)
        }, null, 512), [
          [H, t.filters.startDate]
        ]),
        R(f("input", {
          type: "date",
          id: "end-date",
          "onUpdate:modelValue": e[2] || (e[2] = (n) => t.filters.endDate = n)
        }, null, 512), [
          [H, t.filters.endDate]
        ])
      ]),
      f("div", Nh, [
        e[10] || (e[10] = f("label", { for: "location" }, "Location", -1)),
        R(f("input", {
          type: "text",
          id: "location",
          "onUpdate:modelValue": e[3] || (e[3] = (n) => t.filters.location = n),
          placeholder: "Enter location"
        }, null, 512), [
          [H, t.filters.location]
        ])
      ]),
      f("div", Ih, [
        e[11] || (e[11] = f("label", { for: "participants" }, "Participants", -1)),
        R(f("input", {
          type: "number",
          id: "participants",
          "onUpdate:modelValue": e[4] || (e[4] = (n) => t.filters.participants = n),
          min: "1"
        }, null, 512), [
          [H, t.filters.participants]
        ])
      ]),
      f("div", Lh, [
        e[12] || (e[12] = f("button", { type: "submit" }, "Apply Filters", -1)),
        f("button", {
          type: "button",
          onClick: e[5] || (e[5] = (...n) => t.clearFilters && t.clearFilters(...n))
        }, "Clear Filters")
      ])
    ], 32),
    t.activeFilters ? (d(), c("div", qh, " Active Filters: " + w(t.activeFilters), 1)) : P("", !0)
  ]);
}
const zT = /* @__PURE__ */ A(Ah, [["render", Oh], ["__scopeId", "data-v-88e66fe9"]]), Ph = C({
  name: "EventReminderSystem",
  props: {
    feedbackMessage: {
      type: String,
      default: ""
    }
  },
  setup(t) {
    const e = m([
      { id: "1", title: "Team Meeting" },
      { id: "2", title: "Project Deadline" },
      { id: "3", title: "Client Call" }
    ]), s = m({
      event: "",
      time: "",
      method: ""
    }), r = m(t.feedbackMessage), i = () => {
      r.value = `Reminder set for "${s.value.event}" via ${s.value.method}.`, n();
    }, a = () => {
      r.value = `Reminder for "${s.value.event}" canceled.`, n();
    }, n = () => {
      s.value = {
        event: "",
        time: "",
        method: ""
      };
    };
    return {
      events: e,
      form: s,
      localFeedbackMessage: r,
      setReminder: i,
      cancelReminder: a
    };
  }
}), Dh = {
  class: "event-reminder-system",
  role: "region",
  "aria-label": "Event Reminder System"
}, Rh = { class: "form-group" }, Bh = ["value"], Mh = { class: "form-group" }, Fh = { class: "form-group" }, Uh = { class: "reminder-buttons" }, jh = {
  key: 0,
  class: "feedback"
};
function Vh(t, e, s, r, i, a) {
  return d(), c("div", Dh, [
    f("form", {
      onSubmit: e[4] || (e[4] = de((...n) => t.setReminder && t.setReminder(...n), ["prevent"]))
    }, [
      f("div", Rh, [
        e[5] || (e[5] = f("label", { for: "event" }, "Event", -1)),
        R(f("select", {
          id: "event",
          "onUpdate:modelValue": e[0] || (e[0] = (n) => t.form.event = n),
          required: ""
        }, [
          (d(!0), c(I, null, L(t.events, (n) => (d(), c("option", {
            key: n.id,
            value: n.id
          }, w(n.title), 9, Bh))), 128))
        ], 512), [
          [ye, t.form.event]
        ])
      ]),
      f("div", Mh, [
        e[7] || (e[7] = f("label", { for: "time" }, "Reminder Time", -1)),
        R(f("select", {
          id: "time",
          "onUpdate:modelValue": e[1] || (e[1] = (n) => t.form.time = n),
          required: ""
        }, [...e[6] || (e[6] = [
          f("option", { value: "1 hour" }, "1 hour before", -1),
          f("option", { value: "1 day" }, "1 day before", -1),
          f("option", { value: "1 week" }, "1 week before", -1)
        ])], 512), [
          [ye, t.form.time]
        ])
      ]),
      f("div", Fh, [
        e[9] || (e[9] = f("label", { for: "method" }, "Notification Method", -1)),
        R(f("select", {
          id: "method",
          "onUpdate:modelValue": e[2] || (e[2] = (n) => t.form.method = n),
          required: ""
        }, [...e[8] || (e[8] = [
          f("option", { value: "email" }, "Email", -1),
          f("option", { value: "sms" }, "SMS", -1),
          f("option", { value: "push" }, "Push Notification", -1)
        ])], 512), [
          [ye, t.form.method]
        ])
      ]),
      f("div", Uh, [
        e[10] || (e[10] = f("button", { type: "submit" }, "Set Reminder", -1)),
        f("button", {
          type: "button",
          onClick: e[3] || (e[3] = (...n) => t.cancelReminder && t.cancelReminder(...n))
        }, "Cancel Reminder")
      ])
    ], 32),
    t.localFeedbackMessage ? (d(), c("div", jh, w(t.localFeedbackMessage), 1)) : P("", !0)
  ]);
}
const GT = /* @__PURE__ */ A(Ph, [["render", Vh], ["__scopeId", "data-v-abb09c51"]]), Hh = C({
  name: "ExpandableList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m(null), e = m(null);
    return { selectedItem: t, hoveredItem: e, toggleItem: (i) => {
      t.value = t.value === i ? null : i;
    }, hoverItem: (i) => {
      e.value = i;
    } };
  }
}), zh = {
  class: "expandable-list",
  role: "list",
  "aria-label": "Expandable list"
}, Gh = ["aria-expanded", "onClick", "onMouseover"], Kh = { class: "item-header" }, Wh = {
  key: 0,
  class: "item-content"
};
function Zh(t, e, s, r, i, a) {
  return d(), c("div", zh, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("div", {
      key: o,
      class: "list-item",
      "aria-expanded": t.selectedItem === o,
      onClick: (u) => t.toggleItem(o),
      onMouseover: (u) => t.hoverItem(o),
      onMouseleave: e[0] || (e[0] = (u) => t.hoverItem(null))
    }, [
      f("div", Kh, w(n.title), 1),
      t.selectedItem === o ? (d(), c("div", Wh, w(n.content), 1)) : P("", !0)
    ], 40, Gh))), 128))
  ]);
}
const KT = /* @__PURE__ */ A(Hh, [["render", Zh], ["__scopeId", "data-v-2bce1792"]]), Xh = C({
  name: "FavoritesList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    const e = m(null), s = m(null);
    return { selectedItem: e, hoveredItem: s, selectItem: (n) => {
      e.value = e.value === n ? null : n;
    }, hoverItem: (n) => {
      s.value = n;
    }, toggleStar: (n) => {
      t.items[n].starred = !t.items[n].starred;
    } };
  }
}), Yh = {
  class: "favorites-list",
  role: "list",
  "aria-label": "Favorites list"
}, Qh = ["onClick", "onMouseover"], Jh = { class: "item-header" }, xh = ["aria-pressed", "onClick"];
function eg(t, e, s, r, i, a) {
  return d(), c("div", Yh, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("div", {
      key: o,
      class: q(["list-item", { selected: t.selectedItem === o, hover: t.hoveredItem === o }]),
      onClick: (u) => t.selectItem(o),
      onMouseover: (u) => t.hoverItem(o),
      onMouseleave: e[0] || (e[0] = (u) => t.hoverItem(null))
    }, [
      f("div", Jh, [
        Fe(w(n.title) + " ", 1),
        f("button", {
          class: "star-button",
          "aria-pressed": n.starred,
          onClick: de((u) => t.toggleStar(o), ["stop"])
        }, w(n.starred ? "★" : "☆"), 9, xh)
      ])
    ], 42, Qh))), 128))
  ]);
}
const WT = /* @__PURE__ */ A(Xh, [["render", eg], ["__scopeId", "data-v-62a6fd5a"]]), tg = C({
  name: "FieldEditableDataTable",
  setup() {
    const t = li([
      { id: "1", name: "John Doe", description: "A short note" },
      { id: "2", name: "Jane Smith", description: "Another note" }
    ]), e = m(null), s = li({}), r = m(null);
    return {
      data: t,
      editingField: e,
      fieldValues: s,
      error: r,
      editField: (o, u) => {
        var p;
        e.value = { rowId: o, field: u }, s[u] = ((p = t.find((g) => g.id === o)) == null ? void 0 : p[u]) || "";
      },
      saveField: () => {
        if (!e.value) return;
        const { rowId: o, field: u } = e.value, p = t.find((g) => g.id === o);
        if (!p) {
          r.value = "Row not found";
          return;
        }
        p[u] = s[u], r.value = null, e.value = null;
      },
      discardChanges: () => {
        e.value = null, r.value = null;
      }
    };
  }
}), sg = {
  class: "field-editable-data-table",
  role: "table"
}, ng = ["onUpdate:modelValue"], rg = ["onUpdate:modelValue"], ig = ["onClick"], ag = {
  key: 0,
  class: "error-message",
  "aria-live": "assertive"
};
function og(t, e, s, r, i, a) {
  return d(), c("div", sg, [
    (d(!0), c(I, null, L(t.data, (n) => (d(), c("div", {
      role: "row",
      key: n.id,
      class: "table-row"
    }, [
      (d(!0), c(I, null, L(n, (o, u) => (d(), c("div", {
        role: "cell",
        class: "table-cell",
        key: u
      }, [
        t.editingField && t.editingField.rowId === n.id && t.editingField.field === u ? (d(), c(I, { key: 0 }, [
          u === "description" ? R((d(), c("textarea", {
            key: 0,
            "onUpdate:modelValue": (p) => t.fieldValues[u] = p,
            "aria-label": "Edit description"
          }, null, 8, ng)), [
            [H, t.fieldValues[u]]
          ]) : R((d(), c("input", {
            key: 1,
            type: "text",
            "onUpdate:modelValue": (p) => t.fieldValues[u] = p,
            "aria-label": "Edit field"
          }, null, 8, rg)), [
            [H, t.fieldValues[u]]
          ]),
          f("button", {
            onClick: e[0] || (e[0] = (...p) => t.saveField && t.saveField(...p))
          }, "Save"),
          f("button", {
            onClick: e[1] || (e[1] = (...p) => t.discardChanges && t.discardChanges(...p))
          }, "Cancel")
        ], 64)) : (d(), c("span", {
          key: 1,
          onClick: (p) => t.editField(n.id, u.toString()),
          class: "editable-field"
        }, w(o), 9, ig))
      ]))), 128))
    ]))), 128)),
    t.error ? (d(), c("div", ag, w(t.error), 1)) : P("", !0)
  ]);
}
const ZT = /* @__PURE__ */ A(tg, [["render", og], ["__scopeId", "data-v-5d7b0258"]]), lg = C({
  name: "FileInputWithPreview",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    const t = m(null), e = m(null);
    return { preview: t, error: e, handleFileUpload: (r) => {
      const i = r.target, a = i.files ? i.files[0] : null;
      if (a) {
        const n = new FileReader();
        n.onload = () => {
          t.value = n.result, e.value = null;
        }, n.onerror = () => {
          e.value = "Error loading file.", t.value = null;
        }, n.readAsDataURL(a);
      }
    } };
  }
}), ug = { class: "file-input-container" }, dg = ["disabled", "aria-disabled"], cg = {
  key: 0,
  class: "preview-container"
}, fg = ["src"], pg = {
  key: 1,
  class: "error-message",
  role: "alert"
};
function hg(t, e, s, r, i, a) {
  return d(), c("div", ug, [
    f("input", {
      type: "file",
      disabled: t.disabled,
      onChange: e[0] || (e[0] = (...n) => t.handleFileUpload && t.handleFileUpload(...n)),
      "aria-label": "Upload File",
      "aria-disabled": t.disabled
    }, null, 40, dg),
    t.preview ? (d(), c("div", cg, [
      f("img", {
        src: t.preview,
        alt: "File Preview",
        class: "preview-image"
      }, null, 8, fg)
    ])) : P("", !0),
    t.error ? (d(), c("div", pg, w(t.error), 1)) : P("", !0)
  ]);
}
const XT = /* @__PURE__ */ A(lg, [["render", hg], ["__scopeId", "data-v-a42dea44"]]), gg = C({
  name: "FileUpload",
  props: {
    multiple: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    const t = m(!1), e = m(null);
    return { isDragOver: t, progress: e, handleFileSelect: (n) => {
      n.target.files;
    }, handleDragOver: () => {
      t.value = !0;
    }, handleDragLeave: () => {
      t.value = !1;
    }, handleDrop: (n) => {
      var o;
      t.value = !1, (o = n.dataTransfer) == null || o.files;
    } };
  }
}), mg = ["multiple"], vg = ["aria-valuenow"];
function bg(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["file-upload-container", { "drag-over": t.isDragOver }]),
    onDragover: e[1] || (e[1] = de((...n) => t.handleDragOver && t.handleDragOver(...n), ["prevent"])),
    onDragleave: e[2] || (e[2] = de((...n) => t.handleDragLeave && t.handleDragLeave(...n), ["prevent"])),
    onDrop: e[3] || (e[3] = de((...n) => t.handleDrop && t.handleDrop(...n), ["prevent"]))
  }, [
    f("input", {
      type: "file",
      multiple: t.multiple,
      onChange: e[0] || (e[0] = (...n) => t.handleFileSelect && t.handleFileSelect(...n)),
      "aria-label": "Upload File(s)"
    }, null, 40, mg),
    t.progress ? (d(), c("div", {
      key: 0,
      class: "progress-bar",
      role: "progressbar",
      "aria-valuenow": t.progress,
      "aria-valuemin": "0",
      "aria-valuemax": "100"
    }, [
      f("div", {
        class: "progress",
        style: ne({ width: t.progress + "%" })
      }, null, 4)
    ], 8, vg)) : P("", !0)
  ], 34);
}
const YT = /* @__PURE__ */ A(gg, [["render", bg], ["__scopeId", "data-v-e710dbb6"]]), yg = C({
  name: "FillTool",
  setup() {
    const t = m(!1), e = m(!1), s = m(50);
    return {
      isActive: t,
      isDisabled: e,
      tolerance: s,
      toggleActive: () => {
        e.value || (t.value = !t.value);
      }
    };
  }
}), $g = { class: "fill-tool" }, kg = ["disabled"], wg = {
  key: 0,
  class: "fill-options"
};
function Cg(t, e, s, r, i, a) {
  return d(), c("div", $g, [
    f("button", {
      disabled: t.isDisabled,
      onClick: e[0] || (e[0] = (...n) => t.toggleActive && t.toggleActive(...n)),
      class: q({ active: t.isActive }),
      "aria-label": "Fill Tool"
    }, " Fill ", 10, kg),
    t.isActive ? (d(), c("div", wg, [
      e[2] || (e[2] = f("label", { for: "tolerance" }, "Tolerance:", -1)),
      R(f("input", {
        id: "tolerance",
        type: "range",
        min: "0",
        max: "100",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.tolerance = n)
      }, null, 512), [
        [H, t.tolerance]
      ])
    ])) : P("", !0)
  ]);
}
const QT = /* @__PURE__ */ A(yg, [["render", Cg], ["__scopeId", "data-v-c9034f98"]]), Ag = C({
  name: "FilterableList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    const e = m(""), s = W(
      () => t.items.filter(
        (i) => i.toLowerCase().includes(e.value.toLowerCase())
      )
    );
    return { filterText: e, filteredItems: s, clearFilter: () => {
      e.value = "";
    } };
  }
}), Eg = { class: "filterable-list" }, Sg = {
  role: "list",
  "aria-label": "Filtered list"
}, Tg = {
  key: 0,
  class: "no-results"
};
function _g(t, e, s, r, i, a) {
  return d(), c("div", Eg, [
    R(f("input", {
      type: "text",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.filterText = n),
      placeholder: "Filter items...",
      "aria-label": "Filter items",
      class: "filter-input"
    }, null, 512), [
      [H, t.filterText]
    ]),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.clearFilter && t.clearFilter(...n)),
      class: "clear-button"
    }, "Clear Filter"),
    f("ul", Sg, [
      (d(!0), c(I, null, L(t.filteredItems, (n, o) => (d(), c("li", {
        key: o,
        class: "list-item"
      }, w(n), 1))), 128))
    ]),
    t.filteredItems.length === 0 ? (d(), c("p", Tg, "No results found")) : P("", !0)
  ]);
}
const JT = /* @__PURE__ */ A(Ag, [["render", _g], ["__scopeId", "data-v-d92ce0dc"]]), Ng = C({
  name: "FlipCard",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(!1);
    return {
      flipped: e,
      toggleFlip: () => {
        t.disabled || (e.value = !e.value);
      }
    };
  }
}), Ig = ["aria-disabled"], Lg = {
  class: "flip-card-front",
  role: "region",
  "aria-label": "Front Content"
}, qg = {
  class: "flip-card-back",
  role: "region",
  "aria-label": "Back Content"
};
function Og(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["flip-card", { flipped: t.flipped, disabled: t.disabled }]),
    onClick: e[0] || (e[0] = (...n) => t.toggleFlip && t.toggleFlip(...n)),
    "aria-disabled": t.disabled
  }, [
    f("div", {
      class: "flip-card-inner",
      style: ne({ transform: t.flipped ? "rotateY(180deg)" : "none" })
    }, [
      f("div", Lg, [
        ie(t.$slots, "front", {}, void 0, !0)
      ]),
      f("div", qg, [
        ie(t.$slots, "back", {}, void 0, !0)
      ])
    ], 4)
  ], 10, Ig);
}
const xT = /* @__PURE__ */ A(Ng, [["render", Og], ["__scopeId", "data-v-fd008512"]]), Pg = C({
  name: "FloatingActionButton",
  props: {
    isExpanded: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.isExpanded);
    return { localIsExpanded: e, toggleExpand: () => {
      e.value = !e.value;
    } };
  }
}), Dg = ["aria-expanded"], Rg = {
  key: 0,
  "aria-hidden": "true"
}, Bg = {
  key: 1,
  "aria-hidden": "true"
}, Mg = { class: "sr-only" };
function Fg(t, e, s, r, i, a) {
  return d(), c("button", {
    class: "floating-action-button",
    onClick: e[0] || (e[0] = (...n) => t.toggleExpand && t.toggleExpand(...n)),
    "aria-expanded": t.localIsExpanded
  }, [
    t.localIsExpanded ? (d(), c("span", Rg, "✖")) : (d(), c("span", Bg, "+")),
    f("span", Mg, w(t.localIsExpanded ? "Close menu" : "Open menu"), 1)
  ], 8, Dg);
}
const e4 = /* @__PURE__ */ A(Pg, [["render", Fg], ["__scopeId", "data-v-ec8edb50"]]), Ug = C({
  name: "FoldButton",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  }
}), jg = ["disabled"];
function Vg(t, e, s, r, i, a) {
  return d(), c("button", {
    class: "fold-button",
    disabled: t.disabled,
    "aria-label": "Fold Hand"
  }, " Fold ", 8, jg);
}
const t4 = /* @__PURE__ */ A(Ug, [["render", Vg], ["__scopeId", "data-v-3abbd310"]]), Hg = C({
  name: "GroupedList",
  props: {
    groups: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m([]), e = m(null), s = m(null);
    return { expandedGroups: t, selectedItem: e, hoveredItem: s, toggleGroup: (a) => {
      t.value[a] = !t.value[a];
    }, selectItem: (a) => {
      e.value = a;
    } };
  }
}), zg = { class: "grouped-list" }, Gg = ["onClick"], Kg = {
  class: "group-items",
  role: "list",
  "aria-label": "Group items"
}, Wg = ["onClick", "onMouseover", "aria-selected"];
function Zg(t, e, s, r, i, a) {
  return d(), c("div", zg, [
    (d(!0), c(I, null, L(t.groups, (n, o) => (d(), c("div", {
      key: o,
      class: "group"
    }, [
      f("div", {
        class: "group-header",
        onClick: (u) => t.toggleGroup(o)
      }, w(n.name), 9, Gg),
      R(f("ul", Kg, [
        (d(!0), c(I, null, L(n.items, (u, p) => (d(), c("li", {
          key: p,
          class: q(["list-item", { selected: t.selectedItem === u }]),
          onClick: (g) => t.selectItem(u),
          onMouseover: (g) => t.hoveredItem = u,
          onMouseleave: e[0] || (e[0] = (g) => t.hoveredItem = null),
          "aria-selected": t.selectedItem === u,
          role: "option"
        }, w(u), 43, Wg))), 128))
      ], 512), [
        [lo, t.expandedGroups[o]]
      ])
    ]))), 128))
  ]);
}
const s4 = /* @__PURE__ */ A(Hg, [["render", Zg], ["__scopeId", "data-v-024aa25b"]]), Xg = C({
  name: "HandOfCards",
  props: {
    cards: {
      type: Array,
      required: !0
    },
    maxCards: {
      type: Number,
      default: 5
    }
  },
  setup(t) {
    const e = m([...t.cards]), s = m([]), r = (n) => {
      s.value.includes(n) ? s.value = s.value.filter((o) => o !== n) : s.value.length < t.maxCards && s.value.push(n);
    }, i = W(() => e.value.length >= t.maxCards), a = W(() => s.value.length >= t.maxCards);
    return {
      hand: e,
      selectedCards: s,
      isFull: i,
      maxLimitReached: a,
      toggleSelect: r
    };
  }
}), Yg = ["onClick"], Qg = {
  key: 0,
  class: "limit-notification"
};
function Jg(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["hand", { full: t.isFull, maxLimit: t.maxLimitReached }])
  }, [
    (d(!0), c(I, null, L(t.hand, (n) => (d(), c("div", {
      key: n.id,
      class: q(["card", { selected: t.selectedCards.includes(n.id) }]),
      onClick: (o) => t.toggleSelect(n.id)
    }, [
      ie(t.$slots, "card", { card: n }, void 0, !0)
    ], 10, Yg))), 128)),
    t.maxLimitReached ? (d(), c("div", Qg, "Max card limit reached")) : P("", !0)
  ], 2);
}
const n4 = /* @__PURE__ */ A(Xg, [["render", Jg], ["__scopeId", "data-v-68df639c"]]), xg = C({
  name: "IconButton",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(!1), s = m(!1), r = W(() => t.disabled ? "disabled" : s.value ? "active" : e.value ? "hover" : "");
    return {
      isHover: e,
      isActive: s,
      buttonState: r
    };
  }
}), em = ["aria-disabled", "disabled"];
function tm(t, e, s, r, i, a) {
  return d(), c("button", {
    class: q(["icon-button", t.buttonState, { disabled: t.disabled }]),
    "aria-disabled": t.disabled,
    disabled: t.disabled,
    onMouseover: e[0] || (e[0] = (n) => t.isHover = !0),
    onMouseleave: e[1] || (e[1] = (n) => t.isHover = !1),
    onMousedown: e[2] || (e[2] = (n) => t.isActive = !0),
    onMouseup: e[3] || (e[3] = (n) => t.isActive = !1)
  }, [
    ie(t.$slots, "default", {}, void 0, !0)
  ], 42, em);
}
const r4 = /* @__PURE__ */ A(xg, [["render", tm], ["__scopeId", "data-v-1fd9d51b"]]), sm = C({
  name: "ImageChoicePoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    options: {
      type: Array,
      required: !0
    },
    initialValue: {
      type: Number,
      default: null
    },
    resultsVisible: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialValue);
    return {
      selectedOption: e,
      selectOption: (r) => {
        t.disabled || (e.value = r);
      }
    };
  }
}), nm = {
  class: "image-choice-poll",
  role: "group",
  "aria-labelledby": "image-choice-poll-label"
}, rm = {
  id: "image-choice-poll-label",
  class: "poll-label"
}, im = { class: "options" }, am = ["onClick", "disabled", "aria-pressed"], om = ["src", "alt"], lm = {
  key: 0,
  class: "result-display"
};
function um(t, e, s, r, i, a) {
  return d(), c("div", nm, [
    f("div", rm, w(t.question), 1),
    f("div", im, [
      (d(!0), c(I, null, L(t.options, (n, o) => (d(), c("button", {
        key: o,
        class: q(["option", { selected: t.selectedOption === o, disabled: t.disabled }]),
        onClick: (u) => t.selectOption(o),
        disabled: t.disabled,
        "aria-pressed": t.selectedOption === o,
        "aria-label": "Option"
      }, [
        f("img", {
          src: n.image,
          alt: n.alt,
          class: "option-image"
        }, null, 8, om)
      ], 10, am))), 128))
    ]),
    t.resultsVisible && t.selectedOption !== null ? (d(), c("div", lm, " Selected: " + w(t.options[t.selectedOption].alt), 1)) : P("", !0)
  ]);
}
const i4 = /* @__PURE__ */ A(sm, [["render", um], ["__scopeId", "data-v-ec76f45f"]]), dm = C({
  name: "ImageSlider",
  props: {
    images: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    const e = m(0), s = m(!1);
    return {
      activeIndex: e,
      isHovering: s,
      setHover: (n) => {
        s.value = n;
      },
      prevImage: () => {
        e.value = (e.value - 1 + t.images.length) % t.images.length;
      },
      nextImage: () => {
        e.value = (e.value + 1) % t.images.length;
      }
    };
  }
}), cm = { class: "slider-images" };
function fm(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "image-slider",
    onMouseenter: e[2] || (e[2] = (n) => t.setHover(!0)),
    onMouseleave: e[3] || (e[3] = (n) => t.setHover(!1))
  }, [
    f("div", cm, [
      (d(!0), c(I, null, L(t.images, (n, o) => (d(), c("div", {
        key: o,
        class: q(["slider-image", { active: o === t.activeIndex, hover: t.isHovering }]),
        style: ne({ backgroundImage: "url(" + n + ")" })
      }, null, 6))), 128))
    ]),
    f("button", {
      class: "prev-btn",
      onClick: e[0] || (e[0] = (...n) => t.prevImage && t.prevImage(...n)),
      "aria-label": "Previous image"
    }, "‹"),
    f("button", {
      class: "next-btn",
      onClick: e[1] || (e[1] = (...n) => t.nextImage && t.nextImage(...n)),
      "aria-label": "Next image"
    }, "›")
  ], 32);
}
const a4 = /* @__PURE__ */ A(dm, [["render", fm], ["__scopeId", "data-v-a1b0374f"]]), pm = C({
  name: "InteractiveMediaMap",
  props: {
    mapSrc: {
      type: String,
      required: !0
    },
    markers: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    const t = m(null), e = m(!0);
    return {
      selectedMarker: t,
      loading: e,
      selectMarker: (n) => {
        t.value = n;
      },
      deselectMarker: () => {
        t.value = null;
      },
      zoomIn: () => {
      },
      zoomOut: () => {
      }
    };
  }
}), hm = {
  class: "interactive-media-map",
  role: "application",
  "aria-label": "Interactive Media Map"
}, gm = { class: "map-container" }, mm = ["src"], vm = ["onClick", "aria-label"], bm = {
  key: 0,
  class: "marker-info"
}, ym = {
  key: 1,
  class: "loading"
};
function $m(t, e, s, r, i, a) {
  return d(), c("div", hm, [
    f("div", gm, [
      f("img", {
        src: t.mapSrc,
        alt: "Map",
        onLoad: e[0] || (e[0] = (n) => t.loading = !1)
      }, null, 40, mm),
      (d(!0), c(I, null, L(t.markers, (n, o) => (d(), c("div", {
        key: o,
        class: "map-marker",
        style: ne({ top: n.y + "%", left: n.x + "%" }),
        onClick: (u) => t.selectMarker(o),
        "aria-label": "Marker " + (o + 1),
        role: "button"
      }, null, 12, vm))), 128))
    ]),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.zoomIn && t.zoomIn(...n)),
      "aria-label": "Zoom in",
      class: "zoom-btn"
    }, "+"),
    f("button", {
      onClick: e[2] || (e[2] = (...n) => t.zoomOut && t.zoomOut(...n)),
      "aria-label": "Zoom out",
      class: "zoom-btn"
    }, "-"),
    t.selectedMarker !== null ? (d(), c("div", bm, [
      f("p", null, w(t.markers[t.selectedMarker].info), 1),
      f("button", {
        onClick: e[3] || (e[3] = (...n) => t.deselectMarker && t.deselectMarker(...n)),
        "aria-label": "Close marker info"
      }, "Close")
    ])) : P("", !0),
    t.loading ? (d(), c("div", ym, "Loading...")) : P("", !0)
  ]);
}
const o4 = /* @__PURE__ */ A(pm, [["render", $m], ["__scopeId", "data-v-45db09ed"]]), km = C({
  name: "InteractivePollResults",
  props: {
    title: {
      type: String,
      required: !0
    },
    options: {
      type: Array,
      required: !0
    },
    state: {
      type: String,
      required: !0
    }
  }
}), wm = {
  class: "poll-results",
  role: "region",
  "aria-live": "polite"
}, Cm = ["aria-label"], Am = { class: "option-text" }, Em = { class: "percentage" }, Sm = {
  key: 0,
  class: "poll-status"
}, Tm = {
  key: 1,
  class: "poll-status"
};
function _m(t, e, s, r, i, a) {
  return d(), c("div", wm, [
    f("h2", null, w(t.title), 1),
    f("ul", null, [
      (d(!0), c(I, null, L(t.options, (n) => (d(), c("li", {
        key: n.id,
        "aria-label": `${n.text}: ${n.percentage}%`
      }, [
        f("span", Am, w(n.text), 1),
        f("div", {
          class: "progress-bar",
          style: ne({ "--progress": `${n.percentage}%` })
        }, [
          f("span", Em, w(n.percentage) + "%", 1)
        ], 4)
      ], 8, Cm))), 128))
    ]),
    t.state === "completed" ? (d(), c("div", Sm, "Poll Completed")) : P("", !0),
    t.state === "closed" ? (d(), c("div", Tm, "Poll Closed")) : P("", !0)
  ]);
}
const l4 = /* @__PURE__ */ A(km, [["render", _m], ["__scopeId", "data-v-4fad34d2"]]), Nm = C({
  name: "LayerPanel",
  setup() {
    const t = m([
      { id: 1, name: "Layer 1", opacity: 1, visible: !0 }
    ]), e = m(0);
    return {
      layers: t,
      activeLayerIndex: e,
      addLayer: () => {
        t.value.push({
          id: Date.now(),
          name: `Layer ${t.value.length + 1}`,
          opacity: 1,
          visible: !0
        });
      },
      removeLayer: (n) => {
        t.value.length > 1 && (t.value.splice(n, 1), e.value >= t.value.length && (e.value = t.value.length - 1));
      },
      renameLayer: (n, o) => {
        t.value[n].name = o;
      },
      toggleVisibility: (n) => {
        t.value[n].visible = !t.value[n].visible;
      }
    };
  }
}), Im = { class: "layer-panel" }, Lm = ["onUpdate:modelValue", "onBlur"], qm = ["onUpdate:modelValue"], Om = ["onClick"], Pm = ["onClick"];
function Dm(t, e, s, r, i, a) {
  return d(), c("div", Im, [
    e[1] || (e[1] = f("h2", null, "Layers", -1)),
    f("ul", null, [
      (d(!0), c(I, null, L(t.layers, (n, o) => (d(), c("li", {
        key: n.id,
        class: q({ active: o === t.activeLayerIndex })
      }, [
        R(f("input", {
          type: "text",
          "onUpdate:modelValue": (u) => n.name = u,
          onBlur: (u) => t.renameLayer(o, n.name),
          "aria-label": "Layer Name"
        }, null, 40, Lm), [
          [H, n.name]
        ]),
        R(f("input", {
          type: "range",
          "onUpdate:modelValue": (u) => n.opacity = u,
          min: "0",
          max: "1",
          step: "0.01",
          "aria-label": "Layer Opacity"
        }, null, 8, qm), [
          [H, n.opacity]
        ]),
        f("button", {
          onClick: (u) => t.toggleVisibility(o),
          "aria-label": "Toggle Visibility"
        }, w(n.visible ? "Hide" : "Show"), 9, Om),
        f("button", {
          onClick: (u) => t.removeLayer(o),
          "aria-label": "Remove Layer"
        }, "Remove", 8, Pm)
      ], 2))), 128))
    ]),
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.addLayer && t.addLayer(...n)),
      "aria-label": "Add Layer"
    }, "Add Layer")
  ]);
}
const u4 = /* @__PURE__ */ A(Nm, [["render", Dm], ["__scopeId", "data-v-54d3b63a"]]), Rm = C({
  name: "LiveResultsPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    options: {
      type: Array,
      required: !0
    },
    initialValue: {
      type: Number,
      default: null
    },
    liveResultsVisible: {
      type: Boolean,
      default: !1
    },
    closed: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialValue), s = W(
      () => t.options.reduce((a, n) => a + n.votes, 0)
    );
    return {
      selectedOption: e,
      calculatePercentage: (a) => s.value > 0 ? Math.round(a / s.value * 100) : 0,
      selectOption: (a) => {
        t.closed || (e.value = a, t.options[a].votes += 1);
      }
    };
  }
}), Bm = {
  class: "live-results-poll",
  role: "group",
  "aria-labelledby": "live-results-poll-label"
}, Mm = {
  id: "live-results-poll-label",
  class: "poll-label"
}, Fm = { class: "options" }, Um = ["onClick", "disabled", "aria-pressed"], jm = {
  key: 0,
  class: "result-percentage"
};
function Vm(t, e, s, r, i, a) {
  return d(), c("div", Bm, [
    f("div", Mm, w(t.question), 1),
    f("div", Fm, [
      (d(!0), c(I, null, L(t.options, (n, o) => (d(), c("button", {
        key: o,
        class: q(["option", { selected: t.selectedOption === o, disabled: t.closed }]),
        onClick: (u) => t.selectOption(o),
        disabled: t.closed,
        "aria-pressed": t.selectedOption === o,
        "aria-label": "Option"
      }, [
        Fe(w(n.text) + " ", 1),
        t.liveResultsVisible ? (d(), c("span", jm, " (" + w(t.calculatePercentage(n.votes)) + "%) ", 1)) : P("", !0)
      ], 10, Um))), 128))
    ])
  ]);
}
const d4 = /* @__PURE__ */ A(Rm, [["render", Vm], ["__scopeId", "data-v-f650da5f"]]), Hm = C({
  name: "LiveStreamPlayer",
  props: {
    streamSrc: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(null), e = m(!1), s = m(!1), r = () => {
      t.value && (t.value.muted = !t.value.muted, e.value = t.value.muted);
    }, i = () => {
      s.value = !1;
    }, a = () => {
    }, n = () => {
      s.value = !0;
    }, o = () => {
      t.value && (e.value = t.value.muted);
    };
    return fs(e, (u) => {
      t.value && (t.value.muted = u);
    }), {
      videoElement: t,
      muted: e,
      buffering: s,
      toggleMute: r,
      onPlay: i,
      onPause: a,
      onBuffering: n,
      onVolumeChange: o
    };
  }
}), zm = {
  class: "live-stream-player",
  role: "region",
  "aria-label": "Live Stream Player"
}, Gm = ["src"], Km = {
  key: 0,
  class: "buffering-overlay"
};
function Wm(t, e, s, r, i, a) {
  return d(), c("div", zm, [
    f("video", {
      ref: "videoElement",
      src: t.streamSrc,
      onPlay: e[0] || (e[0] = (...n) => t.onPlay && t.onPlay(...n)),
      onPause: e[1] || (e[1] = (...n) => t.onPause && t.onPause(...n)),
      onWaiting: e[2] || (e[2] = (...n) => t.onBuffering && t.onBuffering(...n)),
      onVolumechange: e[3] || (e[3] = (...n) => t.onVolumeChange && t.onVolumeChange(...n)),
      controls: ""
    }, null, 40, Gm),
    t.buffering ? (d(), c("div", Km, "Buffering...")) : P("", !0),
    f("button", {
      onClick: e[4] || (e[4] = (...n) => t.toggleMute && t.toggleMute(...n)),
      "aria-label": "Toggle Mute",
      class: "mute-btn"
    }, w(t.muted ? "Unmute" : "Mute"), 1)
  ]);
}
const c4 = /* @__PURE__ */ A(Hm, [["render", Wm], ["__scopeId", "data-v-86ab4e35"]]), Zm = C({
  name: "LoadMoreButtonInList",
  props: {
    items: {
      type: Array,
      required: !0
    },
    batchSize: {
      type: Number,
      default: 5
    }
  },
  setup(t) {
    const e = m([]), s = m(!1), r = m(!1), i = () => {
      s.value || r.value || (s.value = !0, setTimeout(() => {
        const a = t.items.slice(e.value.length, e.value.length + t.batchSize);
        a.length > 0 && e.value.push(...a), e.value.length >= t.items.length && (r.value = !0), s.value = !1;
      }, 1e3));
    };
    return i(), { displayedItems: e, isLoading: s, endOfList: r, loadMore: i };
  }
}), Xm = { class: "load-more-button-in-list" }, Ym = {
  class: "item-list",
  role: "list",
  "aria-label": "Items"
}, Qm = ["disabled", "aria-busy"], Jm = { key: 0 }, xm = { key: 1 }, e1 = {
  key: 1,
  class: "end-of-list-message"
};
function t1(t, e, s, r, i, a) {
  return d(), c("div", Xm, [
    f("ul", Ym, [
      (d(!0), c(I, null, L(t.displayedItems, (n, o) => (d(), c("li", {
        key: o,
        class: "list-item"
      }, w(n), 1))), 128))
    ]),
    t.endOfList ? (d(), c("div", e1, "End of List")) : (d(), c("button", {
      key: 0,
      onClick: e[0] || (e[0] = (...n) => t.loadMore && t.loadMore(...n)),
      disabled: t.isLoading,
      class: "load-more-button",
      "aria-busy": t.isLoading
    }, [
      t.isLoading ? (d(), c("span", Jm, "Loading...")) : (d(), c("span", xm, "Load More"))
    ], 8, Qm))
  ]);
}
const f4 = /* @__PURE__ */ A(Zm, [["render", t1], ["__scopeId", "data-v-c106ae76"]]), s1 = C({
  name: "LoadingBarsWithSteps",
  props: {
    steps: {
      type: Array,
      required: !0
    },
    currentStep: {
      type: Number,
      required: !0
    }
  },
  methods: {
    getStepClass(t) {
      return t < this.currentStep ? "completed" : t === this.currentStep ? "active" : "inactive";
    },
    getProgress(t) {
      return t < this.currentStep ? 100 : t === this.currentStep ? 50 : 0;
    }
  }
}), n1 = ["aria-valuenow", "aria-valuemax"], r1 = { class: "step-label" };
function i1(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "loading-bars",
    role: "progressbar",
    "aria-valuemin": "0",
    "aria-valuenow": t.currentStep,
    "aria-valuemax": t.steps.length
  }, [
    f("ul", null, [
      (d(!0), c(I, null, L(t.steps, (n, o) => (d(), c("li", {
        key: n.id,
        class: q(t.getStepClass(o))
      }, [
        f("div", {
          class: "step-bar",
          style: ne({ "--progress": `${t.getProgress(o)}%` })
        }, null, 4),
        f("span", r1, w(n.label), 1)
      ], 2))), 128))
    ])
  ], 8, n1);
}
const p4 = /* @__PURE__ */ A(s1, [["render", i1], ["__scopeId", "data-v-5c336f48"]]), a1 = C({
  name: "LoadingSpinner",
  props: {
    active: {
      type: Boolean,
      required: !0
    }
  }
}), o1 = {
  key: 0,
  class: "spinner",
  role: "status",
  "aria-live": "polite",
  "aria-label": "Loading"
};
function l1(t, e, s, r, i, a) {
  return t.active ? (d(), c("div", o1, [...e[0] || (e[0] = [
    f("span", { class: "visually-hidden" }, "Loading...", -1)
  ])])) : P("", !0);
}
const h4 = /* @__PURE__ */ A(a1, [["render", l1], ["__scopeId", "data-v-8e2b0a89"]]), u1 = C({
  name: "MediaGallery",
  props: {
    images: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    const e = m("thumbnail"), s = m(0), r = m(!1);
    let i;
    const a = (b) => {
      e.value = b;
    }, n = (b) => {
      s.value = b, a("expanded");
    }, o = () => {
      s.value = (s.value + 1) % t.images.length;
    }, u = () => {
      s.value = (s.value - 1 + t.images.length) % t.images.length;
    }, p = () => {
      r.value ? k() : g();
    }, g = () => {
      r.value = !0, i = window.setInterval(o, 3e3);
    }, k = () => {
      r.value = !1, clearInterval(i);
    }, y = () => {
    };
    return Ce(() => {
    }), Tl(() => {
      k();
    }), {
      viewMode: e,
      currentIndex: s,
      isSlideshow: r,
      setViewMode: a,
      expandImage: n,
      nextImage: o,
      previousImage: u,
      toggleSlideshow: p,
      toggleZoom: y
    };
  }
}), d1 = {
  class: "media-gallery",
  role: "region",
  "aria-label": "Media Gallery"
}, c1 = {
  key: 0,
  class: "thumbnail-view"
}, f1 = ["src", "onClick"], p1 = {
  key: 1,
  class: "expanded-view"
}, h1 = ["src"], g1 = { class: "controls" };
function m1(t, e, s, r, i, a) {
  return d(), c("div", d1, [
    t.viewMode === "thumbnail" ? (d(), c("div", c1, [
      (d(!0), c(I, null, L(t.images, (n, o) => (d(), c("img", {
        key: o,
        src: n,
        alt: "Thumbnail",
        onClick: (u) => t.expandImage(o),
        class: "thumbnail"
      }, null, 8, f1))), 128))
    ])) : P("", !0),
    t.viewMode === "expanded" ? (d(), c("div", p1, [
      f("button", {
        onClick: e[0] || (e[0] = (...n) => t.previousImage && t.previousImage(...n)),
        "aria-label": "Previous Image",
        class: "nav-btn"
      }, "◀"),
      f("img", {
        src: t.images[t.currentIndex],
        alt: "Expanded View",
        class: "expanded-image",
        onClick: e[1] || (e[1] = (...n) => t.toggleZoom && t.toggleZoom(...n))
      }, null, 8, h1),
      f("button", {
        onClick: e[2] || (e[2] = (...n) => t.nextImage && t.nextImage(...n)),
        "aria-label": "Next Image",
        class: "nav-btn"
      }, "▶")
    ])) : P("", !0),
    f("div", g1, [
      f("button", {
        onClick: e[3] || (e[3] = (n) => t.setViewMode("thumbnail")),
        "aria-label": "Thumbnail View",
        class: "control-btn"
      }, "Thumbnail"),
      f("button", {
        onClick: e[4] || (e[4] = (n) => t.setViewMode("expanded")),
        "aria-label": "Expanded View",
        class: "control-btn"
      }, "Expanded"),
      f("button", {
        onClick: e[5] || (e[5] = (...n) => t.toggleSlideshow && t.toggleSlideshow(...n)),
        "aria-label": "Toggle Slideshow",
        class: "control-btn"
      }, w(t.isSlideshow ? "Stop Slideshow" : "Start Slideshow"), 1)
    ])
  ]);
}
const g4 = /* @__PURE__ */ A(u1, [["render", m1], ["__scopeId", "data-v-4974d288"]]), v1 = C({
  name: "MultipleChoicePoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    options: {
      type: Array,
      required: !0
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["update:selectedOptions"],
  setup(t, { emit: e }) {
    const s = m([]);
    return {
      selectedOptions: s,
      handleChange: () => {
        e("update:selectedOptions", s.value);
      }
    };
  }
}), b1 = {
  role: "group",
  "aria-labelledby": "poll-question",
  class: "poll"
}, y1 = { id: "poll-question" }, $1 = ["id", "value", "disabled", "aria-checked"], k1 = ["for"];
function w1(t, e, s, r, i, a) {
  return d(), c("div", b1, [
    f("p", y1, w(t.question), 1),
    (d(!0), c(I, null, L(t.options, (n) => (d(), c("div", {
      key: n,
      class: "option"
    }, [
      R(f("input", {
        type: "checkbox",
        id: n,
        value: n,
        "onUpdate:modelValue": e[0] || (e[0] = (o) => t.selectedOptions = o),
        disabled: t.isDisabled,
        onChange: e[1] || (e[1] = (...o) => t.handleChange && t.handleChange(...o)),
        "aria-checked": t.selectedOptions.includes(n)
      }, null, 40, $1), [
        [_l, t.selectedOptions]
      ]),
      f("label", { for: n }, w(n), 9, k1)
    ]))), 128))
  ]);
}
const m4 = /* @__PURE__ */ A(v1, [["render", w1], ["__scopeId", "data-v-e84ac6d0"]]), C1 = C({
  name: "MultiselectList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m([]), e = m(null);
    return { selectedItems: t, hoveredItem: e, toggleItemSelection: (r) => {
      if (r.disabled) return;
      const i = t.value.indexOf(r.value);
      i === -1 ? t.value.push(r.value) : t.value.splice(i, 1);
    } };
  }
}), A1 = {
  class: "multiselect-list",
  role: "listbox",
  "aria-multiselectable": "true"
}, E1 = {
  class: "item-list",
  role: "list",
  "aria-label": "Selectable Items"
}, S1 = ["onClick", "onMouseover", "aria-selected", "aria-disabled"];
function T1(t, e, s, r, i, a) {
  return d(), c("div", A1, [
    f("ul", E1, [
      (d(!0), c(I, null, L(t.items, (n) => (d(), c("li", {
        key: n.value,
        class: q(["list-item", { selected: t.selectedItems.includes(n.value), disabled: n.disabled }]),
        onClick: (o) => t.toggleItemSelection(n),
        onMouseover: (o) => t.hoveredItem = n.value,
        onMouseleave: e[0] || (e[0] = (o) => t.hoveredItem = null),
        "aria-selected": t.selectedItems.includes(n.value),
        "aria-disabled": n.disabled
      }, w(n.label), 43, S1))), 128))
    ])
  ]);
}
const v4 = /* @__PURE__ */ A(C1, [["render", T1], ["__scopeId", "data-v-d45a7e8f"]]), _1 = C({
  name: "Notification",
  props: {
    notificationType: {
      type: String,
      default: "success"
    },
    message: {
      type: String,
      default: "This is a notification message."
    },
    isDismissed: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.isDismissed);
    return { localIsDismissed: e, dismiss: () => {
      e.value = !0;
    } };
  }
});
function N1(t, e, s, r, i, a) {
  return t.localIsDismissed ? P("", !0) : (d(), c("div", {
    key: 0,
    class: q(["notification", t.notificationType]),
    role: "alert"
  }, [
    f("span", null, w(t.message), 1),
    f("button", {
      class: "close-btn",
      onClick: e[0] || (e[0] = (...n) => t.dismiss && t.dismiss(...n)),
      "aria-label": "Dismiss notification"
    }, "✖")
  ], 2));
}
const b4 = /* @__PURE__ */ A(_1, [["render", N1], ["__scopeId", "data-v-cce4ab9d"]]), I1 = C({
  name: "NotificationBellIcon",
  props: {
    hasNotifications: {
      type: Boolean,
      required: !0
    },
    dismissed: {
      type: Boolean,
      required: !1,
      default: !1
    }
  }
}), L1 = {
  class: "notification-bell",
  role: "button",
  "aria-label": "Notification Bell"
}, q1 = {
  key: 0,
  class: "notification-dot",
  "aria-label": "New Notifications"
};
function O1(t, e, s, r, i, a) {
  return d(), c("div", L1, [
    (d(), c("svg", {
      class: q(["bell-icon", { "has-notifications": t.hasNotifications, dismissed: t.dismissed }]),
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "currentColor",
      "aria-hidden": "true"
    }, [...e[0] || (e[0] = [
      f("path", { d: "M12 2C10.34 2 9 3.34 9 5v1.07C6.83 6.57 5 8.64 5 11v5h14v-5c0-2.36-1.83-4.43-4-4.93V5c0-1.66-1.34-3-3-3zm-1 19c0 .55.45 1 1 1s1-.45 1-1h-2z" }, null, -1)
    ])], 2)),
    t.hasNotifications ? (d(), c("span", q1)) : P("", !0)
  ]);
}
const y4 = /* @__PURE__ */ A(I1, [["render", O1], ["__scopeId", "data-v-5f09368b"]]), P1 = C({
  name: "NumberInputWithIncrement",
  props: {
    modelValue: {
      type: Number,
      default: 0
    },
    step: {
      type: Number,
      default: 1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["update:modelValue"],
  setup(t, { emit: e }) {
    const s = m(t.modelValue);
    return { currentValue: s, increment: () => {
      s.value += t.step, e("update:modelValue", s.value);
    }, decrement: () => {
      s.value -= t.step, e("update:modelValue", s.value);
    } };
  }
}), D1 = { class: "number-input-container" }, R1 = ["disabled"], B1 = ["disabled"], M1 = ["disabled"];
function F1(t, e, s, r, i, a) {
  return d(), c("div", D1, [
    f("button", {
      class: "decrement-button",
      onClick: e[0] || (e[0] = (...n) => t.decrement && t.decrement(...n)),
      disabled: t.disabled,
      "aria-label": "Decrement"
    }, " - ", 8, R1),
    R(f("input", {
      type: "number",
      "onUpdate:modelValue": e[1] || (e[1] = (n) => t.currentValue = n),
      disabled: t.disabled,
      "aria-label": "Number Input"
    }, null, 8, B1), [
      [H, t.currentValue]
    ]),
    f("button", {
      class: "increment-button",
      onClick: e[2] || (e[2] = (...n) => t.increment && t.increment(...n)),
      disabled: t.disabled,
      "aria-label": "Increment"
    }, " + ", 8, M1)
  ]);
}
const $4 = /* @__PURE__ */ A(P1, [["render", F1], ["__scopeId", "data-v-0261d126"]]), U1 = C({
  name: "NumberedList",
  props: {
    items: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m(null), e = m(null);
    return { selectedItem: t, hoveredItem: e, selectItem: (r) => {
      r.disabled || (t.value = r.value);
    } };
  }
}), j1 = {
  class: "numbered-list",
  role: "list",
  "aria-label": "Numbered Items"
}, V1 = ["onClick", "onMouseover", "aria-disabled"];
function H1(t, e, s, r, i, a) {
  return d(), c("ol", j1, [
    (d(!0), c(I, null, L(t.items, (n) => (d(), c("li", {
      key: n.value,
      class: q(["list-item", { selected: t.selectedItem === n.value, disabled: n.disabled }]),
      onClick: (o) => t.selectItem(n),
      onMouseover: (o) => t.hoveredItem = n.value,
      onMouseleave: e[0] || (e[0] = (o) => t.hoveredItem = null),
      "aria-disabled": n.disabled
    }, w(n.label), 43, V1))), 128))
  ]);
}
const k4 = /* @__PURE__ */ A(U1, [["render", H1], ["__scopeId", "data-v-3038608d"]]), z1 = C({
  name: "OpenEndedPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    initialResponses: {
      type: Array,
      default: () => []
    },
    resultsVisible: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(""), s = m([...t.initialResponses]);
    return {
      response: e,
      responses: s,
      submitResponse: () => {
        e.value.trim() && (s.value.push(e.value.trim()), e.value = "");
      }
    };
  }
}), G1 = {
  class: "open-ended-poll",
  role: "form",
  "aria-labelledby": "open-ended-poll-label"
}, K1 = {
  id: "open-ended-poll-label",
  class: "poll-label"
}, W1 = ["disabled", "aria-disabled"], Z1 = ["disabled"], X1 = {
  key: 0,
  class: "results"
};
function Y1(t, e, s, r, i, a) {
  return d(), c("div", G1, [
    f("label", K1, w(t.question), 1),
    R(f("textarea", {
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.response = n),
      disabled: t.disabled,
      "aria-disabled": t.disabled,
      "aria-required": "true",
      placeholder: "Type your response here...",
      class: "response-input"
    }, null, 8, W1), [
      [H, t.response]
    ]),
    f("button", {
      onClick: e[1] || (e[1] = (...n) => t.submitResponse && t.submitResponse(...n)),
      disabled: t.disabled || !t.response.trim(),
      class: "submit-button"
    }, " Submit ", 8, Z1),
    t.resultsVisible ? (d(), c("div", X1, [
      e[2] || (e[2] = f("h3", null, "Responses:", -1)),
      f("ul", null, [
        (d(!0), c(I, null, L(t.responses, (n, o) => (d(), c("li", { key: o }, w(n), 1))), 128))
      ])
    ])) : P("", !0)
  ]);
}
const w4 = /* @__PURE__ */ A(z1, [["render", Y1], ["__scopeId", "data-v-5c6668a4"]]), Q1 = C({
  name: "Pagination",
  props: {
    totalPages: {
      type: Number,
      required: !0
    },
    currentPage: {
      type: Number,
      required: !0
    }
  },
  setup(t, { emit: e }) {
    const s = m(null);
    return { pages: W(() => Array.from({ length: t.totalPages }, (a, n) => n + 1)), hoveredPage: s, changePage: (a) => {
      a !== t.currentPage && e("update:currentPage", a);
    } };
  }
}), J1 = {
  class: "pagination",
  "aria-label": "Pagination Navigation"
}, x1 = { class: "pagination-list" }, ev = ["onClick", "onMouseover", "aria-current"];
function tv(t, e, s, r, i, a) {
  return d(), c("nav", J1, [
    f("ul", x1, [
      (d(!0), c(I, null, L(t.pages, (n) => (d(), c("li", {
        key: n,
        class: q(["pagination-item", { active: n === t.currentPage }]),
        onClick: (o) => t.changePage(n),
        onMouseover: (o) => t.hoveredPage = n,
        onMouseleave: e[0] || (e[0] = (o) => t.hoveredPage = null),
        "aria-current": n === t.currentPage ? "page" : void 0
      }, w(n), 43, ev))), 128))
    ])
  ]);
}
const C4 = /* @__PURE__ */ A(Q1, [["render", tv], ["__scopeId", "data-v-62783a13"]]), sv = C({
  name: "PaginationControl",
  props: {
    totalPages: {
      type: Number,
      required: !0
    },
    currentPage: {
      type: Number,
      default: 1
    },
    rowsPerPageOptions: {
      type: Array,
      default: () => [10, 20, 50, 100]
    }
  },
  emits: ["update:currentPage", "update:rowsPerPage"],
  setup(t, { emit: e }) {
    const s = m(t.rowsPerPageOptions[0]), r = W(() => t.currentPage === 1), i = W(() => t.currentPage === t.totalPages);
    return {
      selectedRowsPerPage: s,
      isFirstPage: r,
      isLastPage: i,
      setPage: (o) => {
        o >= 1 && o <= t.totalPages && e("update:currentPage", o);
      },
      setRowsPerPage: (o) => {
        s.value = o, e("update:rowsPerPage", o);
      }
    };
  }
}), nv = { class: "pagination-control" }, rv = ["disabled"], iv = ["disabled"], av = ["disabled"], ov = ["disabled"], lv = ["value"];
function uv(t, e, s, r, i, a) {
  return d(), c("div", nv, [
    f("button", {
      onClick: e[0] || (e[0] = (n) => t.setPage(1)),
      disabled: t.isFirstPage
    }, "First", 8, rv),
    f("button", {
      onClick: e[1] || (e[1] = (n) => t.setPage(t.currentPage - 1)),
      disabled: t.isFirstPage
    }, "Previous", 8, iv),
    f("span", null, "Page " + w(t.currentPage) + " of " + w(t.totalPages), 1),
    f("button", {
      onClick: e[2] || (e[2] = (n) => t.setPage(t.currentPage + 1)),
      disabled: t.isLastPage
    }, "Next", 8, av),
    f("button", {
      onClick: e[3] || (e[3] = (n) => t.setPage(t.totalPages)),
      disabled: t.isLastPage
    }, "Last", 8, ov),
    R(f("select", {
      "onUpdate:modelValue": e[4] || (e[4] = (n) => t.selectedRowsPerPage = n),
      onChange: e[5] || (e[5] = (n) => t.setRowsPerPage(t.selectedRowsPerPage))
    }, [
      (d(!0), c(I, null, L(t.rowsPerPageOptions, (n) => (d(), c("option", {
        key: n,
        value: n
      }, w(n) + " rows per page ", 9, lv))), 128))
    ], 544), [
      [ye, t.selectedRowsPerPage]
    ])
  ]);
}
const A4 = /* @__PURE__ */ A(sv, [["render", uv], ["__scopeId", "data-v-e9633912"]]), dv = C({
  name: "PasswordConfirmationField",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    const t = m(""), e = m(""), s = W(() => t.value === e.value);
    return { password: t, confirmPassword: e, isMatching: s };
  }
}), cv = { class: "password-confirmation-container" }, fv = ["disabled"], pv = ["disabled"];
function hv(t, e, s, r, i, a) {
  return d(), c("div", cv, [
    R(f("input", {
      type: "password",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.password = n),
      disabled: t.disabled,
      placeholder: "Enter password",
      "aria-label": "Enter password"
    }, null, 8, fv), [
      [H, t.password]
    ]),
    R(f("input", {
      type: "password",
      "onUpdate:modelValue": e[1] || (e[1] = (n) => t.confirmPassword = n),
      disabled: t.disabled,
      placeholder: "Confirm password",
      "aria-label": "Confirm password"
    }, null, 8, pv), [
      [H, t.confirmPassword]
    ]),
    f("p", {
      class: q({ match: t.isMatching, "not-match": !t.isMatching })
    }, w(t.isMatching ? "Passwords match" : "Passwords do not match"), 3)
  ]);
}
const E4 = /* @__PURE__ */ A(dv, [["render", hv], ["__scopeId", "data-v-7bc855fa"]]), gv = C({
  name: "PinnedList",
  props: {
    items: {
      type: Array,
      required: !0
    },
    selectedItem: {
      type: Number,
      required: !0
    }
  },
  setup(t, { emit: e }) {
    return { hoveredItem: m(null), selectItem: (i) => {
      e("update:selectedItem", i);
    } };
  }
}), mv = { class: "pinned-list" }, vv = ["onClick", "onMouseover", "aria-selected"];
function bv(t, e, s, r, i, a) {
  return d(), c("ul", mv, [
    (d(!0), c(I, null, L(t.items, (n) => (d(), c("li", {
      key: n.id,
      class: q([
        "pinned-list-item",
        { pinned: n.pinned, selected: n.id === t.selectedItem, hover: n.id === t.hoveredItem }
      ]),
      onClick: (o) => t.selectItem(n.id),
      onMouseover: (o) => t.hoveredItem = n.id,
      onMouseleave: e[0] || (e[0] = (o) => t.hoveredItem = null),
      "aria-selected": n.id === t.selectedItem ? "true" : "false"
    }, w(n.label), 43, vv))), 128))
  ]);
}
const S4 = /* @__PURE__ */ A(gv, [["render", bv], ["__scopeId", "data-v-ecd634ef"]]), yv = C({
  name: "PlayingCard",
  props: {
    flipped: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["update:flipped"],
  setup(t, { emit: e }) {
    return { handleClick: () => {
      t.disabled || e("update:flipped", !t.flipped);
    } };
  }
}), $v = ["aria-pressed", "aria-disabled"], kv = {
  key: 0,
  class: "card-face card-front"
}, wv = {
  key: 1,
  class: "card-face card-back"
};
function Cv(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["playing-card", { "is-flipped": t.flipped, "is-disabled": t.disabled }]),
    onClick: e[0] || (e[0] = (...n) => t.handleClick && t.handleClick(...n)),
    role: "button",
    "aria-pressed": t.flipped,
    "aria-disabled": t.disabled,
    tabindex: "0"
  }, [
    t.flipped ? (d(), c("div", wv, [
      ie(t.$slots, "front", {}, () => [
        e[2] || (e[2] = Fe("Ace of Spades", -1))
      ], !0)
    ])) : (d(), c("div", kv, [
      ie(t.$slots, "back", {}, () => [
        e[1] || (e[1] = Fe("Back Design", -1))
      ], !0)
    ]))
  ], 10, $v);
}
const T4 = /* @__PURE__ */ A(yv, [["render", Cv], ["__scopeId", "data-v-4b36289e"]]), Av = C({
  name: "PodcastPlayer",
  props: {
    episodes: {
      type: Array,
      required: !0
    }
  },
  setup() {
    const t = m(!1), e = m(null), s = m(!1), r = m(!0);
    return {
      isPlaying: t,
      currentEpisodeIndex: e,
      isDownloading: s,
      showEpisodeList: r,
      togglePlayPause: () => {
        e.value !== null && (t.value = !t.value);
      },
      playEpisode: (o) => {
        e.value = o, t.value = !0;
      },
      downloadEpisode: () => {
        e.value !== null && (s.value = !0, setTimeout(() => {
          s.value = !1;
        }, 3e3));
      }
    };
  }
}), Ev = {
  class: "podcast-player",
  role: "region",
  "aria-label": "Podcast Player"
}, Sv = { class: "player-controls" }, Tv = {
  key: 0,
  class: "episode-list"
}, _v = ["onClick"];
function Nv(t, e, s, r, i, a) {
  return d(), c("div", Ev, [
    f("div", Sv, [
      f("button", {
        onClick: e[0] || (e[0] = (...n) => t.togglePlayPause && t.togglePlayPause(...n)),
        "aria-label": "Play/Pause",
        class: "control-btn"
      }, w(t.isPlaying ? "Pause" : "Play"), 1),
      f("button", {
        onClick: e[1] || (e[1] = (...n) => t.downloadEpisode && t.downloadEpisode(...n)),
        "aria-label": "Download Episode",
        class: "control-btn"
      }, w(t.isDownloading ? "Downloading..." : "Download"), 1)
    ]),
    t.showEpisodeList ? (d(), c("div", Tv, [
      f("ul", null, [
        (d(!0), c(I, null, L(t.episodes, (n, o) => (d(), c("li", {
          key: o,
          onClick: (u) => t.playEpisode(o)
        }, w(n.title), 9, _v))), 128))
      ])
    ])) : P("", !0)
  ]);
}
const _4 = /* @__PURE__ */ A(Av, [["render", Nv], ["__scopeId", "data-v-6c576cf9"]]), Iv = C({
  name: "PokerChips",
  props: {
    chips: {
      type: Array,
      default: () => []
    },
    state: {
      type: String,
      default: "stacked",
      validator: (t) => ["stacked", "moving", "betPlaced", "allIn"].includes(t)
    }
  },
  computed: {
    stateClass() {
      return this.state;
    }
  }
}), Lv = ["aria-label"];
function qv(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["poker-chips", t.stateClass])
  }, [
    (d(!0), c(I, null, L(t.chips, (n) => (d(), c("div", {
      key: n.id,
      class: "chip",
      style: ne({ backgroundColor: n.color }),
      "aria-label": `Chip denomination: ${n.denomination}`
    }, w(n.denomination), 13, Lv))), 128))
  ], 2);
}
const N4 = /* @__PURE__ */ A(Iv, [["render", qv], ["__scopeId", "data-v-4c1ec75e"]]), Ov = C({
  name: "PokerHand",
  props: {
    cards: {
      type: Array,
      required: !0
    },
    revealed: {
      type: Boolean,
      default: !1
    },
    folded: {
      type: Boolean,
      default: !1
    }
  }
}), Pv = ["data-folded"], Dv = ["data-revealed"], Rv = {
  key: 0,
  class: "card-value"
};
function Bv(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "poker-hand",
    "aria-label": "Poker Hand",
    "data-folded": t.folded
  }, [
    (d(!0), c(I, null, L(t.cards, (n) => (d(), c("div", {
      key: n.id,
      class: "card",
      "data-revealed": t.revealed
    }, [
      t.revealed ? (d(), c("span", Rv, w(n.value), 1)) : P("", !0)
    ], 8, Dv))), 128))
  ], 8, Pv);
}
const I4 = /* @__PURE__ */ A(Ov, [["render", Bv], ["__scopeId", "data-v-a5885677"]]), Mv = C({
  name: "PokerTable",
  props: {
    seats: {
      type: Array,
      default: () => []
    },
    communityCards: {
      type: Array,
      default: () => []
    },
    tableColor: {
      type: String,
      default: "var(--table-green)"
    }
  }
}), Fv = { class: "community-cards" };
function Uv(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "poker-table",
    style: ne({ backgroundColor: t.tableColor })
  }, [
    (d(!0), c(I, null, L(t.seats, (n) => (d(), c("div", {
      class: "seats",
      key: n.id
    }, [
      f("div", {
        class: q(["player", { "player-active": n.active }])
      }, w(n.name), 3)
    ]))), 128)),
    f("div", Fv, [
      (d(!0), c(I, null, L(t.communityCards, (n) => (d(), c("div", {
        class: "card",
        key: n.id
      }, w(n.suit) + w(n.rank), 1))), 128))
    ]),
    e[0] || (e[0] = f("div", {
      class: "dealer-button",
      role: "button",
      "aria-label": "Dealer button"
    }, null, -1))
  ], 4);
}
const L4 = /* @__PURE__ */ A(Mv, [["render", Uv], ["__scopeId", "data-v-e5c0bbc5"]]), jv = C({
  name: "PokerTimer",
  props: {
    initialTime: {
      type: Number,
      default: 30
    }
  },
  setup(t) {
    const e = m(t.initialTime), s = m(!1), r = W(() => {
      const u = Math.floor(e.value / 60), p = e.value % 60;
      return `${u}:${p < 10 ? "0" : ""}${p}`;
    }), i = W(() => e.value <= 10), a = () => {
      !s.value && e.value > 0 && (e.value -= 1);
    }, n = () => {
      s.value = !s.value;
    };
    let o;
    return Ce(() => {
      o = setInterval(a, 1e3);
    }), Di(() => {
      clearInterval(o);
    }), {
      timeLeft: e,
      formattedTime: r,
      timeRunningOut: i,
      isPaused: s,
      togglePause: n
    };
  }
}), Vv = {
  class: "poker-timer",
  "aria-label": "Poker Timer"
};
function Hv(t, e, s, r, i, a) {
  return d(), c("div", Vv, [
    f("div", {
      class: q(["timer-display", { "time-running-out": t.timeRunningOut }])
    }, w(t.formattedTime), 3),
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.togglePause && t.togglePause(...n)),
      class: "timer-button"
    }, w(t.isPaused ? "Resume" : "Pause"), 1)
  ]);
}
const q4 = /* @__PURE__ */ A(jv, [["render", Hv], ["__scopeId", "data-v-439e81ff"]]), zv = C({
  name: "Pot",
  props: {
    chips: {
      type: Array,
      default: () => []
    },
    totalChips: {
      type: Number,
      default: 0
    },
    isWon: {
      type: Boolean,
      default: !1
    }
  }
}), Gv = { class: "total" };
function Kv(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["pot", { won: t.isWon }]),
    "aria-label": "Poker Pot"
  }, [
    f("div", {
      class: q(["chips", { empty: t.totalChips === 0 }])
    }, [
      fo(Nl, {
        name: "chip-move",
        tag: "div",
        class: "chip-stack"
      }, {
        default: Ri(() => [
          (d(!0), c(I, null, L(t.chips, (n, o) => (d(), c("div", {
            key: o,
            class: "chip"
          }, w(n), 1))), 128))
        ]),
        _: 1
      })
    ], 2),
    f("div", Gv, "Total: " + w(t.totalChips), 1)
  ], 2);
}
const O4 = /* @__PURE__ */ A(zv, [["render", Kv], ["__scopeId", "data-v-177d41d0"]]), Wv = C({
  name: "ProgressBar",
  props: {
    progress: {
      type: Number,
      required: !0,
      validator: (t) => t >= 0 && t <= 100
    },
    disabled: {
      type: Boolean,
      required: !1,
      default: !1
    }
  }
}), Zv = ["aria-valuenow", "aria-label"];
function Xv(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["progress-bar-container", { disabled: t.disabled }]),
    role: "progressbar",
    "aria-valuenow": t.progress,
    "aria-valuemin": "0",
    "aria-valuemax": "100",
    "aria-label": `Progress: ${t.progress}%`
  }, [
    f("div", {
      class: "progress-bar",
      style: ne({ width: t.progress + "%" })
    }, null, 4)
  ], 10, Zv);
}
const P4 = /* @__PURE__ */ A(Wv, [["render", Xv], ["__scopeId", "data-v-0da1f739"]]), Yv = C({
  name: "ProgressCircle",
  props: {
    progress: {
      type: Number,
      required: !0,
      validator: (t) => t >= 0 && t <= 100
    },
    status: {
      type: String,
      required: !1,
      default: "active",
      validator: (t) => ["complete", "incomplete", "paused", "active"].includes(t)
    }
  }
}), Qv = ["aria-valuenow", "aria-label"], Jv = {
  viewBox: "0 0 36 36",
  class: "circular-chart"
}, xv = ["stroke-dasharray"];
function eb(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "progress-circle",
    role: "progressbar",
    "aria-valuenow": t.progress,
    "aria-valuemin": "0",
    "aria-valuemax": "100",
    "aria-label": `Progress: ${t.progress}%`,
    status: t.status
  }, [
    (d(), c("svg", Jv, [
      e[0] || (e[0] = f("path", {
        class: "circle-bg",
        d: "M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
      }, null, -1)),
      f("path", {
        class: "circle",
        "stroke-dasharray": `${t.progress}, 100`,
        d: "M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
      }, null, 8, xv)
    ]))
  ], 8, Qv);
}
const D4 = /* @__PURE__ */ A(Yv, [["render", eb], ["__scopeId", "data-v-d33da7d5"]]), tb = C({
  name: "PublicViewCalendar",
  props: {
    selectedCategoryProp: {
      type: String,
      default: ""
    },
    selectedEventProp: {
      type: Object,
      default: null
    }
  },
  setup(t) {
    const e = m([
      { id: 1, title: "Project Meeting", description: "Discussing project scope.", category: "Work", location: "Room 101", date: "2023-11-01" },
      { id: 2, title: "Yoga Class", description: "Morning yoga session.", category: "Health", location: "Gym", date: "2023-11-02" }
    ]), s = m([...new Set(e.value.map((g) => g.category))]), r = m([...new Set(e.value.map((g) => g.location))]), i = m(""), a = m(""), n = m(t.selectedEventProp), o = W(() => e.value.filter((g) => (!i.value || g.category === i.value) && (!a.value || g.location === a.value)));
    return {
      categories: s,
      locations: r,
      selectedCategory: i,
      selectedLocation: a,
      filteredEvents: o,
      selectedEvent: n,
      showEventDetails: (g) => {
        n.value = g;
      },
      closeEventDetails: () => {
        n.value = null;
      }
    };
  }
}), sb = {
  class: "calendar",
  role: "region",
  "aria-label": "Public Calendar"
}, nb = { class: "filter-options" }, rb = ["value"], ib = ["value"], ab = { class: "events" }, ob = ["onClick"], lb = {
  key: 0,
  class: "event-details",
  role: "dialog",
  "aria-labelledby": "event-title"
}, ub = { id: "event-title" };
function db(t, e, s, r, i, a) {
  return d(), c("div", sb, [
    f("div", nb, [
      e[5] || (e[5] = f("label", { for: "category-filter" }, "Category:", -1)),
      R(f("select", {
        id: "category-filter",
        "onUpdate:modelValue": e[0] || (e[0] = (n) => t.selectedCategory = n),
        "aria-label": "Filter by category"
      }, [
        e[3] || (e[3] = f("option", { value: "" }, "All", -1)),
        (d(!0), c(I, null, L(t.categories, (n) => (d(), c("option", {
          key: n,
          value: n
        }, w(n), 9, rb))), 128))
      ], 512), [
        [ye, t.selectedCategory]
      ]),
      e[6] || (e[6] = f("label", { for: "location-filter" }, "Location:", -1)),
      R(f("select", {
        id: "location-filter",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.selectedLocation = n),
        "aria-label": "Filter by location"
      }, [
        e[4] || (e[4] = f("option", { value: "" }, "All", -1)),
        (d(!0), c(I, null, L(t.locations, (n) => (d(), c("option", {
          key: n,
          value: n
        }, w(n), 9, ib))), 128))
      ], 512), [
        [ye, t.selectedLocation]
      ])
    ]),
    f("div", ab, [
      (d(!0), c(I, null, L(t.filteredEvents, (n) => (d(), c("div", {
        key: n.id,
        class: "event",
        onClick: (o) => t.showEventDetails(n)
      }, [
        f("h3", null, w(n.title), 1),
        f("p", null, w(n.date), 1)
      ], 8, ob))), 128))
    ]),
    fo(co, { name: "fade" }, {
      default: Ri(() => [
        t.selectedEvent ? (d(), c("div", lb, [
          f("h2", ub, w(t.selectedEvent.title), 1),
          f("p", null, w(t.selectedEvent.description), 1),
          f("button", {
            class: "close-details",
            onClick: e[2] || (e[2] = (...n) => t.closeEventDetails && t.closeEventDetails(...n)),
            "aria-label": "Close event details"
          }, "Close")
        ])) : P("", !0)
      ]),
      _: 1
    })
  ]);
}
const R4 = /* @__PURE__ */ A(tb, [["render", db], ["__scopeId", "data-v-4ed1ea3e"]]), cb = C({
  name: "RadioButton",
  props: {
    checked: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    },
    value: {
      type: String,
      required: !0
    },
    name: {
      type: String,
      required: !0
    }
  },
  emits: ["update:checked"],
  methods: {
    onChange(t) {
      this.disabled || this.$emit("update:checked", t.target.checked);
    }
  }
}), fb = { class: "radio-button-container" }, pb = ["checked", "disabled", "aria-checked", "aria-disabled"], hb = { class: "radio-label" };
function gb(t, e, s, r, i, a) {
  return d(), c("div", fb, [
    f("label", {
      class: q({ disabled: t.disabled })
    }, [
      f("input", {
        type: "radio",
        checked: t.checked,
        disabled: t.disabled,
        onChange: e[0] || (e[0] = (...n) => t.onChange && t.onChange(...n)),
        "aria-checked": t.checked,
        "aria-disabled": t.disabled
      }, null, 40, pb),
      f("span", hb, [
        ie(t.$slots, "default", {}, void 0, !0)
      ])
    ], 2)
  ]);
}
const B4 = /* @__PURE__ */ A(cb, [["render", gb], ["__scopeId", "data-v-31d50aca"]]), mb = C({
  name: "RaiseButton",
  props: {
    disabled: {
      type: Boolean,
      default: !1
    }
  }
}), vb = ["disabled"];
function bb(t, e, s, r, i, a) {
  return d(), c("button", {
    class: "raise-button",
    disabled: t.disabled,
    "aria-label": "Raise Bet"
  }, " Raise ", 8, vb);
}
const M4 = /* @__PURE__ */ A(mb, [["render", bb], ["__scopeId", "data-v-cd38f00c"]]), yb = C({
  name: "RangeSlider",
  props: {
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      default: 100
    },
    value: {
      type: Number,
      default: 50
    },
    step: {
      type: Number,
      default: 1
    },
    disabled: {
      type: Boolean,
      default: !1
    },
    label: {
      type: String,
      default: ""
    },
    labelPosition: {
      type: String,
      default: "right"
    }
  },
  emits: ["update:value"],
  methods: {
    onInput(t) {
      this.$emit("update:value", Number(t.target.value));
    },
    onFocus() {
      this.$el.classList.add("focused");
    },
    onBlur() {
      this.$el.classList.remove("focused");
    }
  }
}), $b = { class: "range-slider-container" }, kb = ["aria-label", "aria-disabled"], wb = { key: 0 }, Cb = ["min", "max", "step", "value", "disabled"], Ab = { key: 1 };
function Eb(t, e, s, r, i, a) {
  return d(), c("div", $b, [
    f("label", {
      class: q(["range-label", t.labelPosition]),
      "aria-label": `Range slider at ${t.value}`,
      "aria-disabled": t.disabled
    }, [
      t.labelPosition === "left" || t.labelPosition === "center" ? (d(), c("span", wb, w(t.label), 1)) : P("", !0),
      f("input", {
        type: "range",
        min: t.min,
        max: t.max,
        step: t.step,
        value: t.value,
        disabled: t.disabled,
        onInput: e[0] || (e[0] = (...n) => t.onInput && t.onInput(...n)),
        onFocus: e[1] || (e[1] = (...n) => t.onFocus && t.onFocus(...n)),
        onBlur: e[2] || (e[2] = (...n) => t.onBlur && t.onBlur(...n))
      }, null, 40, Cb),
      t.labelPosition === "right" ? (d(), c("span", Ab, w(t.label), 1)) : P("", !0)
    ], 10, kb)
  ]);
}
const F4 = /* @__PURE__ */ A(yb, [["render", Eb], ["__scopeId", "data-v-99cac0a4"]]), Sb = C({
  name: "RankingPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    options: {
      type: Array,
      required: !0
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m([...t.options]);
    return {
      rankedOptions: e,
      onDragStart: (i) => (a) => {
        var n;
        (n = a.dataTransfer) == null || n.setData("text/plain", i.toString());
      },
      onDrop: (i) => (a) => {
        var u;
        const n = Number((u = a.dataTransfer) == null ? void 0 : u.getData("text")), o = e.value[n];
        e.value.splice(n, 1), e.value.splice(i, 0, o);
      }
    };
  }
}), Tb = {
  role: "list",
  "aria-labelledby": "poll-question",
  class: "ranking-poll"
}, _b = { id: "poll-question" }, Nb = ["draggable", "onDragstart", "onDrop"];
function Ib(t, e, s, r, i, a) {
  return d(), c("div", Tb, [
    f("p", _b, w(t.question), 1),
    f("ul", null, [
      (d(!0), c(I, null, L(t.rankedOptions, (n, o) => (d(), c("li", {
        key: n,
        draggable: !t.isDisabled,
        onDragstart: (u) => t.onDragStart(o),
        onDragover: e[0] || (e[0] = de(() => {
        }, ["prevent"])),
        onDrop: (u) => t.onDrop(o),
        class: "rank-option"
      }, [
        f("span", null, w(o + 1) + ".", 1),
        Fe(" " + w(n), 1)
      ], 40, Nb))), 128))
    ])
  ]);
}
const U4 = /* @__PURE__ */ A(Sb, [["render", Ib], ["__scopeId", "data-v-f7cd36d5"]]), Lb = C({
  name: "RatingStars",
  props: {
    maxStars: {
      type: Number,
      default: 5
    },
    initialRating: {
      type: Number,
      default: 0
    },
    inactive: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialRating), s = m(0);
    return {
      currentRating: e,
      hoverRating: s,
      selectRating: (a) => {
        t.inactive || (e.value = a);
      },
      setHoverRating: (a) => {
        t.inactive || (s.value = a);
      },
      stars: Array.from({ length: t.maxStars }, (a, n) => n + 1)
    };
  }
}), qb = {
  class: "rating-stars",
  role: "radiogroup",
  "aria-label": "Rating"
}, Ob = ["aria-checked", "aria-label", "onClick", "onMouseenter"];
function Pb(t, e, s, r, i, a) {
  return d(), c("div", qb, [
    (d(!0), c(I, null, L(t.stars, (n) => (d(), c("button", {
      key: n,
      type: "button",
      class: q(["star", { active: n <= t.currentRating, hover: n <= t.hoverRating }]),
      "aria-checked": n === t.currentRating,
      "aria-label": `${n} Star${n > 1 ? "s" : ""}`,
      onClick: (o) => t.selectRating(n),
      onMouseenter: (o) => t.setHoverRating(n),
      onMouseleave: e[0] || (e[0] = (o) => t.setHoverRating(0))
    }, " ★ ", 42, Ob))), 128))
  ]);
}
const j4 = /* @__PURE__ */ A(Lb, [["render", Pb], ["__scopeId", "data-v-97f264b6"]]), Db = C({
  name: "RecurringEventScheduler",
  props: {
    feedbackMessageProp: {
      type: String,
      default: ""
    }
  },
  setup(t) {
    const e = m("daily"), s = m(""), r = m(""), i = m(t.feedbackMessageProp);
    return {
      recurrencePattern: e,
      startDate: s,
      endDate: r,
      feedbackMessage: i,
      setRecurrence: () => {
        s.value && r.value ? i.value = `Recurrence set: ${e.value} from ${s.value} to ${r.value}` : i.value = "Please select start and end dates";
      }
    };
  }
}), Rb = {
  class: "recurring-event-scheduler",
  role: "region",
  "aria-label": "Recurring Event Scheduler"
}, Bb = { class: "recurrence-settings" }, Mb = {
  key: 0,
  class: "feedback"
};
function Fb(t, e, s, r, i, a) {
  return d(), c("div", Rb, [
    f("div", Bb, [
      e[5] || (e[5] = f("label", { for: "recurrence-pattern" }, "Recurrence Pattern:", -1)),
      R(f("select", {
        id: "recurrence-pattern",
        "onUpdate:modelValue": e[0] || (e[0] = (n) => t.recurrencePattern = n),
        "aria-label": "Select recurrence pattern"
      }, [...e[4] || (e[4] = [
        f("option", { value: "daily" }, "Daily", -1),
        f("option", { value: "weekly" }, "Weekly", -1),
        f("option", { value: "monthly" }, "Monthly", -1)
      ])], 512), [
        [ye, t.recurrencePattern]
      ]),
      e[6] || (e[6] = f("label", { for: "start-date" }, "Start Date:", -1)),
      R(f("input", {
        id: "start-date",
        type: "date",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.startDate = n),
        "aria-label": "Select start date"
      }, null, 512), [
        [H, t.startDate]
      ]),
      e[7] || (e[7] = f("label", { for: "end-date" }, "End Date:", -1)),
      R(f("input", {
        id: "end-date",
        type: "date",
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.endDate = n),
        "aria-label": "Select end date"
      }, null, 512), [
        [H, t.endDate]
      ])
    ]),
    f("button", {
      onClick: e[3] || (e[3] = (...n) => t.setRecurrence && t.setRecurrence(...n)),
      "aria-label": "Set recurrence"
    }, "Set Recurrence"),
    t.feedbackMessage ? (d(), c("div", Mb, w(t.feedbackMessage), 1)) : P("", !0)
  ]);
}
const V4 = /* @__PURE__ */ A(Db, [["render", Fb], ["__scopeId", "data-v-29126a52"]]);
var po = typeof global == "object" && global && global.Object === Object && global, Ub = typeof self == "object" && self && self.Object === Object && self, et = po || Ub || Function("return this")(), $t = et.Symbol, ho = Object.prototype, jb = ho.hasOwnProperty, Vb = ho.toString, Os = $t ? $t.toStringTag : void 0;
function Hb(t) {
  var e = jb.call(t, Os), s = t[Os];
  try {
    t[Os] = void 0;
    var r = !0;
  } catch {
  }
  var i = Vb.call(t);
  return r && (e ? t[Os] = s : delete t[Os]), i;
}
var zb = Object.prototype, Gb = zb.toString;
function Kb(t) {
  return Gb.call(t);
}
var Wb = "[object Null]", Zb = "[object Undefined]", oa = $t ? $t.toStringTag : void 0;
function ps(t) {
  return t == null ? t === void 0 ? Zb : Wb : oa && oa in Object(t) ? Hb(t) : Kb(t);
}
function ot(t) {
  return t != null && typeof t == "object";
}
var qt = Array.isArray;
function kt(t) {
  var e = typeof t;
  return t != null && (e == "object" || e == "function");
}
function go(t) {
  return t;
}
var Xb = "[object AsyncFunction]", Yb = "[object Function]", Qb = "[object GeneratorFunction]", Jb = "[object Proxy]";
function Bi(t) {
  if (!kt(t))
    return !1;
  var e = ps(t);
  return e == Yb || e == Qb || e == Xb || e == Jb;
}
var Xr = et["__core-js_shared__"], la = function() {
  var t = /[^.]+$/.exec(Xr && Xr.keys && Xr.keys.IE_PROTO || "");
  return t ? "Symbol(src)_1." + t : "";
}();
function xb(t) {
  return !!la && la in t;
}
var e0 = Function.prototype, t0 = e0.toString;
function Dt(t) {
  if (t != null) {
    try {
      return t0.call(t);
    } catch {
    }
    try {
      return t + "";
    } catch {
    }
  }
  return "";
}
var s0 = /[\\^$.*+?()[\]{}|]/g, n0 = /^\[object .+?Constructor\]$/, r0 = Function.prototype, i0 = Object.prototype, a0 = r0.toString, o0 = i0.hasOwnProperty, l0 = RegExp(
  "^" + a0.call(o0).replace(s0, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
);
function u0(t) {
  if (!kt(t) || xb(t))
    return !1;
  var e = Bi(t) ? l0 : n0;
  return e.test(Dt(t));
}
function d0(t, e) {
  return t == null ? void 0 : t[e];
}
function Rt(t, e) {
  var s = d0(t, e);
  return u0(s) ? s : void 0;
}
var ui = Rt(et, "WeakMap"), ua = Object.create, c0 = /* @__PURE__ */ function() {
  function t() {
  }
  return function(e) {
    if (!kt(e))
      return {};
    if (ua)
      return ua(e);
    t.prototype = e;
    var s = new t();
    return t.prototype = void 0, s;
  };
}();
function f0(t, e, s) {
  switch (s.length) {
    case 0:
      return t.call(e);
    case 1:
      return t.call(e, s[0]);
    case 2:
      return t.call(e, s[0], s[1]);
    case 3:
      return t.call(e, s[0], s[1], s[2]);
  }
  return t.apply(e, s);
}
function p0(t, e) {
  var s = -1, r = t.length;
  for (e || (e = Array(r)); ++s < r; )
    e[s] = t[s];
  return e;
}
var h0 = 800, g0 = 16, m0 = Date.now;
function v0(t) {
  var e = 0, s = 0;
  return function() {
    var r = m0(), i = g0 - (r - s);
    if (s = r, i > 0) {
      if (++e >= h0)
        return arguments[0];
    } else
      e = 0;
    return t.apply(void 0, arguments);
  };
}
function b0(t) {
  return function() {
    return t;
  };
}
var Mn = function() {
  try {
    var t = Rt(Object, "defineProperty");
    return t({}, "", {}), t;
  } catch {
  }
}(), y0 = Mn ? function(t, e) {
  return Mn(t, "toString", {
    configurable: !0,
    enumerable: !1,
    value: b0(e),
    writable: !0
  });
} : go, $0 = v0(y0);
function k0(t, e) {
  for (var s = -1, r = t == null ? 0 : t.length; ++s < r && e(t[s], s, t) !== !1; )
    ;
  return t;
}
var w0 = 9007199254740991, C0 = /^(?:0|[1-9]\d*)$/;
function mo(t, e) {
  var s = typeof t;
  return e = e ?? w0, !!e && (s == "number" || s != "symbol" && C0.test(t)) && t > -1 && t % 1 == 0 && t < e;
}
function Mi(t, e, s) {
  e == "__proto__" && Mn ? Mn(t, e, {
    configurable: !0,
    enumerable: !0,
    value: s,
    writable: !0
  }) : t[e] = s;
}
function Ys(t, e) {
  return t === e || t !== t && e !== e;
}
var A0 = Object.prototype, E0 = A0.hasOwnProperty;
function vo(t, e, s) {
  var r = t[e];
  (!(E0.call(t, e) && Ys(r, s)) || s === void 0 && !(e in t)) && Mi(t, e, s);
}
function S0(t, e, s, r) {
  var i = !s;
  s || (s = {});
  for (var a = -1, n = e.length; ++a < n; ) {
    var o = e[a], u = void 0;
    u === void 0 && (u = t[o]), i ? Mi(s, o, u) : vo(s, o, u);
  }
  return s;
}
var da = Math.max;
function T0(t, e, s) {
  return e = da(e === void 0 ? t.length - 1 : e, 0), function() {
    for (var r = arguments, i = -1, a = da(r.length - e, 0), n = Array(a); ++i < a; )
      n[i] = r[e + i];
    i = -1;
    for (var o = Array(e + 1); ++i < e; )
      o[i] = r[i];
    return o[e] = s(n), f0(t, this, o);
  };
}
function _0(t, e) {
  return $0(T0(t, e, go), t + "");
}
var N0 = 9007199254740991;
function bo(t) {
  return typeof t == "number" && t > -1 && t % 1 == 0 && t <= N0;
}
function zn(t) {
  return t != null && bo(t.length) && !Bi(t);
}
function I0(t, e, s) {
  if (!kt(s))
    return !1;
  var r = typeof e;
  return (r == "number" ? zn(s) && mo(e, s.length) : r == "string" && e in s) ? Ys(s[e], t) : !1;
}
function L0(t) {
  return _0(function(e, s) {
    var r = -1, i = s.length, a = i > 1 ? s[i - 1] : void 0, n = i > 2 ? s[2] : void 0;
    for (a = t.length > 3 && typeof a == "function" ? (i--, a) : void 0, n && I0(s[0], s[1], n) && (a = i < 3 ? void 0 : a, i = 1), e = Object(e); ++r < i; ) {
      var o = s[r];
      o && t(e, o, r, a);
    }
    return e;
  });
}
var q0 = Object.prototype;
function Fi(t) {
  var e = t && t.constructor, s = typeof e == "function" && e.prototype || q0;
  return t === s;
}
function O0(t, e) {
  for (var s = -1, r = Array(t); ++s < t; )
    r[s] = e(s);
  return r;
}
var P0 = "[object Arguments]";
function ca(t) {
  return ot(t) && ps(t) == P0;
}
var yo = Object.prototype, D0 = yo.hasOwnProperty, R0 = yo.propertyIsEnumerable, di = ca(/* @__PURE__ */ function() {
  return arguments;
}()) ? ca : function(t) {
  return ot(t) && D0.call(t, "callee") && !R0.call(t, "callee");
};
function B0() {
  return !1;
}
var $o = typeof exports == "object" && exports && !exports.nodeType && exports, fa = $o && typeof module == "object" && module && !module.nodeType && module, M0 = fa && fa.exports === $o, pa = M0 ? et.Buffer : void 0, F0 = pa ? pa.isBuffer : void 0, Vs = F0 || B0, U0 = "[object Arguments]", j0 = "[object Array]", V0 = "[object Boolean]", H0 = "[object Date]", z0 = "[object Error]", G0 = "[object Function]", K0 = "[object Map]", W0 = "[object Number]", Z0 = "[object Object]", X0 = "[object RegExp]", Y0 = "[object Set]", Q0 = "[object String]", J0 = "[object WeakMap]", x0 = "[object ArrayBuffer]", ey = "[object DataView]", ty = "[object Float32Array]", sy = "[object Float64Array]", ny = "[object Int8Array]", ry = "[object Int16Array]", iy = "[object Int32Array]", ay = "[object Uint8Array]", oy = "[object Uint8ClampedArray]", ly = "[object Uint16Array]", uy = "[object Uint32Array]", se = {};
se[ty] = se[sy] = se[ny] = se[ry] = se[iy] = se[ay] = se[oy] = se[ly] = se[uy] = !0;
se[U0] = se[j0] = se[x0] = se[V0] = se[ey] = se[H0] = se[z0] = se[G0] = se[K0] = se[W0] = se[Z0] = se[X0] = se[Y0] = se[Q0] = se[J0] = !1;
function dy(t) {
  return ot(t) && bo(t.length) && !!se[ps(t)];
}
function Ui(t) {
  return function(e) {
    return t(e);
  };
}
var ko = typeof exports == "object" && exports && !exports.nodeType && exports, Ms = ko && typeof module == "object" && module && !module.nodeType && module, cy = Ms && Ms.exports === ko, Yr = cy && po.process, os = function() {
  try {
    var t = Ms && Ms.require && Ms.require("util").types;
    return t || Yr && Yr.binding && Yr.binding("util");
  } catch {
  }
}(), ha = os && os.isTypedArray, ji = ha ? Ui(ha) : dy, fy = Object.prototype, py = fy.hasOwnProperty;
function wo(t, e) {
  var s = qt(t), r = !s && di(t), i = !s && !r && Vs(t), a = !s && !r && !i && ji(t), n = s || r || i || a, o = n ? O0(t.length, String) : [], u = o.length;
  for (var p in t)
    (e || py.call(t, p)) && !(n && // Safari 9 has enumerable `arguments.length` in strict mode.
    (p == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    i && (p == "offset" || p == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    a && (p == "buffer" || p == "byteLength" || p == "byteOffset") || // Skip index properties.
    mo(p, u))) && o.push(p);
  return o;
}
function Co(t, e) {
  return function(s) {
    return t(e(s));
  };
}
var hy = Co(Object.keys, Object), gy = Object.prototype, my = gy.hasOwnProperty;
function vy(t) {
  if (!Fi(t))
    return hy(t);
  var e = [];
  for (var s in Object(t))
    my.call(t, s) && s != "constructor" && e.push(s);
  return e;
}
function by(t) {
  return zn(t) ? wo(t) : vy(t);
}
function yy(t) {
  var e = [];
  if (t != null)
    for (var s in Object(t))
      e.push(s);
  return e;
}
var $y = Object.prototype, ky = $y.hasOwnProperty;
function wy(t) {
  if (!kt(t))
    return yy(t);
  var e = Fi(t), s = [];
  for (var r in t)
    r == "constructor" && (e || !ky.call(t, r)) || s.push(r);
  return s;
}
function Ao(t) {
  return zn(t) ? wo(t, !0) : wy(t);
}
var Hs = Rt(Object, "create");
function Cy() {
  this.__data__ = Hs ? Hs(null) : {}, this.size = 0;
}
function Ay(t) {
  var e = this.has(t) && delete this.__data__[t];
  return this.size -= e ? 1 : 0, e;
}
var Ey = "__lodash_hash_undefined__", Sy = Object.prototype, Ty = Sy.hasOwnProperty;
function _y(t) {
  var e = this.__data__;
  if (Hs) {
    var s = e[t];
    return s === Ey ? void 0 : s;
  }
  return Ty.call(e, t) ? e[t] : void 0;
}
var Ny = Object.prototype, Iy = Ny.hasOwnProperty;
function Ly(t) {
  var e = this.__data__;
  return Hs ? e[t] !== void 0 : Iy.call(e, t);
}
var qy = "__lodash_hash_undefined__";
function Oy(t, e) {
  var s = this.__data__;
  return this.size += this.has(t) ? 0 : 1, s[t] = Hs && e === void 0 ? qy : e, this;
}
function Ot(t) {
  var e = -1, s = t == null ? 0 : t.length;
  for (this.clear(); ++e < s; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
Ot.prototype.clear = Cy;
Ot.prototype.delete = Ay;
Ot.prototype.get = _y;
Ot.prototype.has = Ly;
Ot.prototype.set = Oy;
function Py() {
  this.__data__ = [], this.size = 0;
}
function Gn(t, e) {
  for (var s = t.length; s--; )
    if (Ys(t[s][0], e))
      return s;
  return -1;
}
var Dy = Array.prototype, Ry = Dy.splice;
function By(t) {
  var e = this.__data__, s = Gn(e, t);
  if (s < 0)
    return !1;
  var r = e.length - 1;
  return s == r ? e.pop() : Ry.call(e, s, 1), --this.size, !0;
}
function My(t) {
  var e = this.__data__, s = Gn(e, t);
  return s < 0 ? void 0 : e[s][1];
}
function Fy(t) {
  return Gn(this.__data__, t) > -1;
}
function Uy(t, e) {
  var s = this.__data__, r = Gn(s, t);
  return r < 0 ? (++this.size, s.push([t, e])) : s[r][1] = e, this;
}
function dt(t) {
  var e = -1, s = t == null ? 0 : t.length;
  for (this.clear(); ++e < s; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
dt.prototype.clear = Py;
dt.prototype.delete = By;
dt.prototype.get = My;
dt.prototype.has = Fy;
dt.prototype.set = Uy;
var zs = Rt(et, "Map");
function jy() {
  this.size = 0, this.__data__ = {
    hash: new Ot(),
    map: new (zs || dt)(),
    string: new Ot()
  };
}
function Vy(t) {
  var e = typeof t;
  return e == "string" || e == "number" || e == "symbol" || e == "boolean" ? t !== "__proto__" : t === null;
}
function Kn(t, e) {
  var s = t.__data__;
  return Vy(e) ? s[typeof e == "string" ? "string" : "hash"] : s.map;
}
function Hy(t) {
  var e = Kn(this, t).delete(t);
  return this.size -= e ? 1 : 0, e;
}
function zy(t) {
  return Kn(this, t).get(t);
}
function Gy(t) {
  return Kn(this, t).has(t);
}
function Ky(t, e) {
  var s = Kn(this, t), r = s.size;
  return s.set(t, e), this.size += s.size == r ? 0 : 1, this;
}
function Bt(t) {
  var e = -1, s = t == null ? 0 : t.length;
  for (this.clear(); ++e < s; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
Bt.prototype.clear = jy;
Bt.prototype.delete = Hy;
Bt.prototype.get = zy;
Bt.prototype.has = Gy;
Bt.prototype.set = Ky;
function Wy(t, e) {
  for (var s = -1, r = e.length, i = t.length; ++s < r; )
    t[i + s] = e[s];
  return t;
}
var Eo = Co(Object.getPrototypeOf, Object), Zy = "[object Object]", Xy = Function.prototype, Yy = Object.prototype, So = Xy.toString, Qy = Yy.hasOwnProperty, Jy = So.call(Object);
function xy(t) {
  if (!ot(t) || ps(t) != Zy)
    return !1;
  var e = Eo(t);
  if (e === null)
    return !0;
  var s = Qy.call(e, "constructor") && e.constructor;
  return typeof s == "function" && s instanceof s && So.call(s) == Jy;
}
function e$() {
  this.__data__ = new dt(), this.size = 0;
}
function t$(t) {
  var e = this.__data__, s = e.delete(t);
  return this.size = e.size, s;
}
function s$(t) {
  return this.__data__.get(t);
}
function n$(t) {
  return this.__data__.has(t);
}
var r$ = 200;
function i$(t, e) {
  var s = this.__data__;
  if (s instanceof dt) {
    var r = s.__data__;
    if (!zs || r.length < r$ - 1)
      return r.push([t, e]), this.size = ++s.size, this;
    s = this.__data__ = new Bt(r);
  }
  return s.set(t, e), this.size = s.size, this;
}
function Ye(t) {
  var e = this.__data__ = new dt(t);
  this.size = e.size;
}
Ye.prototype.clear = e$;
Ye.prototype.delete = t$;
Ye.prototype.get = s$;
Ye.prototype.has = n$;
Ye.prototype.set = i$;
var To = typeof exports == "object" && exports && !exports.nodeType && exports, ga = To && typeof module == "object" && module && !module.nodeType && module, a$ = ga && ga.exports === To, ma = a$ ? et.Buffer : void 0, va = ma ? ma.allocUnsafe : void 0;
function _o(t, e) {
  if (e)
    return t.slice();
  var s = t.length, r = va ? va(s) : new t.constructor(s);
  return t.copy(r), r;
}
function o$(t, e) {
  for (var s = -1, r = t == null ? 0 : t.length, i = 0, a = []; ++s < r; ) {
    var n = t[s];
    e(n, s, t) && (a[i++] = n);
  }
  return a;
}
function l$() {
  return [];
}
var u$ = Object.prototype, d$ = u$.propertyIsEnumerable, ba = Object.getOwnPropertySymbols, c$ = ba ? function(t) {
  return t == null ? [] : (t = Object(t), o$(ba(t), function(e) {
    return d$.call(t, e);
  }));
} : l$;
function f$(t, e, s) {
  var r = e(t);
  return qt(t) ? r : Wy(r, s(t));
}
function ci(t) {
  return f$(t, by, c$);
}
var fi = Rt(et, "DataView"), pi = Rt(et, "Promise"), hi = Rt(et, "Set"), ya = "[object Map]", p$ = "[object Object]", $a = "[object Promise]", ka = "[object Set]", wa = "[object WeakMap]", Ca = "[object DataView]", h$ = Dt(fi), g$ = Dt(zs), m$ = Dt(pi), v$ = Dt(hi), b$ = Dt(ui), Be = ps;
(fi && Be(new fi(new ArrayBuffer(1))) != Ca || zs && Be(new zs()) != ya || pi && Be(pi.resolve()) != $a || hi && Be(new hi()) != ka || ui && Be(new ui()) != wa) && (Be = function(t) {
  var e = ps(t), s = e == p$ ? t.constructor : void 0, r = s ? Dt(s) : "";
  if (r)
    switch (r) {
      case h$:
        return Ca;
      case g$:
        return ya;
      case m$:
        return $a;
      case v$:
        return ka;
      case b$:
        return wa;
    }
  return e;
});
var y$ = Object.prototype, $$ = y$.hasOwnProperty;
function k$(t) {
  var e = t.length, s = new t.constructor(e);
  return e && typeof t[0] == "string" && $$.call(t, "index") && (s.index = t.index, s.input = t.input), s;
}
var Fn = et.Uint8Array;
function Vi(t) {
  var e = new t.constructor(t.byteLength);
  return new Fn(e).set(new Fn(t)), e;
}
function w$(t, e) {
  var s = Vi(t.buffer);
  return new t.constructor(s, t.byteOffset, t.byteLength);
}
var C$ = /\w*$/;
function A$(t) {
  var e = new t.constructor(t.source, C$.exec(t));
  return e.lastIndex = t.lastIndex, e;
}
var Aa = $t ? $t.prototype : void 0, Ea = Aa ? Aa.valueOf : void 0;
function E$(t) {
  return Ea ? Object(Ea.call(t)) : {};
}
function No(t, e) {
  var s = e ? Vi(t.buffer) : t.buffer;
  return new t.constructor(s, t.byteOffset, t.length);
}
var S$ = "[object Boolean]", T$ = "[object Date]", _$ = "[object Map]", N$ = "[object Number]", I$ = "[object RegExp]", L$ = "[object Set]", q$ = "[object String]", O$ = "[object Symbol]", P$ = "[object ArrayBuffer]", D$ = "[object DataView]", R$ = "[object Float32Array]", B$ = "[object Float64Array]", M$ = "[object Int8Array]", F$ = "[object Int16Array]", U$ = "[object Int32Array]", j$ = "[object Uint8Array]", V$ = "[object Uint8ClampedArray]", H$ = "[object Uint16Array]", z$ = "[object Uint32Array]";
function G$(t, e, s) {
  var r = t.constructor;
  switch (e) {
    case P$:
      return Vi(t);
    case S$:
    case T$:
      return new r(+t);
    case D$:
      return w$(t);
    case R$:
    case B$:
    case M$:
    case F$:
    case U$:
    case j$:
    case V$:
    case H$:
    case z$:
      return No(t, s);
    case _$:
      return new r();
    case N$:
    case q$:
      return new r(t);
    case I$:
      return A$(t);
    case L$:
      return new r();
    case O$:
      return E$(t);
  }
}
function Io(t) {
  return typeof t.constructor == "function" && !Fi(t) ? c0(Eo(t)) : {};
}
var K$ = "[object Map]";
function W$(t) {
  return ot(t) && Be(t) == K$;
}
var Sa = os && os.isMap, Z$ = Sa ? Ui(Sa) : W$, X$ = "[object Set]";
function Y$(t) {
  return ot(t) && Be(t) == X$;
}
var Ta = os && os.isSet, Q$ = Ta ? Ui(Ta) : Y$, J$ = 1, Lo = "[object Arguments]", x$ = "[object Array]", e2 = "[object Boolean]", t2 = "[object Date]", s2 = "[object Error]", qo = "[object Function]", n2 = "[object GeneratorFunction]", r2 = "[object Map]", i2 = "[object Number]", Oo = "[object Object]", a2 = "[object RegExp]", o2 = "[object Set]", l2 = "[object String]", u2 = "[object Symbol]", d2 = "[object WeakMap]", c2 = "[object ArrayBuffer]", f2 = "[object DataView]", p2 = "[object Float32Array]", h2 = "[object Float64Array]", g2 = "[object Int8Array]", m2 = "[object Int16Array]", v2 = "[object Int32Array]", b2 = "[object Uint8Array]", y2 = "[object Uint8ClampedArray]", $2 = "[object Uint16Array]", k2 = "[object Uint32Array]", ee = {};
ee[Lo] = ee[x$] = ee[c2] = ee[f2] = ee[e2] = ee[t2] = ee[p2] = ee[h2] = ee[g2] = ee[m2] = ee[v2] = ee[r2] = ee[i2] = ee[Oo] = ee[a2] = ee[o2] = ee[l2] = ee[u2] = ee[b2] = ee[y2] = ee[$2] = ee[k2] = !0;
ee[s2] = ee[qo] = ee[d2] = !1;
function Rn(t, e, s, r, i, a) {
  var n, o = e & J$;
  if (n !== void 0)
    return n;
  if (!kt(t))
    return t;
  var u = qt(t);
  if (u)
    n = k$(t);
  else {
    var p = Be(t), g = p == qo || p == n2;
    if (Vs(t))
      return _o(t, o);
    if (p == Oo || p == Lo || g && !i)
      n = g ? {} : Io(t);
    else {
      if (!ee[p])
        return i ? t : {};
      n = G$(t, p, o);
    }
  }
  a || (a = new Ye());
  var k = a.get(t);
  if (k)
    return k;
  a.set(t, n), Q$(t) ? t.forEach(function(v) {
    n.add(Rn(v, e, s, v, t, a));
  }) : Z$(t) && t.forEach(function(v, E) {
    n.set(E, Rn(v, e, s, E, t, a));
  });
  var y = ci, b = u ? void 0 : y(t);
  return k0(b || t, function(v, E) {
    b && (E = v, v = t[E]), vo(n, E, Rn(v, e, s, E, t, a));
  }), n;
}
var w2 = 1, C2 = 4;
function rs(t) {
  return Rn(t, w2 | C2);
}
var A2 = "__lodash_hash_undefined__";
function E2(t) {
  return this.__data__.set(t, A2), this;
}
function S2(t) {
  return this.__data__.has(t);
}
function Un(t) {
  var e = -1, s = t == null ? 0 : t.length;
  for (this.__data__ = new Bt(); ++e < s; )
    this.add(t[e]);
}
Un.prototype.add = Un.prototype.push = E2;
Un.prototype.has = S2;
function T2(t, e) {
  for (var s = -1, r = t == null ? 0 : t.length; ++s < r; )
    if (e(t[s], s, t))
      return !0;
  return !1;
}
function _2(t, e) {
  return t.has(e);
}
var N2 = 1, I2 = 2;
function Po(t, e, s, r, i, a) {
  var n = s & N2, o = t.length, u = e.length;
  if (o != u && !(n && u > o))
    return !1;
  var p = a.get(t), g = a.get(e);
  if (p && g)
    return p == e && g == t;
  var k = -1, y = !0, b = s & I2 ? new Un() : void 0;
  for (a.set(t, e), a.set(e, t); ++k < o; ) {
    var v = t[k], E = e[k];
    if (r)
      var S = n ? r(E, v, k, e, t, a) : r(v, E, k, t, e, a);
    if (S !== void 0) {
      if (S)
        continue;
      y = !1;
      break;
    }
    if (b) {
      if (!T2(e, function(_, O) {
        if (!_2(b, O) && (v === _ || i(v, _, s, r, a)))
          return b.push(O);
      })) {
        y = !1;
        break;
      }
    } else if (!(v === E || i(v, E, s, r, a))) {
      y = !1;
      break;
    }
  }
  return a.delete(t), a.delete(e), y;
}
function L2(t) {
  var e = -1, s = Array(t.size);
  return t.forEach(function(r, i) {
    s[++e] = [i, r];
  }), s;
}
function q2(t) {
  var e = -1, s = Array(t.size);
  return t.forEach(function(r) {
    s[++e] = r;
  }), s;
}
var O2 = 1, P2 = 2, D2 = "[object Boolean]", R2 = "[object Date]", B2 = "[object Error]", M2 = "[object Map]", F2 = "[object Number]", U2 = "[object RegExp]", j2 = "[object Set]", V2 = "[object String]", H2 = "[object Symbol]", z2 = "[object ArrayBuffer]", G2 = "[object DataView]", _a = $t ? $t.prototype : void 0, Qr = _a ? _a.valueOf : void 0;
function K2(t, e, s, r, i, a, n) {
  switch (s) {
    case G2:
      if (t.byteLength != e.byteLength || t.byteOffset != e.byteOffset)
        return !1;
      t = t.buffer, e = e.buffer;
    case z2:
      return !(t.byteLength != e.byteLength || !a(new Fn(t), new Fn(e)));
    case D2:
    case R2:
    case F2:
      return Ys(+t, +e);
    case B2:
      return t.name == e.name && t.message == e.message;
    case U2:
    case V2:
      return t == e + "";
    case M2:
      var o = L2;
    case j2:
      var u = r & O2;
      if (o || (o = q2), t.size != e.size && !u)
        return !1;
      var p = n.get(t);
      if (p)
        return p == e;
      r |= P2, n.set(t, e);
      var g = Po(o(t), o(e), r, i, a, n);
      return n.delete(t), g;
    case H2:
      if (Qr)
        return Qr.call(t) == Qr.call(e);
  }
  return !1;
}
var W2 = 1, Z2 = Object.prototype, X2 = Z2.hasOwnProperty;
function Y2(t, e, s, r, i, a) {
  var n = s & W2, o = ci(t), u = o.length, p = ci(e), g = p.length;
  if (u != g && !n)
    return !1;
  for (var k = u; k--; ) {
    var y = o[k];
    if (!(n ? y in e : X2.call(e, y)))
      return !1;
  }
  var b = a.get(t), v = a.get(e);
  if (b && v)
    return b == e && v == t;
  var E = !0;
  a.set(t, e), a.set(e, t);
  for (var S = n; ++k < u; ) {
    y = o[k];
    var _ = t[y], O = e[y];
    if (r)
      var D = n ? r(O, _, y, e, t, a) : r(_, O, y, t, e, a);
    if (!(D === void 0 ? _ === O || i(_, O, s, r, a) : D)) {
      E = !1;
      break;
    }
    S || (S = y == "constructor");
  }
  if (E && !S) {
    var U = t.constructor, M = e.constructor;
    U != M && "constructor" in t && "constructor" in e && !(typeof U == "function" && U instanceof U && typeof M == "function" && M instanceof M) && (E = !1);
  }
  return a.delete(t), a.delete(e), E;
}
var Q2 = 1, Na = "[object Arguments]", Ia = "[object Array]", In = "[object Object]", J2 = Object.prototype, La = J2.hasOwnProperty;
function x2(t, e, s, r, i, a) {
  var n = qt(t), o = qt(e), u = n ? Ia : Be(t), p = o ? Ia : Be(e);
  u = u == Na ? In : u, p = p == Na ? In : p;
  var g = u == In, k = p == In, y = u == p;
  if (y && Vs(t)) {
    if (!Vs(e))
      return !1;
    n = !0, g = !1;
  }
  if (y && !g)
    return a || (a = new Ye()), n || ji(t) ? Po(t, e, s, r, i, a) : K2(t, e, u, s, r, i, a);
  if (!(s & Q2)) {
    var b = g && La.call(t, "__wrapped__"), v = k && La.call(e, "__wrapped__");
    if (b || v) {
      var E = b ? t.value() : t, S = v ? e.value() : e;
      return a || (a = new Ye()), i(E, S, s, r, a);
    }
  }
  return y ? (a || (a = new Ye()), Y2(t, e, s, r, i, a)) : !1;
}
function Do(t, e, s, r, i) {
  return t === e ? !0 : t == null || e == null || !ot(t) && !ot(e) ? t !== t && e !== e : x2(t, e, s, r, Do, i);
}
function ek(t) {
  return function(e, s, r) {
    for (var i = -1, a = Object(e), n = r(e), o = n.length; o--; ) {
      var u = n[++i];
      if (s(a[u], u, a) === !1)
        break;
    }
    return e;
  };
}
var tk = ek();
function gi(t, e, s) {
  (s !== void 0 && !Ys(t[e], s) || s === void 0 && !(e in t)) && Mi(t, e, s);
}
function sk(t) {
  return ot(t) && zn(t);
}
function mi(t, e) {
  if (!(e === "constructor" && typeof t[e] == "function") && e != "__proto__")
    return t[e];
}
function nk(t) {
  return S0(t, Ao(t));
}
function rk(t, e, s, r, i, a, n) {
  var o = mi(t, s), u = mi(e, s), p = n.get(u);
  if (p) {
    gi(t, s, p);
    return;
  }
  var g = a ? a(o, u, s + "", t, e, n) : void 0, k = g === void 0;
  if (k) {
    var y = qt(u), b = !y && Vs(u), v = !y && !b && ji(u);
    g = u, y || b || v ? qt(o) ? g = o : sk(o) ? g = p0(o) : b ? (k = !1, g = _o(u, !0)) : v ? (k = !1, g = No(u, !0)) : g = [] : xy(u) || di(u) ? (g = o, di(o) ? g = nk(o) : (!kt(o) || Bi(o)) && (g = Io(u))) : k = !1;
  }
  k && (n.set(u, g), i(g, u, r, a, n), n.delete(u)), gi(t, s, g);
}
function Ro(t, e, s, r, i) {
  t !== e && tk(e, function(a, n) {
    if (i || (i = new Ye()), kt(a))
      rk(t, e, n, s, Ro, r, i);
    else {
      var o = r ? r(mi(t, n), a, n + "", t, e, i) : void 0;
      o === void 0 && (o = a), gi(t, n, o);
    }
  }, Ao);
}
function Hi(t, e) {
  return Do(t, e);
}
var yt = L0(function(t, e, s) {
  Ro(t, e, s);
}), V = /* @__PURE__ */ ((t) => (t[t.TYPE = 3] = "TYPE", t[t.LEVEL = 12] = "LEVEL", t[t.ATTRIBUTE = 13] = "ATTRIBUTE", t[t.BLOT = 14] = "BLOT", t[t.INLINE = 7] = "INLINE", t[t.BLOCK = 11] = "BLOCK", t[t.BLOCK_BLOT = 10] = "BLOCK_BLOT", t[t.INLINE_BLOT = 6] = "INLINE_BLOT", t[t.BLOCK_ATTRIBUTE = 9] = "BLOCK_ATTRIBUTE", t[t.INLINE_ATTRIBUTE = 5] = "INLINE_ATTRIBUTE", t[t.ANY = 15] = "ANY", t))(V || {});
class Je {
  constructor(e, s, r = {}) {
    this.attrName = e, this.keyName = s;
    const i = V.TYPE & V.ATTRIBUTE;
    this.scope = r.scope != null ? (
      // Ignore type bits, force attribute bit
      r.scope & V.LEVEL | i
    ) : V.ATTRIBUTE, r.whitelist != null && (this.whitelist = r.whitelist);
  }
  static keys(e) {
    return Array.from(e.attributes).map((s) => s.name);
  }
  add(e, s) {
    return this.canAdd(e, s) ? (e.setAttribute(this.keyName, s), !0) : !1;
  }
  canAdd(e, s) {
    return this.whitelist == null ? !0 : typeof s == "string" ? this.whitelist.indexOf(s.replace(/["']/g, "")) > -1 : this.whitelist.indexOf(s) > -1;
  }
  remove(e) {
    e.removeAttribute(this.keyName);
  }
  value(e) {
    const s = e.getAttribute(this.keyName);
    return this.canAdd(e, s) && s ? s : "";
  }
}
class is extends Error {
  constructor(e) {
    e = "[Parchment] " + e, super(e), this.message = e, this.name = this.constructor.name;
  }
}
const Bo = class vi {
  constructor() {
    this.attributes = {}, this.classes = {}, this.tags = {}, this.types = {};
  }
  static find(e, s = !1) {
    if (e == null)
      return null;
    if (this.blots.has(e))
      return this.blots.get(e) || null;
    if (s) {
      let r = null;
      try {
        r = e.parentNode;
      } catch {
        return null;
      }
      return this.find(r, s);
    }
    return null;
  }
  create(e, s, r) {
    const i = this.query(s);
    if (i == null)
      throw new is(`Unable to create ${s} blot`);
    const a = i, n = (
      // @ts-expect-error Fix me later
      s instanceof Node || s.nodeType === Node.TEXT_NODE ? s : a.create(r)
    ), o = new a(e, n, r);
    return vi.blots.set(o.domNode, o), o;
  }
  find(e, s = !1) {
    return vi.find(e, s);
  }
  query(e, s = V.ANY) {
    let r;
    return typeof e == "string" ? r = this.types[e] || this.attributes[e] : e instanceof Text || e.nodeType === Node.TEXT_NODE ? r = this.types.text : typeof e == "number" ? e & V.LEVEL & V.BLOCK ? r = this.types.block : e & V.LEVEL & V.INLINE && (r = this.types.inline) : e instanceof Element && ((e.getAttribute("class") || "").split(/\s+/).some((i) => (r = this.classes[i], !!r)), r = r || this.tags[e.tagName]), r == null ? null : "scope" in r && s & V.LEVEL & r.scope && s & V.TYPE & r.scope ? r : null;
  }
  register(...e) {
    return e.map((s) => {
      const r = "blotName" in s, i = "attrName" in s;
      if (!r && !i)
        throw new is("Invalid definition");
      if (r && s.blotName === "abstract")
        throw new is("Cannot register abstract class");
      const a = r ? s.blotName : i ? s.attrName : void 0;
      return this.types[a] = s, i ? typeof s.keyName == "string" && (this.attributes[s.keyName] = s) : r && (s.className && (this.classes[s.className] = s), s.tagName && (Array.isArray(s.tagName) ? s.tagName = s.tagName.map((n) => n.toUpperCase()) : s.tagName = s.tagName.toUpperCase(), (Array.isArray(s.tagName) ? s.tagName : [s.tagName]).forEach((n) => {
        (this.tags[n] == null || s.className == null) && (this.tags[n] = s);
      }))), s;
    });
  }
};
Bo.blots = /* @__PURE__ */ new WeakMap();
let ls = Bo;
function qa(t, e) {
  return (t.getAttribute("class") || "").split(/\s+/).filter((s) => s.indexOf(`${e}-`) === 0);
}
class ik extends Je {
  static keys(e) {
    return (e.getAttribute("class") || "").split(/\s+/).map((s) => s.split("-").slice(0, -1).join("-"));
  }
  add(e, s) {
    return this.canAdd(e, s) ? (this.remove(e), e.classList.add(`${this.keyName}-${s}`), !0) : !1;
  }
  remove(e) {
    qa(e, this.keyName).forEach((s) => {
      e.classList.remove(s);
    }), e.classList.length === 0 && e.removeAttribute("class");
  }
  value(e) {
    const s = (qa(e, this.keyName)[0] || "").slice(this.keyName.length + 1);
    return this.canAdd(e, s) ? s : "";
  }
}
const Ve = ik;
function Jr(t) {
  const e = t.split("-"), s = e.slice(1).map((r) => r[0].toUpperCase() + r.slice(1)).join("");
  return e[0] + s;
}
class ak extends Je {
  static keys(e) {
    return (e.getAttribute("style") || "").split(";").map((s) => s.split(":")[0].trim());
  }
  add(e, s) {
    return this.canAdd(e, s) ? (e.style[Jr(this.keyName)] = s, !0) : !1;
  }
  remove(e) {
    e.style[Jr(this.keyName)] = "", e.getAttribute("style") || e.removeAttribute("style");
  }
  value(e) {
    const s = e.style[Jr(this.keyName)];
    return this.canAdd(e, s) ? s : "";
  }
}
const wt = ak;
class ok {
  constructor(e) {
    this.attributes = {}, this.domNode = e, this.build();
  }
  attribute(e, s) {
    s ? e.add(this.domNode, s) && (e.value(this.domNode) != null ? this.attributes[e.attrName] = e : delete this.attributes[e.attrName]) : (e.remove(this.domNode), delete this.attributes[e.attrName]);
  }
  build() {
    this.attributes = {};
    const e = ls.find(this.domNode);
    if (e == null)
      return;
    const s = Je.keys(this.domNode), r = Ve.keys(this.domNode), i = wt.keys(this.domNode);
    s.concat(r).concat(i).forEach((a) => {
      const n = e.scroll.query(a, V.ATTRIBUTE);
      n instanceof Je && (this.attributes[n.attrName] = n);
    });
  }
  copy(e) {
    Object.keys(this.attributes).forEach((s) => {
      const r = this.attributes[s].value(this.domNode);
      e.format(s, r);
    });
  }
  move(e) {
    this.copy(e), Object.keys(this.attributes).forEach((s) => {
      this.attributes[s].remove(this.domNode);
    }), this.attributes = {};
  }
  values() {
    return Object.keys(this.attributes).reduce(
      (e, s) => (e[s] = this.attributes[s].value(this.domNode), e),
      {}
    );
  }
}
const Wn = ok, Mo = class {
  constructor(e, s) {
    this.scroll = e, this.domNode = s, ls.blots.set(s, this), this.prev = null, this.next = null;
  }
  static create(e) {
    if (this.tagName == null)
      throw new is("Blot definition missing tagName");
    let s, r;
    return Array.isArray(this.tagName) ? (typeof e == "string" ? (r = e.toUpperCase(), parseInt(r, 10).toString() === r && (r = parseInt(r, 10))) : typeof e == "number" && (r = e), typeof r == "number" ? s = document.createElement(this.tagName[r - 1]) : r && this.tagName.indexOf(r) > -1 ? s = document.createElement(r) : s = document.createElement(this.tagName[0])) : s = document.createElement(this.tagName), this.className && s.classList.add(this.className), s;
  }
  // Hack for accessing inherited static methods
  get statics() {
    return this.constructor;
  }
  attach() {
  }
  clone() {
    const e = this.domNode.cloneNode(!1);
    return this.scroll.create(e);
  }
  detach() {
    this.parent != null && this.parent.removeChild(this), ls.blots.delete(this.domNode);
  }
  deleteAt(e, s) {
    this.isolate(e, s).remove();
  }
  formatAt(e, s, r, i) {
    const a = this.isolate(e, s);
    if (this.scroll.query(r, V.BLOT) != null && i)
      a.wrap(r, i);
    else if (this.scroll.query(r, V.ATTRIBUTE) != null) {
      const n = this.scroll.create(this.statics.scope);
      a.wrap(n), n.format(r, i);
    }
  }
  insertAt(e, s, r) {
    const i = r == null ? this.scroll.create("text", s) : this.scroll.create(s, r), a = this.split(e);
    this.parent.insertBefore(i, a || void 0);
  }
  isolate(e, s) {
    const r = this.split(e);
    if (r == null)
      throw new Error("Attempt to isolate at end");
    return r.split(s), r;
  }
  length() {
    return 1;
  }
  offset(e = this.parent) {
    return this.parent == null || this === e ? 0 : this.parent.children.offset(this) + this.parent.offset(e);
  }
  optimize(e) {
    this.statics.requiredContainer && !(this.parent instanceof this.statics.requiredContainer) && this.wrap(this.statics.requiredContainer.blotName);
  }
  remove() {
    this.domNode.parentNode != null && this.domNode.parentNode.removeChild(this.domNode), this.detach();
  }
  replaceWith(e, s) {
    const r = typeof e == "string" ? this.scroll.create(e, s) : e;
    return this.parent != null && (this.parent.insertBefore(r, this.next || void 0), this.remove()), r;
  }
  split(e, s) {
    return e === 0 ? this : this.next;
  }
  update(e, s) {
  }
  wrap(e, s) {
    const r = typeof e == "string" ? this.scroll.create(e, s) : e;
    if (this.parent != null && this.parent.insertBefore(r, this.next || void 0), typeof r.appendChild != "function")
      throw new is(`Cannot wrap ${e}`);
    return r.appendChild(this), r;
  }
};
Mo.blotName = "abstract";
let Fo = Mo;
const Uo = class extends Fo {
  /**
   * Returns the value represented by domNode if it is this Blot's type
   * No checking that domNode can represent this Blot type is required so
   * applications needing it should check externally before calling.
   */
  static value(e) {
    return !0;
  }
  /**
   * Given location represented by node and offset from DOM Selection Range,
   * return index to that location.
   */
  index(e, s) {
    return this.domNode === e || this.domNode.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_CONTAINED_BY ? Math.min(s, 1) : -1;
  }
  /**
   * Given index to location within blot, return node and offset representing
   * that location, consumable by DOM Selection Range
   */
  position(e, s) {
    let r = Array.from(this.parent.domNode.childNodes).indexOf(this.domNode);
    return e > 0 && (r += 1), [this.parent.domNode, r];
  }
  /**
   * Return value represented by this blot
   * Should not change without interaction from API or
   * user change detectable by update()
   */
  value() {
    return {
      [this.statics.blotName]: this.statics.value(this.domNode) || !0
    };
  }
};
Uo.scope = V.INLINE_BLOT;
let lk = Uo;
const ge = lk;
class uk {
  constructor() {
    this.head = null, this.tail = null, this.length = 0;
  }
  append(...e) {
    if (this.insertBefore(e[0], null), e.length > 1) {
      const s = e.slice(1);
      this.append(...s);
    }
  }
  at(e) {
    const s = this.iterator();
    let r = s();
    for (; r && e > 0; )
      e -= 1, r = s();
    return r;
  }
  contains(e) {
    const s = this.iterator();
    let r = s();
    for (; r; ) {
      if (r === e)
        return !0;
      r = s();
    }
    return !1;
  }
  indexOf(e) {
    const s = this.iterator();
    let r = s(), i = 0;
    for (; r; ) {
      if (r === e)
        return i;
      i += 1, r = s();
    }
    return -1;
  }
  insertBefore(e, s) {
    e != null && (this.remove(e), e.next = s, s != null ? (e.prev = s.prev, s.prev != null && (s.prev.next = e), s.prev = e, s === this.head && (this.head = e)) : this.tail != null ? (this.tail.next = e, e.prev = this.tail, this.tail = e) : (e.prev = null, this.head = this.tail = e), this.length += 1);
  }
  offset(e) {
    let s = 0, r = this.head;
    for (; r != null; ) {
      if (r === e)
        return s;
      s += r.length(), r = r.next;
    }
    return -1;
  }
  remove(e) {
    this.contains(e) && (e.prev != null && (e.prev.next = e.next), e.next != null && (e.next.prev = e.prev), e === this.head && (this.head = e.next), e === this.tail && (this.tail = e.prev), this.length -= 1);
  }
  iterator(e = this.head) {
    return () => {
      const s = e;
      return e != null && (e = e.next), s;
    };
  }
  find(e, s = !1) {
    const r = this.iterator();
    let i = r();
    for (; i; ) {
      const a = i.length();
      if (e < a || s && e === a && (i.next == null || i.next.length() !== 0))
        return [i, e];
      e -= a, i = r();
    }
    return [null, 0];
  }
  forEach(e) {
    const s = this.iterator();
    let r = s();
    for (; r; )
      e(r), r = s();
  }
  forEachAt(e, s, r) {
    if (s <= 0)
      return;
    const [i, a] = this.find(e);
    let n = e - a;
    const o = this.iterator(i);
    let u = o();
    for (; u && n < e + s; ) {
      const p = u.length();
      e > n ? r(
        u,
        e - n,
        Math.min(s, n + p - e)
      ) : r(u, 0, Math.min(p, e + s - n)), n += p, u = o();
    }
  }
  map(e) {
    return this.reduce((s, r) => (s.push(e(r)), s), []);
  }
  reduce(e, s) {
    const r = this.iterator();
    let i = r();
    for (; i; )
      s = e(s, i), i = r();
    return s;
  }
}
function Oa(t, e) {
  const s = e.find(t);
  if (s)
    return s;
  try {
    return e.create(t);
  } catch {
    const r = e.create(V.INLINE);
    return Array.from(t.childNodes).forEach((i) => {
      r.domNode.appendChild(i);
    }), t.parentNode && t.parentNode.replaceChild(r.domNode, t), r.attach(), r;
  }
}
const jo = class gt extends Fo {
  constructor(e, s) {
    super(e, s), this.uiNode = null, this.build();
  }
  appendChild(e) {
    this.insertBefore(e);
  }
  attach() {
    super.attach(), this.children.forEach((e) => {
      e.attach();
    });
  }
  attachUI(e) {
    this.uiNode != null && this.uiNode.remove(), this.uiNode = e, gt.uiClass && this.uiNode.classList.add(gt.uiClass), this.uiNode.setAttribute("contenteditable", "false"), this.domNode.insertBefore(this.uiNode, this.domNode.firstChild);
  }
  /**
   * Called during construction, should fill its own children LinkedList.
   */
  build() {
    this.children = new uk(), Array.from(this.domNode.childNodes).filter((e) => e !== this.uiNode).reverse().forEach((e) => {
      try {
        const s = Oa(e, this.scroll);
        this.insertBefore(s, this.children.head || void 0);
      } catch (s) {
        if (s instanceof is)
          return;
        throw s;
      }
    });
  }
  deleteAt(e, s) {
    if (e === 0 && s === this.length())
      return this.remove();
    this.children.forEachAt(e, s, (r, i, a) => {
      r.deleteAt(i, a);
    });
  }
  descendant(e, s = 0) {
    const [r, i] = this.children.find(s);
    return e.blotName == null && e(r) || e.blotName != null && r instanceof e ? [r, i] : r instanceof gt ? r.descendant(e, i) : [null, -1];
  }
  descendants(e, s = 0, r = Number.MAX_VALUE) {
    let i = [], a = r;
    return this.children.forEachAt(
      s,
      r,
      (n, o, u) => {
        (e.blotName == null && e(n) || e.blotName != null && n instanceof e) && i.push(n), n instanceof gt && (i = i.concat(
          n.descendants(e, o, a)
        )), a -= u;
      }
    ), i;
  }
  detach() {
    this.children.forEach((e) => {
      e.detach();
    }), super.detach();
  }
  enforceAllowedChildren() {
    let e = !1;
    this.children.forEach((s) => {
      e || this.statics.allowedChildren.some(
        (r) => s instanceof r
      ) || (s.statics.scope === V.BLOCK_BLOT ? (s.next != null && this.splitAfter(s), s.prev != null && this.splitAfter(s.prev), s.parent.unwrap(), e = !0) : s instanceof gt ? s.unwrap() : s.remove());
    });
  }
  formatAt(e, s, r, i) {
    this.children.forEachAt(e, s, (a, n, o) => {
      a.formatAt(n, o, r, i);
    });
  }
  insertAt(e, s, r) {
    const [i, a] = this.children.find(e);
    if (i)
      i.insertAt(a, s, r);
    else {
      const n = r == null ? this.scroll.create("text", s) : this.scroll.create(s, r);
      this.appendChild(n);
    }
  }
  insertBefore(e, s) {
    e.parent != null && e.parent.children.remove(e);
    let r = null;
    this.children.insertBefore(e, s || null), e.parent = this, s != null && (r = s.domNode), (this.domNode.parentNode !== e.domNode || this.domNode.nextSibling !== r) && this.domNode.insertBefore(e.domNode, r), e.attach();
  }
  length() {
    return this.children.reduce((e, s) => e + s.length(), 0);
  }
  moveChildren(e, s) {
    this.children.forEach((r) => {
      e.insertBefore(r, s);
    });
  }
  optimize(e) {
    if (super.optimize(e), this.enforceAllowedChildren(), this.uiNode != null && this.uiNode !== this.domNode.firstChild && this.domNode.insertBefore(this.uiNode, this.domNode.firstChild), this.children.length === 0)
      if (this.statics.defaultChild != null) {
        const s = this.scroll.create(this.statics.defaultChild.blotName);
        this.appendChild(s);
      } else
        this.remove();
  }
  path(e, s = !1) {
    const [r, i] = this.children.find(e, s), a = [[this, e]];
    return r instanceof gt ? a.concat(r.path(i, s)) : (r != null && a.push([r, i]), a);
  }
  removeChild(e) {
    this.children.remove(e);
  }
  replaceWith(e, s) {
    const r = typeof e == "string" ? this.scroll.create(e, s) : e;
    return r instanceof gt && this.moveChildren(r), super.replaceWith(r);
  }
  split(e, s = !1) {
    if (!s) {
      if (e === 0)
        return this;
      if (e === this.length())
        return this.next;
    }
    const r = this.clone();
    return this.parent && this.parent.insertBefore(r, this.next || void 0), this.children.forEachAt(e, this.length(), (i, a, n) => {
      const o = i.split(a, s);
      o != null && r.appendChild(o);
    }), r;
  }
  splitAfter(e) {
    const s = this.clone();
    for (; e.next != null; )
      s.appendChild(e.next);
    return this.parent && this.parent.insertBefore(s, this.next || void 0), s;
  }
  unwrap() {
    this.parent && this.moveChildren(this.parent, this.next || void 0), this.remove();
  }
  update(e, s) {
    const r = [], i = [];
    e.forEach((a) => {
      a.target === this.domNode && a.type === "childList" && (r.push(...a.addedNodes), i.push(...a.removedNodes));
    }), i.forEach((a) => {
      if (a.parentNode != null && // @ts-expect-error Fix me later
      a.tagName !== "IFRAME" && document.body.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_CONTAINED_BY)
        return;
      const n = this.scroll.find(a);
      n != null && (n.domNode.parentNode == null || n.domNode.parentNode === this.domNode) && n.detach();
    }), r.filter((a) => a.parentNode === this.domNode && a !== this.uiNode).sort((a, n) => a === n ? 0 : a.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING ? 1 : -1).forEach((a) => {
      let n = null;
      a.nextSibling != null && (n = this.scroll.find(a.nextSibling));
      const o = Oa(a, this.scroll);
      (o.next !== n || o.next == null) && (o.parent != null && o.parent.removeChild(this), this.insertBefore(o, n || void 0));
    }), this.enforceAllowedChildren();
  }
};
jo.uiClass = "";
let dk = jo;
const Ue = dk;
function ck(t, e) {
  if (Object.keys(t).length !== Object.keys(e).length)
    return !1;
  for (const s in t)
    if (t[s] !== e[s])
      return !1;
  return !0;
}
const Jt = class xt extends Ue {
  static create(e) {
    return super.create(e);
  }
  static formats(e, s) {
    const r = s.query(xt.blotName);
    if (!(r != null && e.tagName === r.tagName)) {
      if (typeof this.tagName == "string")
        return !0;
      if (Array.isArray(this.tagName))
        return e.tagName.toLowerCase();
    }
  }
  constructor(e, s) {
    super(e, s), this.attributes = new Wn(this.domNode);
  }
  format(e, s) {
    if (e === this.statics.blotName && !s)
      this.children.forEach((r) => {
        r instanceof xt || (r = r.wrap(xt.blotName, !0)), this.attributes.copy(r);
      }), this.unwrap();
    else {
      const r = this.scroll.query(e, V.INLINE);
      if (r == null)
        return;
      r instanceof Je ? this.attributes.attribute(r, s) : s && (e !== this.statics.blotName || this.formats()[e] !== s) && this.replaceWith(e, s);
    }
  }
  formats() {
    const e = this.attributes.values(), s = this.statics.formats(this.domNode, this.scroll);
    return s != null && (e[this.statics.blotName] = s), e;
  }
  formatAt(e, s, r, i) {
    this.formats()[r] != null || this.scroll.query(r, V.ATTRIBUTE) ? this.isolate(e, s).format(r, i) : super.formatAt(e, s, r, i);
  }
  optimize(e) {
    super.optimize(e);
    const s = this.formats();
    if (Object.keys(s).length === 0)
      return this.unwrap();
    const r = this.next;
    r instanceof xt && r.prev === this && ck(s, r.formats()) && (r.moveChildren(this), r.remove());
  }
  replaceWith(e, s) {
    const r = super.replaceWith(e, s);
    return this.attributes.copy(r), r;
  }
  update(e, s) {
    super.update(e, s), e.some(
      (r) => r.target === this.domNode && r.type === "attributes"
    ) && this.attributes.build();
  }
  wrap(e, s) {
    const r = super.wrap(e, s);
    return r instanceof xt && this.attributes.move(r), r;
  }
};
Jt.allowedChildren = [Jt, ge], Jt.blotName = "inline", Jt.scope = V.INLINE_BLOT, Jt.tagName = "SPAN";
let fk = Jt;
const zi = fk, es = class bi extends Ue {
  static create(e) {
    return super.create(e);
  }
  static formats(e, s) {
    const r = s.query(bi.blotName);
    if (!(r != null && e.tagName === r.tagName)) {
      if (typeof this.tagName == "string")
        return !0;
      if (Array.isArray(this.tagName))
        return e.tagName.toLowerCase();
    }
  }
  constructor(e, s) {
    super(e, s), this.attributes = new Wn(this.domNode);
  }
  format(e, s) {
    const r = this.scroll.query(e, V.BLOCK);
    r != null && (r instanceof Je ? this.attributes.attribute(r, s) : e === this.statics.blotName && !s ? this.replaceWith(bi.blotName) : s && (e !== this.statics.blotName || this.formats()[e] !== s) && this.replaceWith(e, s));
  }
  formats() {
    const e = this.attributes.values(), s = this.statics.formats(this.domNode, this.scroll);
    return s != null && (e[this.statics.blotName] = s), e;
  }
  formatAt(e, s, r, i) {
    this.scroll.query(r, V.BLOCK) != null ? this.format(r, i) : super.formatAt(e, s, r, i);
  }
  insertAt(e, s, r) {
    if (r == null || this.scroll.query(s, V.INLINE) != null)
      super.insertAt(e, s, r);
    else {
      const i = this.split(e);
      if (i != null) {
        const a = this.scroll.create(s, r);
        i.parent.insertBefore(a, i);
      } else
        throw new Error("Attempt to insertAt after block boundaries");
    }
  }
  replaceWith(e, s) {
    const r = super.replaceWith(e, s);
    return this.attributes.copy(r), r;
  }
  update(e, s) {
    super.update(e, s), e.some(
      (r) => r.target === this.domNode && r.type === "attributes"
    ) && this.attributes.build();
  }
};
es.blotName = "block", es.scope = V.BLOCK_BLOT, es.tagName = "P", es.allowedChildren = [
  zi,
  es,
  ge
];
let pk = es;
const Gs = pk, yi = class extends Ue {
  checkMerge() {
    return this.next !== null && this.next.statics.blotName === this.statics.blotName;
  }
  deleteAt(e, s) {
    super.deleteAt(e, s), this.enforceAllowedChildren();
  }
  formatAt(e, s, r, i) {
    super.formatAt(e, s, r, i), this.enforceAllowedChildren();
  }
  insertAt(e, s, r) {
    super.insertAt(e, s, r), this.enforceAllowedChildren();
  }
  optimize(e) {
    super.optimize(e), this.children.length > 0 && this.next != null && this.checkMerge() && (this.next.moveChildren(this), this.next.remove());
  }
};
yi.blotName = "container", yi.scope = V.BLOCK_BLOT;
let hk = yi;
const Zn = hk;
class gk extends ge {
  static formats(e, s) {
  }
  format(e, s) {
    super.formatAt(0, this.length(), e, s);
  }
  formatAt(e, s, r, i) {
    e === 0 && s === this.length() ? this.format(r, i) : super.formatAt(e, s, r, i);
  }
  formats() {
    return this.statics.formats(this.domNode, this.scroll);
  }
}
const Ae = gk, mk = {
  attributes: !0,
  characterData: !0,
  characterDataOldValue: !0,
  childList: !0,
  subtree: !0
}, vk = 100, ts = class extends Ue {
  constructor(e, s) {
    super(null, s), this.registry = e, this.scroll = this, this.build(), this.observer = new MutationObserver((r) => {
      this.update(r);
    }), this.observer.observe(this.domNode, mk), this.attach();
  }
  create(e, s) {
    return this.registry.create(this, e, s);
  }
  find(e, s = !1) {
    const r = this.registry.find(e, s);
    return r ? r.scroll === this ? r : s ? this.find(r.scroll.domNode.parentNode, !0) : null : null;
  }
  query(e, s = V.ANY) {
    return this.registry.query(e, s);
  }
  register(...e) {
    return this.registry.register(...e);
  }
  build() {
    this.scroll != null && super.build();
  }
  detach() {
    super.detach(), this.observer.disconnect();
  }
  deleteAt(e, s) {
    this.update(), e === 0 && s === this.length() ? this.children.forEach((r) => {
      r.remove();
    }) : super.deleteAt(e, s);
  }
  formatAt(e, s, r, i) {
    this.update(), super.formatAt(e, s, r, i);
  }
  insertAt(e, s, r) {
    this.update(), super.insertAt(e, s, r);
  }
  optimize(e = [], s = {}) {
    super.optimize(s);
    const r = s.mutationsMap || /* @__PURE__ */ new WeakMap();
    let i = Array.from(this.observer.takeRecords());
    for (; i.length > 0; )
      e.push(i.pop());
    const a = (u, p = !0) => {
      u == null || u === this || u.domNode.parentNode != null && (r.has(u.domNode) || r.set(u.domNode, []), p && a(u.parent));
    }, n = (u) => {
      r.has(u.domNode) && (u instanceof Ue && u.children.forEach(n), r.delete(u.domNode), u.optimize(s));
    };
    let o = e;
    for (let u = 0; o.length > 0; u += 1) {
      if (u >= vk)
        throw new Error("[Parchment] Maximum optimize iterations reached");
      for (o.forEach((p) => {
        const g = this.find(p.target, !0);
        g != null && (g.domNode === p.target && (p.type === "childList" ? (a(this.find(p.previousSibling, !1)), Array.from(p.addedNodes).forEach((k) => {
          const y = this.find(k, !1);
          a(y, !1), y instanceof Ue && y.children.forEach((b) => {
            a(b, !1);
          });
        })) : p.type === "attributes" && a(g.prev)), a(g));
      }), this.children.forEach(n), o = Array.from(this.observer.takeRecords()), i = o.slice(); i.length > 0; )
        e.push(i.pop());
    }
  }
  update(e, s = {}) {
    e = e || this.observer.takeRecords();
    const r = /* @__PURE__ */ new WeakMap();
    e.map((i) => {
      const a = this.find(i.target, !0);
      return a == null ? null : r.has(a.domNode) ? (r.get(a.domNode).push(i), null) : (r.set(a.domNode, [i]), a);
    }).forEach((i) => {
      i != null && i !== this && r.has(i.domNode) && i.update(r.get(i.domNode) || [], s);
    }), s.mutationsMap = r, r.has(this.domNode) && super.update(r.get(this.domNode), s), this.optimize(e, s);
  }
};
ts.blotName = "scroll", ts.defaultChild = Gs, ts.allowedChildren = [Gs, Zn], ts.scope = V.BLOCK_BLOT, ts.tagName = "DIV";
let bk = ts;
const Gi = bk, $i = class Vo extends ge {
  static create(e) {
    return document.createTextNode(e);
  }
  static value(e) {
    return e.data;
  }
  constructor(e, s) {
    super(e, s), this.text = this.statics.value(this.domNode);
  }
  deleteAt(e, s) {
    this.domNode.data = this.text = this.text.slice(0, e) + this.text.slice(e + s);
  }
  index(e, s) {
    return this.domNode === e ? s : -1;
  }
  insertAt(e, s, r) {
    r == null ? (this.text = this.text.slice(0, e) + s + this.text.slice(e), this.domNode.data = this.text) : super.insertAt(e, s, r);
  }
  length() {
    return this.text.length;
  }
  optimize(e) {
    super.optimize(e), this.text = this.statics.value(this.domNode), this.text.length === 0 ? this.remove() : this.next instanceof Vo && this.next.prev === this && (this.insertAt(this.length(), this.next.value()), this.next.remove());
  }
  position(e, s = !1) {
    return [this.domNode, e];
  }
  split(e, s = !1) {
    if (!s) {
      if (e === 0)
        return this;
      if (e === this.length())
        return this.next;
    }
    const r = this.scroll.create(this.domNode.splitText(e));
    return this.parent.insertBefore(r, this.next || void 0), this.text = this.statics.value(this.domNode), r;
  }
  update(e, s) {
    e.some((r) => r.type === "characterData" && r.target === this.domNode) && (this.text = this.statics.value(this.domNode));
  }
  value() {
    return this.text;
  }
};
$i.blotName = "text", $i.scope = V.INLINE_BLOT;
let yk = $i;
const jn = yk, $k = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  Attributor: Je,
  AttributorStore: Wn,
  BlockBlot: Gs,
  ClassAttributor: Ve,
  ContainerBlot: Zn,
  EmbedBlot: Ae,
  InlineBlot: zi,
  LeafBlot: ge,
  ParentBlot: Ue,
  Registry: ls,
  Scope: V,
  ScrollBlot: Gi,
  StyleAttributor: wt,
  TextBlot: jn
}, Symbol.toStringTag, { value: "Module" }));
var mt = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
function Ho(t) {
  return t && t.__esModule && Object.prototype.hasOwnProperty.call(t, "default") ? t.default : t;
}
var ki = { exports: {} }, we = -1, be = 1, oe = 0;
function Ks(t, e, s, r, i) {
  if (t === e)
    return t ? [[oe, t]] : [];
  if (s != null) {
    var a = Nk(t, e, s);
    if (a)
      return a;
  }
  var n = Ki(t, e), o = t.substring(0, n);
  t = t.substring(n), e = e.substring(n), n = Xn(t, e);
  var u = t.substring(t.length - n);
  t = t.substring(0, t.length - n), e = e.substring(0, e.length - n);
  var p = kk(t, e);
  return o && p.unshift([oe, o]), u && p.push([oe, u]), Wi(p, i), r && Ak(p), p;
}
function kk(t, e) {
  var s;
  if (!t)
    return [[be, e]];
  if (!e)
    return [[we, t]];
  var r = t.length > e.length ? t : e, i = t.length > e.length ? e : t, a = r.indexOf(i);
  if (a !== -1)
    return s = [
      [be, r.substring(0, a)],
      [oe, i],
      [be, r.substring(a + i.length)]
    ], t.length > e.length && (s[0][0] = s[2][0] = we), s;
  if (i.length === 1)
    return [
      [we, t],
      [be, e]
    ];
  var n = Ck(t, e);
  if (n) {
    var o = n[0], u = n[1], p = n[2], g = n[3], k = n[4], y = Ks(o, p), b = Ks(u, g);
    return y.concat([[oe, k]], b);
  }
  return wk(t, e);
}
function wk(t, e) {
  for (var s = t.length, r = e.length, i = Math.ceil((s + r) / 2), a = i, n = 2 * i, o = new Array(n), u = new Array(n), p = 0; p < n; p++)
    o[p] = -1, u[p] = -1;
  o[a + 1] = 0, u[a + 1] = 0;
  for (var g = s - r, k = g % 2 !== 0, y = 0, b = 0, v = 0, E = 0, S = 0; S < i; S++) {
    for (var _ = -S + y; _ <= S - b; _ += 2) {
      var O = a + _, D;
      _ === -S || _ !== S && o[O - 1] < o[O + 1] ? D = o[O + 1] : D = o[O - 1] + 1;
      for (var U = D - _; D < s && U < r && t.charAt(D) === e.charAt(U); )
        D++, U++;
      if (o[O] = D, D > s)
        b += 2;
      else if (U > r)
        y += 2;
      else if (k) {
        var M = a + g - _;
        if (M >= 0 && M < n && u[M] !== -1) {
          var G = s - u[M];
          if (D >= G)
            return Pa(t, e, D, U);
        }
      }
    }
    for (var Z = -S + v; Z <= S - E; Z += 2) {
      var M = a + Z, G;
      Z === -S || Z !== S && u[M - 1] < u[M + 1] ? G = u[M + 1] : G = u[M - 1] + 1;
      for (var te = G - Z; G < s && te < r && t.charAt(s - G - 1) === e.charAt(r - te - 1); )
        G++, te++;
      if (u[M] = G, G > s)
        E += 2;
      else if (te > r)
        v += 2;
      else if (!k) {
        var O = a + g - Z;
        if (O >= 0 && O < n && o[O] !== -1) {
          var D = o[O], U = a + D - O;
          if (G = s - G, D >= G)
            return Pa(t, e, D, U);
        }
      }
    }
  }
  return [
    [we, t],
    [be, e]
  ];
}
function Pa(t, e, s, r) {
  var i = t.substring(0, s), a = e.substring(0, r), n = t.substring(s), o = e.substring(r), u = Ks(i, a), p = Ks(n, o);
  return u.concat(p);
}
function Ki(t, e) {
  if (!t || !e || t.charAt(0) !== e.charAt(0))
    return 0;
  for (var s = 0, r = Math.min(t.length, e.length), i = r, a = 0; s < i; )
    t.substring(a, i) == e.substring(a, i) ? (s = i, a = s) : r = i, i = Math.floor((r - s) / 2 + s);
  return zo(t.charCodeAt(i - 1)) && i--, i;
}
function Da(t, e) {
  var s = t.length, r = e.length;
  if (s == 0 || r == 0)
    return 0;
  s > r ? t = t.substring(s - r) : s < r && (e = e.substring(0, s));
  var i = Math.min(s, r);
  if (t == e)
    return i;
  for (var a = 0, n = 1; ; ) {
    var o = t.substring(i - n), u = e.indexOf(o);
    if (u == -1)
      return a;
    n += u, (u == 0 || t.substring(i - n) == e.substring(0, n)) && (a = n, n++);
  }
}
function Xn(t, e) {
  if (!t || !e || t.slice(-1) !== e.slice(-1))
    return 0;
  for (var s = 0, r = Math.min(t.length, e.length), i = r, a = 0; s < i; )
    t.substring(t.length - i, t.length - a) == e.substring(e.length - i, e.length - a) ? (s = i, a = s) : r = i, i = Math.floor((r - s) / 2 + s);
  return Go(t.charCodeAt(t.length - i)) && i--, i;
}
function Ck(t, e) {
  var s = t.length > e.length ? t : e, r = t.length > e.length ? e : t;
  if (s.length < 4 || r.length * 2 < s.length)
    return null;
  function i(b, v, E) {
    for (var S = b.substring(E, E + Math.floor(b.length / 4)), _ = -1, O = "", D, U, M, G; (_ = v.indexOf(S, _ + 1)) !== -1; ) {
      var Z = Ki(
        b.substring(E),
        v.substring(_)
      ), te = Xn(
        b.substring(0, E),
        v.substring(0, _)
      );
      O.length < te + Z && (O = v.substring(_ - te, _) + v.substring(_, _ + Z), D = b.substring(0, E - te), U = b.substring(E + Z), M = v.substring(0, _ - te), G = v.substring(_ + Z));
    }
    return O.length * 2 >= b.length ? [
      D,
      U,
      M,
      G,
      O
    ] : null;
  }
  var a = i(
    s,
    r,
    Math.ceil(s.length / 4)
  ), n = i(
    s,
    r,
    Math.ceil(s.length / 2)
  ), o;
  if (!a && !n)
    return null;
  n ? a ? o = a[4].length > n[4].length ? a : n : o = n : o = a;
  var u, p, g, k;
  t.length > e.length ? (u = o[0], p = o[1], g = o[2], k = o[3]) : (g = o[0], k = o[1], u = o[2], p = o[3]);
  var y = o[4];
  return [u, p, g, k, y];
}
function Ak(t) {
  for (var e = !1, s = [], r = 0, i = null, a = 0, n = 0, o = 0, u = 0, p = 0; a < t.length; )
    t[a][0] == oe ? (s[r++] = a, n = u, o = p, u = 0, p = 0, i = t[a][1]) : (t[a][0] == be ? u += t[a][1].length : p += t[a][1].length, i && i.length <= Math.max(n, o) && i.length <= Math.max(u, p) && (t.splice(s[r - 1], 0, [
      we,
      i
    ]), t[s[r - 1] + 1][0] = be, r--, r--, a = r > 0 ? s[r - 1] : -1, n = 0, o = 0, u = 0, p = 0, i = null, e = !0)), a++;
  for (e && Wi(t), Tk(t), a = 1; a < t.length; ) {
    if (t[a - 1][0] == we && t[a][0] == be) {
      var g = t[a - 1][1], k = t[a][1], y = Da(g, k), b = Da(k, g);
      y >= b ? (y >= g.length / 2 || y >= k.length / 2) && (t.splice(a, 0, [
        oe,
        k.substring(0, y)
      ]), t[a - 1][1] = g.substring(
        0,
        g.length - y
      ), t[a + 1][1] = k.substring(y), a++) : (b >= g.length / 2 || b >= k.length / 2) && (t.splice(a, 0, [
        oe,
        g.substring(0, b)
      ]), t[a - 1][0] = be, t[a - 1][1] = k.substring(
        0,
        k.length - b
      ), t[a + 1][0] = we, t[a + 1][1] = g.substring(b), a++), a++;
    }
    a++;
  }
}
var Ra = /[^a-zA-Z0-9]/, Ba = /\s/, Ma = /[\r\n]/, Ek = /\n\r?\n$/, Sk = /^\r?\n\r?\n/;
function Tk(t) {
  function e(b, v) {
    if (!b || !v)
      return 6;
    var E = b.charAt(b.length - 1), S = v.charAt(0), _ = E.match(Ra), O = S.match(Ra), D = _ && E.match(Ba), U = O && S.match(Ba), M = D && E.match(Ma), G = U && S.match(Ma), Z = M && b.match(Ek), te = G && v.match(Sk);
    return Z || te ? 5 : M || G ? 4 : _ && !D && U ? 3 : D || U ? 2 : _ || O ? 1 : 0;
  }
  for (var s = 1; s < t.length - 1; ) {
    if (t[s - 1][0] == oe && t[s + 1][0] == oe) {
      var r = t[s - 1][1], i = t[s][1], a = t[s + 1][1], n = Xn(r, i);
      if (n) {
        var o = i.substring(i.length - n);
        r = r.substring(0, r.length - n), i = o + i.substring(0, i.length - n), a = o + a;
      }
      for (var u = r, p = i, g = a, k = e(r, i) + e(i, a); i.charAt(0) === a.charAt(0); ) {
        r += i.charAt(0), i = i.substring(1) + a.charAt(0), a = a.substring(1);
        var y = e(r, i) + e(i, a);
        y >= k && (k = y, u = r, p = i, g = a);
      }
      t[s - 1][1] != u && (u ? t[s - 1][1] = u : (t.splice(s - 1, 1), s--), t[s][1] = p, g ? t[s + 1][1] = g : (t.splice(s + 1, 1), s--));
    }
    s++;
  }
}
function Wi(t, e) {
  t.push([oe, ""]);
  for (var s = 0, r = 0, i = 0, a = "", n = "", o; s < t.length; ) {
    if (s < t.length - 1 && !t[s][1]) {
      t.splice(s, 1);
      continue;
    }
    switch (t[s][0]) {
      case be:
        i++, n += t[s][1], s++;
        break;
      case we:
        r++, a += t[s][1], s++;
        break;
      case oe:
        var u = s - i - r - 1;
        if (e) {
          if (u >= 0 && Wo(t[u][1])) {
            var p = t[u][1].slice(-1);
            if (t[u][1] = t[u][1].slice(
              0,
              -1
            ), a = p + a, n = p + n, !t[u][1]) {
              t.splice(u, 1), s--;
              var g = u - 1;
              t[g] && t[g][0] === be && (i++, n = t[g][1] + n, g--), t[g] && t[g][0] === we && (r++, a = t[g][1] + a, g--), u = g;
            }
          }
          if (Ko(t[s][1])) {
            var p = t[s][1].charAt(0);
            t[s][1] = t[s][1].slice(1), a += p, n += p;
          }
        }
        if (s < t.length - 1 && !t[s][1]) {
          t.splice(s, 1);
          break;
        }
        if (a.length > 0 || n.length > 0) {
          a.length > 0 && n.length > 0 && (o = Ki(n, a), o !== 0 && (u >= 0 ? t[u][1] += n.substring(
            0,
            o
          ) : (t.splice(0, 0, [
            oe,
            n.substring(0, o)
          ]), s++), n = n.substring(o), a = a.substring(o)), o = Xn(n, a), o !== 0 && (t[s][1] = n.substring(n.length - o) + t[s][1], n = n.substring(
            0,
            n.length - o
          ), a = a.substring(
            0,
            a.length - o
          )));
          var k = i + r;
          a.length === 0 && n.length === 0 ? (t.splice(s - k, k), s = s - k) : a.length === 0 ? (t.splice(s - k, k, [be, n]), s = s - k + 1) : n.length === 0 ? (t.splice(s - k, k, [we, a]), s = s - k + 1) : (t.splice(
            s - k,
            k,
            [we, a],
            [be, n]
          ), s = s - k + 2);
        }
        s !== 0 && t[s - 1][0] === oe ? (t[s - 1][1] += t[s][1], t.splice(s, 1)) : s++, i = 0, r = 0, a = "", n = "";
        break;
    }
  }
  t[t.length - 1][1] === "" && t.pop();
  var y = !1;
  for (s = 1; s < t.length - 1; )
    t[s - 1][0] === oe && t[s + 1][0] === oe && (t[s][1].substring(
      t[s][1].length - t[s - 1][1].length
    ) === t[s - 1][1] ? (t[s][1] = t[s - 1][1] + t[s][1].substring(
      0,
      t[s][1].length - t[s - 1][1].length
    ), t[s + 1][1] = t[s - 1][1] + t[s + 1][1], t.splice(s - 1, 1), y = !0) : t[s][1].substring(0, t[s + 1][1].length) == t[s + 1][1] && (t[s - 1][1] += t[s + 1][1], t[s][1] = t[s][1].substring(t[s + 1][1].length) + t[s + 1][1], t.splice(s + 1, 1), y = !0)), s++;
  y && Wi(t, e);
}
function zo(t) {
  return t >= 55296 && t <= 56319;
}
function Go(t) {
  return t >= 56320 && t <= 57343;
}
function Ko(t) {
  return Go(t.charCodeAt(0));
}
function Wo(t) {
  return zo(t.charCodeAt(t.length - 1));
}
function _k(t) {
  for (var e = [], s = 0; s < t.length; s++)
    t[s][1].length > 0 && e.push(t[s]);
  return e;
}
function xr(t, e, s, r) {
  return Wo(t) || Ko(r) ? null : _k([
    [oe, t],
    [we, e],
    [be, s],
    [oe, r]
  ]);
}
function Nk(t, e, s) {
  var r = typeof s == "number" ? { index: s, length: 0 } : s.oldRange, i = typeof s == "number" ? null : s.newRange, a = t.length, n = e.length;
  if (r.length === 0 && (i === null || i.length === 0)) {
    var o = r.index, u = t.slice(0, o), p = t.slice(o), g = i ? i.index : null;
    e: {
      var k = o + n - a;
      if (g !== null && g !== k || k < 0 || k > n)
        break e;
      var y = e.slice(0, k), b = e.slice(k);
      if (b !== p)
        break e;
      var v = Math.min(o, k), E = u.slice(0, v), S = y.slice(0, v);
      if (E !== S)
        break e;
      var _ = u.slice(v), O = y.slice(v);
      return xr(E, _, O, p);
    }
    e: {
      if (g !== null && g !== o)
        break e;
      var D = o, y = e.slice(0, D), b = e.slice(D);
      if (y !== u)
        break e;
      var U = Math.min(a - D, n - D), M = p.slice(p.length - U), G = b.slice(b.length - U);
      if (M !== G)
        break e;
      var _ = p.slice(0, p.length - U), O = b.slice(0, b.length - U);
      return xr(u, _, O, M);
    }
  }
  if (r.length > 0 && i && i.length === 0)
    e: {
      var E = t.slice(0, r.index), M = t.slice(r.index + r.length), v = E.length, U = M.length;
      if (n < v + U)
        break e;
      var S = e.slice(0, v), G = e.slice(n - U);
      if (E !== S || M !== G)
        break e;
      var _ = t.slice(v, a - U), O = e.slice(v, n - U);
      return xr(E, _, O, M);
    }
  return null;
}
function Yn(t, e, s, r) {
  return Ks(t, e, s, r, !0);
}
Yn.INSERT = be;
Yn.DELETE = we;
Yn.EQUAL = oe;
var Ik = Yn, Vn = { exports: {} };
Vn.exports;
(function(t, e) {
  var s = 200, r = "__lodash_hash_undefined__", i = 9007199254740991, a = "[object Arguments]", n = "[object Array]", o = "[object Boolean]", u = "[object Date]", p = "[object Error]", g = "[object Function]", k = "[object GeneratorFunction]", y = "[object Map]", b = "[object Number]", v = "[object Object]", E = "[object Promise]", S = "[object RegExp]", _ = "[object Set]", O = "[object String]", D = "[object Symbol]", U = "[object WeakMap]", M = "[object ArrayBuffer]", G = "[object DataView]", Z = "[object Float32Array]", te = "[object Float64Array]", tt = "[object Int8Array]", ft = "[object Int16Array]", Ct = "[object Int32Array]", At = "[object Uint8Array]", tn = "[object Uint8ClampedArray]", sn = "[object Uint16Array]", nn = "[object Uint32Array]", tr = /[\\^$.*+?()[\]{}|]/g, sr = /\w*$/, nr = /^\[object .+?Constructor\]$/, rr = /^(?:0|[1-9]\d*)$/, J = {};
  J[a] = J[n] = J[M] = J[G] = J[o] = J[u] = J[Z] = J[te] = J[tt] = J[ft] = J[Ct] = J[y] = J[b] = J[v] = J[S] = J[_] = J[O] = J[D] = J[At] = J[tn] = J[sn] = J[nn] = !0, J[p] = J[g] = J[U] = !1;
  var ir = typeof mt == "object" && mt && mt.Object === Object && mt, ar = typeof self == "object" && self && self.Object === Object && self, Le = ir || ar || Function("return this")(), rn = e && !e.nodeType && e, x = rn && !0 && t && !t.nodeType && t, an = x && x.exports === rn;
  function or(l, h) {
    return l.set(h[0], h[1]), l;
  }
  function qe(l, h) {
    return l.add(h), l;
  }
  function on(l, h) {
    for (var $ = -1, T = l ? l.length : 0; ++$ < T && h(l[$], $, l) !== !1; )
      ;
    return l;
  }
  function ln(l, h) {
    for (var $ = -1, T = h.length, K = l.length; ++$ < T; )
      l[K + $] = h[$];
    return l;
  }
  function hs(l, h, $, T) {
    for (var K = -1, z = l ? l.length : 0; ++K < z; )
      $ = h($, l[K], K, l);
    return $;
  }
  function gs(l, h) {
    for (var $ = -1, T = Array(l); ++$ < l; )
      T[$] = h($);
    return T;
  }
  function un(l, h) {
    return l == null ? void 0 : l[h];
  }
  function ms(l) {
    var h = !1;
    if (l != null && typeof l.toString != "function")
      try {
        h = !!(l + "");
      } catch {
      }
    return h;
  }
  function dn(l) {
    var h = -1, $ = Array(l.size);
    return l.forEach(function(T, K) {
      $[++h] = [K, T];
    }), $;
  }
  function vs(l, h) {
    return function($) {
      return l(h($));
    };
  }
  function cn(l) {
    var h = -1, $ = Array(l.size);
    return l.forEach(function(T) {
      $[++h] = T;
    }), $;
  }
  var lr = Array.prototype, ur = Function.prototype, jt = Object.prototype, bs = Le["__core-js_shared__"], fn = function() {
    var l = /[^.]+$/.exec(bs && bs.keys && bs.keys.IE_PROTO || "");
    return l ? "Symbol(src)_1." + l : "";
  }(), pn = ur.toString, Ge = jt.hasOwnProperty, Vt = jt.toString, dr = RegExp(
    "^" + pn.call(Ge).replace(tr, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
  ), Et = an ? Le.Buffer : void 0, Ht = Le.Symbol, ys = Le.Uint8Array, Ee = vs(Object.getPrototypeOf, Object), hn = Object.create, gn = jt.propertyIsEnumerable, cr = lr.splice, $s = Object.getOwnPropertySymbols, zt = Et ? Et.isBuffer : void 0, mn = vs(Object.keys, Object), Gt = Pe(Le, "DataView"), St = Pe(Le, "Map"), Oe = Pe(Le, "Promise"), Kt = Pe(Le, "Set"), ks = Pe(Le, "WeakMap"), Tt = Pe(Object, "create"), ws = ve(Gt), _t = ve(St), Cs = ve(Oe), As = ve(Kt), Es = ve(ks), pt = Ht ? Ht.prototype : void 0, vn = pt ? pt.valueOf : void 0;
  function st(l) {
    var h = -1, $ = l ? l.length : 0;
    for (this.clear(); ++h < $; ) {
      var T = l[h];
      this.set(T[0], T[1]);
    }
  }
  function fr() {
    this.__data__ = Tt ? Tt(null) : {};
  }
  function pr(l) {
    return this.has(l) && delete this.__data__[l];
  }
  function hr(l) {
    var h = this.__data__;
    if (Tt) {
      var $ = h[l];
      return $ === r ? void 0 : $;
    }
    return Ge.call(h, l) ? h[l] : void 0;
  }
  function bn(l) {
    var h = this.__data__;
    return Tt ? h[l] !== void 0 : Ge.call(h, l);
  }
  function Ss(l, h) {
    var $ = this.__data__;
    return $[l] = Tt && h === void 0 ? r : h, this;
  }
  st.prototype.clear = fr, st.prototype.delete = pr, st.prototype.get = hr, st.prototype.has = bn, st.prototype.set = Ss;
  function le(l) {
    var h = -1, $ = l ? l.length : 0;
    for (this.clear(); ++h < $; ) {
      var T = l[h];
      this.set(T[0], T[1]);
    }
  }
  function gr() {
    this.__data__ = [];
  }
  function mr(l) {
    var h = this.__data__, $ = Zt(h, l);
    if ($ < 0)
      return !1;
    var T = h.length - 1;
    return $ == T ? h.pop() : cr.call(h, $, 1), !0;
  }
  function vr(l) {
    var h = this.__data__, $ = Zt(h, l);
    return $ < 0 ? void 0 : h[$][1];
  }
  function br(l) {
    return Zt(this.__data__, l) > -1;
  }
  function yr(l, h) {
    var $ = this.__data__, T = Zt($, l);
    return T < 0 ? $.push([l, h]) : $[T][1] = h, this;
  }
  le.prototype.clear = gr, le.prototype.delete = mr, le.prototype.get = vr, le.prototype.has = br, le.prototype.set = yr;
  function fe(l) {
    var h = -1, $ = l ? l.length : 0;
    for (this.clear(); ++h < $; ) {
      var T = l[h];
      this.set(T[0], T[1]);
    }
  }
  function $r() {
    this.__data__ = {
      hash: new st(),
      map: new (St || le)(),
      string: new st()
    };
  }
  function kr(l) {
    return It(this, l).delete(l);
  }
  function wr(l) {
    return It(this, l).get(l);
  }
  function Cr(l) {
    return It(this, l).has(l);
  }
  function Ar(l, h) {
    return It(this, l).set(l, h), this;
  }
  fe.prototype.clear = $r, fe.prototype.delete = kr, fe.prototype.get = wr, fe.prototype.has = Cr, fe.prototype.set = Ar;
  function $e(l) {
    this.__data__ = new le(l);
  }
  function Er() {
    this.__data__ = new le();
  }
  function Sr(l) {
    return this.__data__.delete(l);
  }
  function Tr(l) {
    return this.__data__.get(l);
  }
  function _r(l) {
    return this.__data__.has(l);
  }
  function Nr(l, h) {
    var $ = this.__data__;
    if ($ instanceof le) {
      var T = $.__data__;
      if (!St || T.length < s - 1)
        return T.push([l, h]), this;
      $ = this.__data__ = new fe(T);
    }
    return $.set(l, h), this;
  }
  $e.prototype.clear = Er, $e.prototype.delete = Sr, $e.prototype.get = Tr, $e.prototype.has = _r, $e.prototype.set = Nr;
  function Wt(l, h) {
    var $ = Is(l) || Yt(l) ? gs(l.length, String) : [], T = $.length, K = !!T;
    for (var z in l)
      Ge.call(l, z) && !(K && (z == "length" || Hr(z, T))) && $.push(z);
    return $;
  }
  function yn(l, h, $) {
    var T = l[h];
    (!(Ge.call(l, h) && An(T, $)) || $ === void 0 && !(h in l)) && (l[h] = $);
  }
  function Zt(l, h) {
    for (var $ = l.length; $--; )
      if (An(l[$][0], h))
        return $;
    return -1;
  }
  function Ke(l, h) {
    return l && Ns(h, qs(h), l);
  }
  function Ts(l, h, $, T, K, z, Y) {
    var X;
    if (T && (X = z ? T(l, K, z, Y) : T(l)), X !== void 0)
      return X;
    if (!Ze(l))
      return l;
    var re = Is(l);
    if (re) {
      if (X = jr(l), !h)
        return Mr(l, X);
    } else {
      var Q = rt(l), pe = Q == g || Q == k;
      if (En(l))
        return Xt(l, h);
      if (Q == v || Q == a || pe && !z) {
        if (ms(l))
          return z ? l : {};
        if (X = We(pe ? {} : l), !h)
          return Fr(l, Ke(X, l));
      } else {
        if (!J[Q])
          return z ? l : {};
        X = Vr(l, Q, Ts, h);
      }
    }
    Y || (Y = new $e());
    var ke = Y.get(l);
    if (ke)
      return ke;
    if (Y.set(l, X), !re)
      var ae = $ ? Ur(l) : qs(l);
    return on(ae || l, function(he, ue) {
      ae && (ue = he, he = l[ue]), yn(X, ue, Ts(he, h, $, T, ue, l, Y));
    }), X;
  }
  function Ir(l) {
    return Ze(l) ? hn(l) : {};
  }
  function Lr(l, h, $) {
    var T = h(l);
    return Is(l) ? T : ln(T, $(l));
  }
  function qr(l) {
    return Vt.call(l);
  }
  function Or(l) {
    if (!Ze(l) || Gr(l))
      return !1;
    var h = Ls(l) || ms(l) ? dr : nr;
    return h.test(ve(l));
  }
  function Pr(l) {
    if (!wn(l))
      return mn(l);
    var h = [];
    for (var $ in Object(l))
      Ge.call(l, $) && $ != "constructor" && h.push($);
    return h;
  }
  function Xt(l, h) {
    if (h)
      return l.slice();
    var $ = new l.constructor(l.length);
    return l.copy($), $;
  }
  function _s(l) {
    var h = new l.constructor(l.byteLength);
    return new ys(h).set(new ys(l)), h;
  }
  function Nt(l, h) {
    var $ = h ? _s(l.buffer) : l.buffer;
    return new l.constructor($, l.byteOffset, l.byteLength);
  }
  function $n(l, h, $) {
    var T = h ? $(dn(l), !0) : dn(l);
    return hs(T, or, new l.constructor());
  }
  function kn(l) {
    var h = new l.constructor(l.source, sr.exec(l));
    return h.lastIndex = l.lastIndex, h;
  }
  function Dr(l, h, $) {
    var T = h ? $(cn(l), !0) : cn(l);
    return hs(T, qe, new l.constructor());
  }
  function Rr(l) {
    return vn ? Object(vn.call(l)) : {};
  }
  function Br(l, h) {
    var $ = h ? _s(l.buffer) : l.buffer;
    return new l.constructor($, l.byteOffset, l.length);
  }
  function Mr(l, h) {
    var $ = -1, T = l.length;
    for (h || (h = Array(T)); ++$ < T; )
      h[$] = l[$];
    return h;
  }
  function Ns(l, h, $, T) {
    $ || ($ = {});
    for (var K = -1, z = h.length; ++K < z; ) {
      var Y = h[K], X = void 0;
      yn($, Y, X === void 0 ? l[Y] : X);
    }
    return $;
  }
  function Fr(l, h) {
    return Ns(l, nt(l), h);
  }
  function Ur(l) {
    return Lr(l, qs, nt);
  }
  function It(l, h) {
    var $ = l.__data__;
    return zr(h) ? $[typeof h == "string" ? "string" : "hash"] : $.map;
  }
  function Pe(l, h) {
    var $ = un(l, h);
    return Or($) ? $ : void 0;
  }
  var nt = $s ? vs($s, Object) : Wr, rt = qr;
  (Gt && rt(new Gt(new ArrayBuffer(1))) != G || St && rt(new St()) != y || Oe && rt(Oe.resolve()) != E || Kt && rt(new Kt()) != _ || ks && rt(new ks()) != U) && (rt = function(l) {
    var h = Vt.call(l), $ = h == v ? l.constructor : void 0, T = $ ? ve($) : void 0;
    if (T)
      switch (T) {
        case ws:
          return G;
        case _t:
          return y;
        case Cs:
          return E;
        case As:
          return _;
        case Es:
          return U;
      }
    return h;
  });
  function jr(l) {
    var h = l.length, $ = l.constructor(h);
    return h && typeof l[0] == "string" && Ge.call(l, "index") && ($.index = l.index, $.input = l.input), $;
  }
  function We(l) {
    return typeof l.constructor == "function" && !wn(l) ? Ir(Ee(l)) : {};
  }
  function Vr(l, h, $, T) {
    var K = l.constructor;
    switch (h) {
      case M:
        return _s(l);
      case o:
      case u:
        return new K(+l);
      case G:
        return Nt(l, T);
      case Z:
      case te:
      case tt:
      case ft:
      case Ct:
      case At:
      case tn:
      case sn:
      case nn:
        return Br(l, T);
      case y:
        return $n(l, T, $);
      case b:
      case O:
        return new K(l);
      case S:
        return kn(l);
      case _:
        return Dr(l, T, $);
      case D:
        return Rr(l);
    }
  }
  function Hr(l, h) {
    return h = h ?? i, !!h && (typeof l == "number" || rr.test(l)) && l > -1 && l % 1 == 0 && l < h;
  }
  function zr(l) {
    var h = typeof l;
    return h == "string" || h == "number" || h == "symbol" || h == "boolean" ? l !== "__proto__" : l === null;
  }
  function Gr(l) {
    return !!fn && fn in l;
  }
  function wn(l) {
    var h = l && l.constructor, $ = typeof h == "function" && h.prototype || jt;
    return l === $;
  }
  function ve(l) {
    if (l != null) {
      try {
        return pn.call(l);
      } catch {
      }
      try {
        return l + "";
      } catch {
      }
    }
    return "";
  }
  function Cn(l) {
    return Ts(l, !0, !0);
  }
  function An(l, h) {
    return l === h || l !== l && h !== h;
  }
  function Yt(l) {
    return Kr(l) && Ge.call(l, "callee") && (!gn.call(l, "callee") || Vt.call(l) == a);
  }
  var Is = Array.isArray;
  function Qt(l) {
    return l != null && Sn(l.length) && !Ls(l);
  }
  function Kr(l) {
    return Tn(l) && Qt(l);
  }
  var En = zt || Zr;
  function Ls(l) {
    var h = Ze(l) ? Vt.call(l) : "";
    return h == g || h == k;
  }
  function Sn(l) {
    return typeof l == "number" && l > -1 && l % 1 == 0 && l <= i;
  }
  function Ze(l) {
    var h = typeof l;
    return !!l && (h == "object" || h == "function");
  }
  function Tn(l) {
    return !!l && typeof l == "object";
  }
  function qs(l) {
    return Qt(l) ? Wt(l) : Pr(l);
  }
  function Wr() {
    return [];
  }
  function Zr() {
    return !1;
  }
  t.exports = Cn;
})(Vn, Vn.exports);
var Zo = Vn.exports, Hn = { exports: {} };
Hn.exports;
(function(t, e) {
  var s = 200, r = "__lodash_hash_undefined__", i = 1, a = 2, n = 9007199254740991, o = "[object Arguments]", u = "[object Array]", p = "[object AsyncFunction]", g = "[object Boolean]", k = "[object Date]", y = "[object Error]", b = "[object Function]", v = "[object GeneratorFunction]", E = "[object Map]", S = "[object Number]", _ = "[object Null]", O = "[object Object]", D = "[object Promise]", U = "[object Proxy]", M = "[object RegExp]", G = "[object Set]", Z = "[object String]", te = "[object Symbol]", tt = "[object Undefined]", ft = "[object WeakMap]", Ct = "[object ArrayBuffer]", At = "[object DataView]", tn = "[object Float32Array]", sn = "[object Float64Array]", nn = "[object Int8Array]", tr = "[object Int16Array]", sr = "[object Int32Array]", nr = "[object Uint8Array]", rr = "[object Uint8ClampedArray]", J = "[object Uint16Array]", ir = "[object Uint32Array]", ar = /[\\^$.*+?()[\]{}|]/g, Le = /^\[object .+?Constructor\]$/, rn = /^(?:0|[1-9]\d*)$/, x = {};
  x[tn] = x[sn] = x[nn] = x[tr] = x[sr] = x[nr] = x[rr] = x[J] = x[ir] = !0, x[o] = x[u] = x[Ct] = x[g] = x[At] = x[k] = x[y] = x[b] = x[E] = x[S] = x[O] = x[M] = x[G] = x[Z] = x[ft] = !1;
  var an = typeof mt == "object" && mt && mt.Object === Object && mt, or = typeof self == "object" && self && self.Object === Object && self, qe = an || or || Function("return this")(), on = e && !e.nodeType && e, ln = on && !0 && t && !t.nodeType && t, hs = ln && ln.exports === on, gs = hs && an.process, un = function() {
    try {
      return gs && gs.binding && gs.binding("util");
    } catch {
    }
  }(), ms = un && un.isTypedArray;
  function dn(l, h) {
    for (var $ = -1, T = l == null ? 0 : l.length, K = 0, z = []; ++$ < T; ) {
      var Y = l[$];
      h(Y, $, l) && (z[K++] = Y);
    }
    return z;
  }
  function vs(l, h) {
    for (var $ = -1, T = h.length, K = l.length; ++$ < T; )
      l[K + $] = h[$];
    return l;
  }
  function cn(l, h) {
    for (var $ = -1, T = l == null ? 0 : l.length; ++$ < T; )
      if (h(l[$], $, l))
        return !0;
    return !1;
  }
  function lr(l, h) {
    for (var $ = -1, T = Array(l); ++$ < l; )
      T[$] = h($);
    return T;
  }
  function ur(l) {
    return function(h) {
      return l(h);
    };
  }
  function jt(l, h) {
    return l.has(h);
  }
  function bs(l, h) {
    return l == null ? void 0 : l[h];
  }
  function fn(l) {
    var h = -1, $ = Array(l.size);
    return l.forEach(function(T, K) {
      $[++h] = [K, T];
    }), $;
  }
  function pn(l, h) {
    return function($) {
      return l(h($));
    };
  }
  function Ge(l) {
    var h = -1, $ = Array(l.size);
    return l.forEach(function(T) {
      $[++h] = T;
    }), $;
  }
  var Vt = Array.prototype, dr = Function.prototype, Et = Object.prototype, Ht = qe["__core-js_shared__"], ys = dr.toString, Ee = Et.hasOwnProperty, hn = function() {
    var l = /[^.]+$/.exec(Ht && Ht.keys && Ht.keys.IE_PROTO || "");
    return l ? "Symbol(src)_1." + l : "";
  }(), gn = Et.toString, cr = RegExp(
    "^" + ys.call(Ee).replace(ar, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
  ), $s = hs ? qe.Buffer : void 0, zt = qe.Symbol, mn = qe.Uint8Array, Gt = Et.propertyIsEnumerable, St = Vt.splice, Oe = zt ? zt.toStringTag : void 0, Kt = Object.getOwnPropertySymbols, ks = $s ? $s.isBuffer : void 0, Tt = pn(Object.keys, Object), ws = nt(qe, "DataView"), _t = nt(qe, "Map"), Cs = nt(qe, "Promise"), As = nt(qe, "Set"), Es = nt(qe, "WeakMap"), pt = nt(Object, "create"), vn = ve(ws), st = ve(_t), fr = ve(Cs), pr = ve(As), hr = ve(Es), bn = zt ? zt.prototype : void 0, Ss = bn ? bn.valueOf : void 0;
  function le(l) {
    var h = -1, $ = l == null ? 0 : l.length;
    for (this.clear(); ++h < $; ) {
      var T = l[h];
      this.set(T[0], T[1]);
    }
  }
  function gr() {
    this.__data__ = pt ? pt(null) : {}, this.size = 0;
  }
  function mr(l) {
    var h = this.has(l) && delete this.__data__[l];
    return this.size -= h ? 1 : 0, h;
  }
  function vr(l) {
    var h = this.__data__;
    if (pt) {
      var $ = h[l];
      return $ === r ? void 0 : $;
    }
    return Ee.call(h, l) ? h[l] : void 0;
  }
  function br(l) {
    var h = this.__data__;
    return pt ? h[l] !== void 0 : Ee.call(h, l);
  }
  function yr(l, h) {
    var $ = this.__data__;
    return this.size += this.has(l) ? 0 : 1, $[l] = pt && h === void 0 ? r : h, this;
  }
  le.prototype.clear = gr, le.prototype.delete = mr, le.prototype.get = vr, le.prototype.has = br, le.prototype.set = yr;
  function fe(l) {
    var h = -1, $ = l == null ? 0 : l.length;
    for (this.clear(); ++h < $; ) {
      var T = l[h];
      this.set(T[0], T[1]);
    }
  }
  function $r() {
    this.__data__ = [], this.size = 0;
  }
  function kr(l) {
    var h = this.__data__, $ = Xt(h, l);
    if ($ < 0)
      return !1;
    var T = h.length - 1;
    return $ == T ? h.pop() : St.call(h, $, 1), --this.size, !0;
  }
  function wr(l) {
    var h = this.__data__, $ = Xt(h, l);
    return $ < 0 ? void 0 : h[$][1];
  }
  function Cr(l) {
    return Xt(this.__data__, l) > -1;
  }
  function Ar(l, h) {
    var $ = this.__data__, T = Xt($, l);
    return T < 0 ? (++this.size, $.push([l, h])) : $[T][1] = h, this;
  }
  fe.prototype.clear = $r, fe.prototype.delete = kr, fe.prototype.get = wr, fe.prototype.has = Cr, fe.prototype.set = Ar;
  function $e(l) {
    var h = -1, $ = l == null ? 0 : l.length;
    for (this.clear(); ++h < $; ) {
      var T = l[h];
      this.set(T[0], T[1]);
    }
  }
  function Er() {
    this.size = 0, this.__data__ = {
      hash: new le(),
      map: new (_t || fe)(),
      string: new le()
    };
  }
  function Sr(l) {
    var h = Pe(this, l).delete(l);
    return this.size -= h ? 1 : 0, h;
  }
  function Tr(l) {
    return Pe(this, l).get(l);
  }
  function _r(l) {
    return Pe(this, l).has(l);
  }
  function Nr(l, h) {
    var $ = Pe(this, l), T = $.size;
    return $.set(l, h), this.size += $.size == T ? 0 : 1, this;
  }
  $e.prototype.clear = Er, $e.prototype.delete = Sr, $e.prototype.get = Tr, $e.prototype.has = _r, $e.prototype.set = Nr;
  function Wt(l) {
    var h = -1, $ = l == null ? 0 : l.length;
    for (this.__data__ = new $e(); ++h < $; )
      this.add(l[h]);
  }
  function yn(l) {
    return this.__data__.set(l, r), this;
  }
  function Zt(l) {
    return this.__data__.has(l);
  }
  Wt.prototype.add = Wt.prototype.push = yn, Wt.prototype.has = Zt;
  function Ke(l) {
    var h = this.__data__ = new fe(l);
    this.size = h.size;
  }
  function Ts() {
    this.__data__ = new fe(), this.size = 0;
  }
  function Ir(l) {
    var h = this.__data__, $ = h.delete(l);
    return this.size = h.size, $;
  }
  function Lr(l) {
    return this.__data__.get(l);
  }
  function qr(l) {
    return this.__data__.has(l);
  }
  function Or(l, h) {
    var $ = this.__data__;
    if ($ instanceof fe) {
      var T = $.__data__;
      if (!_t || T.length < s - 1)
        return T.push([l, h]), this.size = ++$.size, this;
      $ = this.__data__ = new $e(T);
    }
    return $.set(l, h), this.size = $.size, this;
  }
  Ke.prototype.clear = Ts, Ke.prototype.delete = Ir, Ke.prototype.get = Lr, Ke.prototype.has = qr, Ke.prototype.set = Or;
  function Pr(l, h) {
    var $ = Yt(l), T = !$ && An(l), K = !$ && !T && Qt(l), z = !$ && !T && !K && Tn(l), Y = $ || T || K || z, X = Y ? lr(l.length, String) : [], re = X.length;
    for (var Q in l)
      Ee.call(l, Q) && !(Y && // Safari 9 has enumerable `arguments.length` in strict mode.
      (Q == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
      K && (Q == "offset" || Q == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
      z && (Q == "buffer" || Q == "byteLength" || Q == "byteOffset") || // Skip index properties.
      Vr(Q, re))) && X.push(Q);
    return X;
  }
  function Xt(l, h) {
    for (var $ = l.length; $--; )
      if (Cn(l[$][0], h))
        return $;
    return -1;
  }
  function _s(l, h, $) {
    var T = h(l);
    return Yt(l) ? T : vs(T, $(l));
  }
  function Nt(l) {
    return l == null ? l === void 0 ? tt : _ : Oe && Oe in Object(l) ? rt(l) : wn(l);
  }
  function $n(l) {
    return Ze(l) && Nt(l) == o;
  }
  function kn(l, h, $, T, K) {
    return l === h ? !0 : l == null || h == null || !Ze(l) && !Ze(h) ? l !== l && h !== h : Dr(l, h, $, T, kn, K);
  }
  function Dr(l, h, $, T, K, z) {
    var Y = Yt(l), X = Yt(h), re = Y ? u : We(l), Q = X ? u : We(h);
    re = re == o ? O : re, Q = Q == o ? O : Q;
    var pe = re == O, ke = Q == O, ae = re == Q;
    if (ae && Qt(l)) {
      if (!Qt(h))
        return !1;
      Y = !0, pe = !1;
    }
    if (ae && !pe)
      return z || (z = new Ke()), Y || Tn(l) ? Ns(l, h, $, T, K, z) : Fr(l, h, re, $, T, K, z);
    if (!($ & i)) {
      var he = pe && Ee.call(l, "__wrapped__"), ue = ke && Ee.call(h, "__wrapped__");
      if (he || ue) {
        var ht = he ? l.value() : l, it = ue ? h.value() : h;
        return z || (z = new Ke()), K(ht, it, $, T, z);
      }
    }
    return ae ? (z || (z = new Ke()), Ur(l, h, $, T, K, z)) : !1;
  }
  function Rr(l) {
    if (!Sn(l) || zr(l))
      return !1;
    var h = En(l) ? cr : Le;
    return h.test(ve(l));
  }
  function Br(l) {
    return Ze(l) && Ls(l.length) && !!x[Nt(l)];
  }
  function Mr(l) {
    if (!Gr(l))
      return Tt(l);
    var h = [];
    for (var $ in Object(l))
      Ee.call(l, $) && $ != "constructor" && h.push($);
    return h;
  }
  function Ns(l, h, $, T, K, z) {
    var Y = $ & i, X = l.length, re = h.length;
    if (X != re && !(Y && re > X))
      return !1;
    var Q = z.get(l);
    if (Q && z.get(h))
      return Q == h;
    var pe = -1, ke = !0, ae = $ & a ? new Wt() : void 0;
    for (z.set(l, h), z.set(h, l); ++pe < X; ) {
      var he = l[pe], ue = h[pe];
      if (T)
        var ht = Y ? T(ue, he, pe, h, l, z) : T(he, ue, pe, l, h, z);
      if (ht !== void 0) {
        if (ht)
          continue;
        ke = !1;
        break;
      }
      if (ae) {
        if (!cn(h, function(it, Lt) {
          if (!jt(ae, Lt) && (he === it || K(he, it, $, T, z)))
            return ae.push(Lt);
        })) {
          ke = !1;
          break;
        }
      } else if (!(he === ue || K(he, ue, $, T, z))) {
        ke = !1;
        break;
      }
    }
    return z.delete(l), z.delete(h), ke;
  }
  function Fr(l, h, $, T, K, z, Y) {
    switch ($) {
      case At:
        if (l.byteLength != h.byteLength || l.byteOffset != h.byteOffset)
          return !1;
        l = l.buffer, h = h.buffer;
      case Ct:
        return !(l.byteLength != h.byteLength || !z(new mn(l), new mn(h)));
      case g:
      case k:
      case S:
        return Cn(+l, +h);
      case y:
        return l.name == h.name && l.message == h.message;
      case M:
      case Z:
        return l == h + "";
      case E:
        var X = fn;
      case G:
        var re = T & i;
        if (X || (X = Ge), l.size != h.size && !re)
          return !1;
        var Q = Y.get(l);
        if (Q)
          return Q == h;
        T |= a, Y.set(l, h);
        var pe = Ns(X(l), X(h), T, K, z, Y);
        return Y.delete(l), pe;
      case te:
        if (Ss)
          return Ss.call(l) == Ss.call(h);
    }
    return !1;
  }
  function Ur(l, h, $, T, K, z) {
    var Y = $ & i, X = It(l), re = X.length, Q = It(h), pe = Q.length;
    if (re != pe && !Y)
      return !1;
    for (var ke = re; ke--; ) {
      var ae = X[ke];
      if (!(Y ? ae in h : Ee.call(h, ae)))
        return !1;
    }
    var he = z.get(l);
    if (he && z.get(h))
      return he == h;
    var ue = !0;
    z.set(l, h), z.set(h, l);
    for (var ht = Y; ++ke < re; ) {
      ae = X[ke];
      var it = l[ae], Lt = h[ae];
      if (T)
        var aa = Y ? T(Lt, it, ae, h, l, z) : T(it, Lt, ae, l, h, z);
      if (!(aa === void 0 ? it === Lt || K(it, Lt, $, T, z) : aa)) {
        ue = !1;
        break;
      }
      ht || (ht = ae == "constructor");
    }
    if (ue && !ht) {
      var _n = l.constructor, Nn = h.constructor;
      _n != Nn && "constructor" in l && "constructor" in h && !(typeof _n == "function" && _n instanceof _n && typeof Nn == "function" && Nn instanceof Nn) && (ue = !1);
    }
    return z.delete(l), z.delete(h), ue;
  }
  function It(l) {
    return _s(l, qs, jr);
  }
  function Pe(l, h) {
    var $ = l.__data__;
    return Hr(h) ? $[typeof h == "string" ? "string" : "hash"] : $.map;
  }
  function nt(l, h) {
    var $ = bs(l, h);
    return Rr($) ? $ : void 0;
  }
  function rt(l) {
    var h = Ee.call(l, Oe), $ = l[Oe];
    try {
      l[Oe] = void 0;
      var T = !0;
    } catch {
    }
    var K = gn.call(l);
    return T && (h ? l[Oe] = $ : delete l[Oe]), K;
  }
  var jr = Kt ? function(l) {
    return l == null ? [] : (l = Object(l), dn(Kt(l), function(h) {
      return Gt.call(l, h);
    }));
  } : Wr, We = Nt;
  (ws && We(new ws(new ArrayBuffer(1))) != At || _t && We(new _t()) != E || Cs && We(Cs.resolve()) != D || As && We(new As()) != G || Es && We(new Es()) != ft) && (We = function(l) {
    var h = Nt(l), $ = h == O ? l.constructor : void 0, T = $ ? ve($) : "";
    if (T)
      switch (T) {
        case vn:
          return At;
        case st:
          return E;
        case fr:
          return D;
        case pr:
          return G;
        case hr:
          return ft;
      }
    return h;
  });
  function Vr(l, h) {
    return h = h ?? n, !!h && (typeof l == "number" || rn.test(l)) && l > -1 && l % 1 == 0 && l < h;
  }
  function Hr(l) {
    var h = typeof l;
    return h == "string" || h == "number" || h == "symbol" || h == "boolean" ? l !== "__proto__" : l === null;
  }
  function zr(l) {
    return !!hn && hn in l;
  }
  function Gr(l) {
    var h = l && l.constructor, $ = typeof h == "function" && h.prototype || Et;
    return l === $;
  }
  function wn(l) {
    return gn.call(l);
  }
  function ve(l) {
    if (l != null) {
      try {
        return ys.call(l);
      } catch {
      }
      try {
        return l + "";
      } catch {
      }
    }
    return "";
  }
  function Cn(l, h) {
    return l === h || l !== l && h !== h;
  }
  var An = $n(/* @__PURE__ */ function() {
    return arguments;
  }()) ? $n : function(l) {
    return Ze(l) && Ee.call(l, "callee") && !Gt.call(l, "callee");
  }, Yt = Array.isArray;
  function Is(l) {
    return l != null && Ls(l.length) && !En(l);
  }
  var Qt = ks || Zr;
  function Kr(l, h) {
    return kn(l, h);
  }
  function En(l) {
    if (!Sn(l))
      return !1;
    var h = Nt(l);
    return h == b || h == v || h == p || h == U;
  }
  function Ls(l) {
    return typeof l == "number" && l > -1 && l % 1 == 0 && l <= n;
  }
  function Sn(l) {
    var h = typeof l;
    return l != null && (h == "object" || h == "function");
  }
  function Ze(l) {
    return l != null && typeof l == "object";
  }
  var Tn = ms ? ur(ms) : Br;
  function qs(l) {
    return Is(l) ? Pr(l) : Mr(l);
  }
  function Wr() {
    return [];
  }
  function Zr() {
    return !1;
  }
  t.exports = Kr;
})(Hn, Hn.exports);
var Xo = Hn.exports, Zi = {};
Object.defineProperty(Zi, "__esModule", { value: !0 });
const Lk = Zo, qk = Xo;
var wi;
(function(t) {
  function e(a = {}, n = {}, o = !1) {
    typeof a != "object" && (a = {}), typeof n != "object" && (n = {});
    let u = Lk(n);
    o || (u = Object.keys(u).reduce((p, g) => (u[g] != null && (p[g] = u[g]), p), {}));
    for (const p in a)
      a[p] !== void 0 && n[p] === void 0 && (u[p] = a[p]);
    return Object.keys(u).length > 0 ? u : void 0;
  }
  t.compose = e;
  function s(a = {}, n = {}) {
    typeof a != "object" && (a = {}), typeof n != "object" && (n = {});
    const o = Object.keys(a).concat(Object.keys(n)).reduce((u, p) => (qk(a[p], n[p]) || (u[p] = n[p] === void 0 ? null : n[p]), u), {});
    return Object.keys(o).length > 0 ? o : void 0;
  }
  t.diff = s;
  function r(a = {}, n = {}) {
    a = a || {};
    const o = Object.keys(n).reduce((u, p) => (n[p] !== a[p] && a[p] !== void 0 && (u[p] = n[p]), u), {});
    return Object.keys(a).reduce((u, p) => (a[p] !== n[p] && n[p] === void 0 && (u[p] = null), u), o);
  }
  t.invert = r;
  function i(a, n, o = !1) {
    if (typeof a != "object")
      return n;
    if (typeof n != "object")
      return;
    if (!o)
      return n;
    const u = Object.keys(n).reduce((p, g) => (a[g] === void 0 && (p[g] = n[g]), p), {});
    return Object.keys(u).length > 0 ? u : void 0;
  }
  t.transform = i;
})(wi || (wi = {}));
Zi.default = wi;
var Qn = {};
Object.defineProperty(Qn, "__esModule", { value: !0 });
var Ci;
(function(t) {
  function e(s) {
    return typeof s.delete == "number" ? s.delete : typeof s.retain == "number" ? s.retain : typeof s.retain == "object" && s.retain !== null ? 1 : typeof s.insert == "string" ? s.insert.length : 1;
  }
  t.length = e;
})(Ci || (Ci = {}));
Qn.default = Ci;
var Xi = {};
Object.defineProperty(Xi, "__esModule", { value: !0 });
const Fa = Qn;
class Ok {
  constructor(e) {
    this.ops = e, this.index = 0, this.offset = 0;
  }
  hasNext() {
    return this.peekLength() < 1 / 0;
  }
  next(e) {
    e || (e = 1 / 0);
    const s = this.ops[this.index];
    if (s) {
      const r = this.offset, i = Fa.default.length(s);
      if (e >= i - r ? (e = i - r, this.index += 1, this.offset = 0) : this.offset += e, typeof s.delete == "number")
        return { delete: e };
      {
        const a = {};
        return s.attributes && (a.attributes = s.attributes), typeof s.retain == "number" ? a.retain = e : typeof s.retain == "object" && s.retain !== null ? a.retain = s.retain : typeof s.insert == "string" ? a.insert = s.insert.substr(r, e) : a.insert = s.insert, a;
      }
    } else
      return { retain: 1 / 0 };
  }
  peek() {
    return this.ops[this.index];
  }
  peekLength() {
    return this.ops[this.index] ? Fa.default.length(this.ops[this.index]) - this.offset : 1 / 0;
  }
  peekType() {
    const e = this.ops[this.index];
    return e ? typeof e.delete == "number" ? "delete" : typeof e.retain == "number" || typeof e.retain == "object" && e.retain !== null ? "retain" : "insert" : "retain";
  }
  rest() {
    if (this.hasNext()) {
      if (this.offset === 0)
        return this.ops.slice(this.index);
      {
        const e = this.offset, s = this.index, r = this.next(), i = this.ops.slice(this.index);
        return this.offset = e, this.index = s, [r].concat(i);
      }
    } else return [];
  }
}
Xi.default = Ok;
(function(t, e) {
  Object.defineProperty(e, "__esModule", { value: !0 }), e.AttributeMap = e.OpIterator = e.Op = void 0;
  const s = Ik, r = Zo, i = Xo, a = Zi;
  e.AttributeMap = a.default;
  const n = Qn;
  e.Op = n.default;
  const o = Xi;
  e.OpIterator = o.default;
  const u = "\0", p = (k, y) => {
    if (typeof k != "object" || k === null)
      throw new Error(`cannot retain a ${typeof k}`);
    if (typeof y != "object" || y === null)
      throw new Error(`cannot retain a ${typeof y}`);
    const b = Object.keys(k)[0];
    if (!b || b !== Object.keys(y)[0])
      throw new Error(`embed types not matched: ${b} != ${Object.keys(y)[0]}`);
    return [b, k[b], y[b]];
  };
  class g {
    constructor(y) {
      Array.isArray(y) ? this.ops = y : y != null && Array.isArray(y.ops) ? this.ops = y.ops : this.ops = [];
    }
    static registerEmbed(y, b) {
      this.handlers[y] = b;
    }
    static unregisterEmbed(y) {
      delete this.handlers[y];
    }
    static getHandler(y) {
      const b = this.handlers[y];
      if (!b)
        throw new Error(`no handlers for embed type "${y}"`);
      return b;
    }
    insert(y, b) {
      const v = {};
      return typeof y == "string" && y.length === 0 ? this : (v.insert = y, b != null && typeof b == "object" && Object.keys(b).length > 0 && (v.attributes = b), this.push(v));
    }
    delete(y) {
      return y <= 0 ? this : this.push({ delete: y });
    }
    retain(y, b) {
      if (typeof y == "number" && y <= 0)
        return this;
      const v = { retain: y };
      return b != null && typeof b == "object" && Object.keys(b).length > 0 && (v.attributes = b), this.push(v);
    }
    push(y) {
      let b = this.ops.length, v = this.ops[b - 1];
      if (y = r(y), typeof v == "object") {
        if (typeof y.delete == "number" && typeof v.delete == "number")
          return this.ops[b - 1] = { delete: v.delete + y.delete }, this;
        if (typeof v.delete == "number" && y.insert != null && (b -= 1, v = this.ops[b - 1], typeof v != "object"))
          return this.ops.unshift(y), this;
        if (i(y.attributes, v.attributes)) {
          if (typeof y.insert == "string" && typeof v.insert == "string")
            return this.ops[b - 1] = { insert: v.insert + y.insert }, typeof y.attributes == "object" && (this.ops[b - 1].attributes = y.attributes), this;
          if (typeof y.retain == "number" && typeof v.retain == "number")
            return this.ops[b - 1] = { retain: v.retain + y.retain }, typeof y.attributes == "object" && (this.ops[b - 1].attributes = y.attributes), this;
        }
      }
      return b === this.ops.length ? this.ops.push(y) : this.ops.splice(b, 0, y), this;
    }
    chop() {
      const y = this.ops[this.ops.length - 1];
      return y && typeof y.retain == "number" && !y.attributes && this.ops.pop(), this;
    }
    filter(y) {
      return this.ops.filter(y);
    }
    forEach(y) {
      this.ops.forEach(y);
    }
    map(y) {
      return this.ops.map(y);
    }
    partition(y) {
      const b = [], v = [];
      return this.forEach((E) => {
        (y(E) ? b : v).push(E);
      }), [b, v];
    }
    reduce(y, b) {
      return this.ops.reduce(y, b);
    }
    changeLength() {
      return this.reduce((y, b) => b.insert ? y + n.default.length(b) : b.delete ? y - b.delete : y, 0);
    }
    length() {
      return this.reduce((y, b) => y + n.default.length(b), 0);
    }
    slice(y = 0, b = 1 / 0) {
      const v = [], E = new o.default(this.ops);
      let S = 0;
      for (; S < b && E.hasNext(); ) {
        let _;
        S < y ? _ = E.next(y - S) : (_ = E.next(b - S), v.push(_)), S += n.default.length(_);
      }
      return new g(v);
    }
    compose(y) {
      const b = new o.default(this.ops), v = new o.default(y.ops), E = [], S = v.peek();
      if (S != null && typeof S.retain == "number" && S.attributes == null) {
        let O = S.retain;
        for (; b.peekType() === "insert" && b.peekLength() <= O; )
          O -= b.peekLength(), E.push(b.next());
        S.retain - O > 0 && v.next(S.retain - O);
      }
      const _ = new g(E);
      for (; b.hasNext() || v.hasNext(); )
        if (v.peekType() === "insert")
          _.push(v.next());
        else if (b.peekType() === "delete")
          _.push(b.next());
        else {
          const O = Math.min(b.peekLength(), v.peekLength()), D = b.next(O), U = v.next(O);
          if (U.retain) {
            const M = {};
            if (typeof D.retain == "number")
              M.retain = typeof U.retain == "number" ? O : U.retain;
            else if (typeof U.retain == "number")
              D.retain == null ? M.insert = D.insert : M.retain = D.retain;
            else {
              const Z = D.retain == null ? "insert" : "retain", [te, tt, ft] = p(D[Z], U.retain), Ct = g.getHandler(te);
              M[Z] = {
                [te]: Ct.compose(tt, ft, Z === "retain")
              };
            }
            const G = a.default.compose(D.attributes, U.attributes, typeof D.retain == "number");
            if (G && (M.attributes = G), _.push(M), !v.hasNext() && i(_.ops[_.ops.length - 1], M)) {
              const Z = new g(b.rest());
              return _.concat(Z).chop();
            }
          } else typeof U.delete == "number" && (typeof D.retain == "number" || typeof D.retain == "object" && D.retain !== null) && _.push(U);
        }
      return _.chop();
    }
    concat(y) {
      const b = new g(this.ops.slice());
      return y.ops.length > 0 && (b.push(y.ops[0]), b.ops = b.ops.concat(y.ops.slice(1))), b;
    }
    diff(y, b) {
      if (this.ops === y.ops)
        return new g();
      const v = [this, y].map((D) => D.map((U) => {
        if (U.insert != null)
          return typeof U.insert == "string" ? U.insert : u;
        const M = D === y ? "on" : "with";
        throw new Error("diff() called " + M + " non-document");
      }).join("")), E = new g(), S = s(v[0], v[1], b, !0), _ = new o.default(this.ops), O = new o.default(y.ops);
      return S.forEach((D) => {
        let U = D[1].length;
        for (; U > 0; ) {
          let M = 0;
          switch (D[0]) {
            case s.INSERT:
              M = Math.min(O.peekLength(), U), E.push(O.next(M));
              break;
            case s.DELETE:
              M = Math.min(U, _.peekLength()), _.next(M), E.delete(M);
              break;
            case s.EQUAL:
              M = Math.min(_.peekLength(), O.peekLength(), U);
              const G = _.next(M), Z = O.next(M);
              i(G.insert, Z.insert) ? E.retain(M, a.default.diff(G.attributes, Z.attributes)) : E.push(Z).delete(M);
              break;
          }
          U -= M;
        }
      }), E.chop();
    }
    eachLine(y, b = `
`) {
      const v = new o.default(this.ops);
      let E = new g(), S = 0;
      for (; v.hasNext(); ) {
        if (v.peekType() !== "insert")
          return;
        const _ = v.peek(), O = n.default.length(_) - v.peekLength(), D = typeof _.insert == "string" ? _.insert.indexOf(b, O) - O : -1;
        if (D < 0)
          E.push(v.next());
        else if (D > 0)
          E.push(v.next(D));
        else {
          if (y(E, v.next(1).attributes || {}, S) === !1)
            return;
          S += 1, E = new g();
        }
      }
      E.length() > 0 && y(E, {}, S);
    }
    invert(y) {
      const b = new g();
      return this.reduce((v, E) => {
        if (E.insert)
          b.delete(n.default.length(E));
        else {
          if (typeof E.retain == "number" && E.attributes == null)
            return b.retain(E.retain), v + E.retain;
          if (E.delete || typeof E.retain == "number") {
            const S = E.delete || E.retain;
            return y.slice(v, v + S).forEach((O) => {
              E.delete ? b.push(O) : E.retain && E.attributes && b.retain(n.default.length(O), a.default.invert(E.attributes, O.attributes));
            }), v + S;
          } else if (typeof E.retain == "object" && E.retain !== null) {
            const S = y.slice(v, v + 1), _ = new o.default(S.ops).next(), [O, D, U] = p(E.retain, _.insert), M = g.getHandler(O);
            return b.retain({ [O]: M.invert(D, U) }, a.default.invert(E.attributes, _.attributes)), v + 1;
          }
        }
        return v;
      }, 0), b.chop();
    }
    transform(y, b = !1) {
      if (b = !!b, typeof y == "number")
        return this.transformPosition(y, b);
      const v = y, E = new o.default(this.ops), S = new o.default(v.ops), _ = new g();
      for (; E.hasNext() || S.hasNext(); )
        if (E.peekType() === "insert" && (b || S.peekType() !== "insert"))
          _.retain(n.default.length(E.next()));
        else if (S.peekType() === "insert")
          _.push(S.next());
        else {
          const O = Math.min(E.peekLength(), S.peekLength()), D = E.next(O), U = S.next(O);
          if (D.delete)
            continue;
          if (U.delete)
            _.push(U);
          else {
            const M = D.retain, G = U.retain;
            let Z = typeof G == "object" && G !== null ? G : O;
            if (typeof M == "object" && M !== null && typeof G == "object" && G !== null) {
              const te = Object.keys(M)[0];
              if (te === Object.keys(G)[0]) {
                const tt = g.getHandler(te);
                tt && (Z = {
                  [te]: tt.transform(M[te], G[te], b)
                });
              }
            }
            _.retain(Z, a.default.transform(D.attributes, U.attributes, b));
          }
        }
      return _.chop();
    }
    transformPosition(y, b = !1) {
      b = !!b;
      const v = new o.default(this.ops);
      let E = 0;
      for (; v.hasNext() && E <= y; ) {
        const S = v.peekLength(), _ = v.peekType();
        if (v.next(), _ === "delete") {
          y -= Math.min(S, y - E);
          continue;
        } else _ === "insert" && (E < y || !b) && (y += S);
        E += S;
      }
      return y;
    }
  }
  g.Op = n.default, g.OpIterator = o.default, g.AttributeMap = a.default, g.handlers = {}, e.default = g, t.exports = g, t.exports.default = g;
})(ki, ki.exports);
var Ie = ki.exports;
const j = /* @__PURE__ */ Ho(Ie);
class He extends Ae {
  static value() {
  }
  optimize() {
    (this.prev || this.next) && this.remove();
  }
  length() {
    return 0;
  }
  value() {
    return "";
  }
}
He.blotName = "break";
He.tagName = "BR";
let je = class extends jn {
};
const Pk = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
};
function Jn(t) {
  return t.replace(/[&<>"']/g, (e) => Pk[e]);
}
const Xe = class Xe extends zi {
  static compare(e, s) {
    const r = Xe.order.indexOf(e), i = Xe.order.indexOf(s);
    return r >= 0 || i >= 0 ? r - i : e === s ? 0 : e < s ? -1 : 1;
  }
  formatAt(e, s, r, i) {
    if (Xe.compare(this.statics.blotName, r) < 0 && this.scroll.query(r, V.BLOT)) {
      const a = this.isolate(e, s);
      i && a.wrap(r, i);
    } else
      super.formatAt(e, s, r, i);
  }
  optimize(e) {
    if (super.optimize(e), this.parent instanceof Xe && Xe.compare(this.statics.blotName, this.parent.statics.blotName) > 0) {
      const s = this.parent.isolate(this.offset(), this.length());
      this.moveChildren(s), s.wrap(this);
    }
  }
};
B(Xe, "allowedChildren", [Xe, He, Ae, je]), // Lower index means deeper in the DOM tree, since not found (-1) is for embeds
B(Xe, "order", [
  "cursor",
  "inline",
  // Must be lower
  "link",
  // Chrome wants <a> to be lower
  "underline",
  "strike",
  "italic",
  "bold",
  "script",
  "code"
  // Must be higher
]);
let xe = Xe;
const Ua = 1;
class ce extends Gs {
  constructor() {
    super(...arguments);
    B(this, "cache", {});
  }
  delta() {
    return this.cache.delta == null && (this.cache.delta = Yo(this)), this.cache.delta;
  }
  deleteAt(s, r) {
    super.deleteAt(s, r), this.cache = {};
  }
  formatAt(s, r, i, a) {
    r <= 0 || (this.scroll.query(i, V.BLOCK) ? s + r === this.length() && this.format(i, a) : super.formatAt(s, Math.min(r, this.length() - s - 1), i, a), this.cache = {});
  }
  insertAt(s, r, i) {
    if (i != null) {
      super.insertAt(s, r, i), this.cache = {};
      return;
    }
    if (r.length === 0) return;
    const a = r.split(`
`), n = a.shift();
    n.length > 0 && (s < this.length() - 1 || this.children.tail == null ? super.insertAt(Math.min(s, this.length() - 1), n) : this.children.tail.insertAt(this.children.tail.length(), n), this.cache = {});
    let o = this;
    a.reduce((u, p) => (o = o.split(u, !0), o.insertAt(0, p), p.length), s + n.length);
  }
  insertBefore(s, r) {
    const {
      head: i
    } = this.children;
    super.insertBefore(s, r), i instanceof He && i.remove(), this.cache = {};
  }
  length() {
    return this.cache.length == null && (this.cache.length = super.length() + Ua), this.cache.length;
  }
  moveChildren(s, r) {
    super.moveChildren(s, r), this.cache = {};
  }
  optimize(s) {
    super.optimize(s), this.cache = {};
  }
  path(s) {
    return super.path(s, !0);
  }
  removeChild(s) {
    super.removeChild(s), this.cache = {};
  }
  split(s) {
    let r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1;
    if (r && (s === 0 || s >= this.length() - Ua)) {
      const a = this.clone();
      return s === 0 ? (this.parent.insertBefore(a, this), this) : (this.parent.insertBefore(a, this.next), a);
    }
    const i = super.split(s, r);
    return this.cache = {}, i;
  }
}
ce.blotName = "block";
ce.tagName = "P";
ce.defaultChild = He;
ce.allowedChildren = [He, xe, Ae, je];
class Ne extends Ae {
  attach() {
    super.attach(), this.attributes = new Wn(this.domNode);
  }
  delta() {
    return new j().insert(this.value(), {
      ...this.formats(),
      ...this.attributes.values()
    });
  }
  format(e, s) {
    const r = this.scroll.query(e, V.BLOCK_ATTRIBUTE);
    r != null && this.attributes.attribute(r, s);
  }
  formatAt(e, s, r, i) {
    this.format(r, i);
  }
  insertAt(e, s, r) {
    if (r != null) {
      super.insertAt(e, s, r);
      return;
    }
    const i = s.split(`
`), a = i.pop(), n = i.map((u) => {
      const p = this.scroll.create(ce.blotName);
      return p.insertAt(0, u), p;
    }), o = this.split(e);
    n.forEach((u) => {
      this.parent.insertBefore(u, o);
    }), a && this.parent.insertBefore(this.scroll.create("text", a), o);
  }
}
Ne.scope = V.BLOCK_BLOT;
function Yo(t) {
  let e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !0;
  return t.descendants(ge).reduce((s, r) => r.length() === 0 ? s : s.insert(r.value(), Te(r, {}, e)), new j()).insert(`
`, Te(t));
}
function Te(t) {
  let e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, s = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : !0;
  return t == null || ("formats" in t && typeof t.formats == "function" && (e = {
    ...e,
    ...t.formats()
  }, s && delete e["code-token"]), t.parent == null || t.parent.statics.blotName === "scroll" || t.parent.statics.scope !== t.statics.scope) ? e : Te(t.parent, e, s);
}
const Se = class Se extends Ae {
  // Zero width no break space
  static value() {
  }
  constructor(e, s, r) {
    super(e, s), this.selection = r, this.textNode = document.createTextNode(Se.CONTENTS), this.domNode.appendChild(this.textNode), this.savedLength = 0;
  }
  detach() {
    this.parent != null && this.parent.removeChild(this);
  }
  format(e, s) {
    if (this.savedLength !== 0) {
      super.format(e, s);
      return;
    }
    let r = this, i = 0;
    for (; r != null && r.statics.scope !== V.BLOCK_BLOT; )
      i += r.offset(r.parent), r = r.parent;
    r != null && (this.savedLength = Se.CONTENTS.length, r.optimize(), r.formatAt(i, Se.CONTENTS.length, e, s), this.savedLength = 0);
  }
  index(e, s) {
    return e === this.textNode ? 0 : super.index(e, s);
  }
  length() {
    return this.savedLength;
  }
  position() {
    return [this.textNode, this.textNode.data.length];
  }
  remove() {
    super.remove(), this.parent = null;
  }
  restore() {
    if (this.selection.composing || this.parent == null) return null;
    const e = this.selection.getNativeRange();
    for (; this.domNode.lastChild != null && this.domNode.lastChild !== this.textNode; )
      this.domNode.parentNode.insertBefore(this.domNode.lastChild, this.domNode);
    const s = this.prev instanceof je ? this.prev : null, r = s ? s.length() : 0, i = this.next instanceof je ? this.next : null, a = i ? i.text : "", {
      textNode: n
    } = this, o = n.data.split(Se.CONTENTS).join("");
    n.data = Se.CONTENTS;
    let u;
    if (s)
      u = s, (o || i) && (s.insertAt(s.length(), o + a), i && i.remove());
    else if (i)
      u = i, i.insertAt(0, o);
    else {
      const p = document.createTextNode(o);
      u = this.scroll.create(p), this.parent.insertBefore(u, this);
    }
    if (this.remove(), e) {
      const p = (y, b) => s && y === s.domNode ? b : y === n ? r + b - 1 : i && y === i.domNode ? r + o.length + b : null, g = p(e.start.node, e.start.offset), k = p(e.end.node, e.end.offset);
      if (g !== null && k !== null)
        return {
          startNode: u.domNode,
          startOffset: g,
          endNode: u.domNode,
          endOffset: k
        };
    }
    return null;
  }
  update(e, s) {
    if (e.some((r) => r.type === "characterData" && r.target === this.textNode)) {
      const r = this.restore();
      r && (s.range = r);
    }
  }
  // Avoid .ql-cursor being a descendant of `<a/>`.
  // The reason is Safari pushes down `<a/>` on text insertion.
  // That will cause DOM nodes not sync with the model.
  //
  // For example ({I} is the caret), given the markup:
  //    <a><span class="ql-cursor">\uFEFF{I}</span></a>
  // When typing a char "x", `<a/>` will be pushed down inside the `<span>` first:
  //    <span class="ql-cursor"><a>\uFEFF{I}</a></span>
  // And then "x" will be inserted after `<a/>`:
  //    <span class="ql-cursor"><a>\uFEFF</a>d{I}</span>
  optimize(e) {
    super.optimize(e);
    let {
      parent: s
    } = this;
    for (; s; ) {
      if (s.domNode.tagName === "A") {
        this.savedLength = Se.CONTENTS.length, s.isolate(this.offset(s), this.length()).unwrap(), this.savedLength = 0;
        break;
      }
      s = s.parent;
    }
  }
  value() {
    return "";
  }
};
B(Se, "blotName", "cursor"), B(Se, "className", "ql-cursor"), B(Se, "tagName", "span"), B(Se, "CONTENTS", "\uFEFF");
let us = Se;
var Qo = { exports: {} };
(function(t) {
  var e = Object.prototype.hasOwnProperty, s = "~";
  function r() {
  }
  Object.create && (r.prototype = /* @__PURE__ */ Object.create(null), new r().__proto__ || (s = !1));
  function i(u, p, g) {
    this.fn = u, this.context = p, this.once = g || !1;
  }
  function a(u, p, g, k, y) {
    if (typeof g != "function")
      throw new TypeError("The listener must be a function");
    var b = new i(g, k || u, y), v = s ? s + p : p;
    return u._events[v] ? u._events[v].fn ? u._events[v] = [u._events[v], b] : u._events[v].push(b) : (u._events[v] = b, u._eventsCount++), u;
  }
  function n(u, p) {
    --u._eventsCount === 0 ? u._events = new r() : delete u._events[p];
  }
  function o() {
    this._events = new r(), this._eventsCount = 0;
  }
  o.prototype.eventNames = function() {
    var p = [], g, k;
    if (this._eventsCount === 0) return p;
    for (k in g = this._events)
      e.call(g, k) && p.push(s ? k.slice(1) : k);
    return Object.getOwnPropertySymbols ? p.concat(Object.getOwnPropertySymbols(g)) : p;
  }, o.prototype.listeners = function(p) {
    var g = s ? s + p : p, k = this._events[g];
    if (!k) return [];
    if (k.fn) return [k.fn];
    for (var y = 0, b = k.length, v = new Array(b); y < b; y++)
      v[y] = k[y].fn;
    return v;
  }, o.prototype.listenerCount = function(p) {
    var g = s ? s + p : p, k = this._events[g];
    return k ? k.fn ? 1 : k.length : 0;
  }, o.prototype.emit = function(p, g, k, y, b, v) {
    var E = s ? s + p : p;
    if (!this._events[E]) return !1;
    var S = this._events[E], _ = arguments.length, O, D;
    if (S.fn) {
      switch (S.once && this.removeListener(p, S.fn, void 0, !0), _) {
        case 1:
          return S.fn.call(S.context), !0;
        case 2:
          return S.fn.call(S.context, g), !0;
        case 3:
          return S.fn.call(S.context, g, k), !0;
        case 4:
          return S.fn.call(S.context, g, k, y), !0;
        case 5:
          return S.fn.call(S.context, g, k, y, b), !0;
        case 6:
          return S.fn.call(S.context, g, k, y, b, v), !0;
      }
      for (D = 1, O = new Array(_ - 1); D < _; D++)
        O[D - 1] = arguments[D];
      S.fn.apply(S.context, O);
    } else {
      var U = S.length, M;
      for (D = 0; D < U; D++)
        switch (S[D].once && this.removeListener(p, S[D].fn, void 0, !0), _) {
          case 1:
            S[D].fn.call(S[D].context);
            break;
          case 2:
            S[D].fn.call(S[D].context, g);
            break;
          case 3:
            S[D].fn.call(S[D].context, g, k);
            break;
          case 4:
            S[D].fn.call(S[D].context, g, k, y);
            break;
          default:
            if (!O) for (M = 1, O = new Array(_ - 1); M < _; M++)
              O[M - 1] = arguments[M];
            S[D].fn.apply(S[D].context, O);
        }
    }
    return !0;
  }, o.prototype.on = function(p, g, k) {
    return a(this, p, g, k, !1);
  }, o.prototype.once = function(p, g, k) {
    return a(this, p, g, k, !0);
  }, o.prototype.removeListener = function(p, g, k, y) {
    var b = s ? s + p : p;
    if (!this._events[b]) return this;
    if (!g)
      return n(this, b), this;
    var v = this._events[b];
    if (v.fn)
      v.fn === g && (!y || v.once) && (!k || v.context === k) && n(this, b);
    else {
      for (var E = 0, S = [], _ = v.length; E < _; E++)
        (v[E].fn !== g || y && !v[E].once || k && v[E].context !== k) && S.push(v[E]);
      S.length ? this._events[b] = S.length === 1 ? S[0] : S : n(this, b);
    }
    return this;
  }, o.prototype.removeAllListeners = function(p) {
    var g;
    return p ? (g = s ? s + p : p, this._events[g] && n(this, g)) : (this._events = new r(), this._eventsCount = 0), this;
  }, o.prototype.off = o.prototype.removeListener, o.prototype.addListener = o.prototype.on, o.prefixed = s, o.EventEmitter = o, t.exports = o;
})(Qo);
var Dk = Qo.exports;
const Rk = /* @__PURE__ */ Ho(Dk), Ai = /* @__PURE__ */ new WeakMap(), Ei = ["error", "warn", "log", "info"];
let Si = "warn";
function Jo(t) {
  if (Si && Ei.indexOf(t) <= Ei.indexOf(Si)) {
    for (var e = arguments.length, s = new Array(e > 1 ? e - 1 : 0), r = 1; r < e; r++)
      s[r - 1] = arguments[r];
    console[t](...s);
  }
}
function ct(t) {
  return Ei.reduce((e, s) => (e[s] = Jo.bind(console, s, t), e), {});
}
ct.level = (t) => {
  Si = t;
};
Jo.level = ct.level;
const ei = ct("quill:events"), Bk = ["selectionchange", "mousedown", "mouseup", "click"];
Bk.forEach((t) => {
  document.addEventListener(t, function() {
    for (var e = arguments.length, s = new Array(e), r = 0; r < e; r++)
      s[r] = arguments[r];
    Array.from(document.querySelectorAll(".ql-container")).forEach((i) => {
      const a = Ai.get(i);
      a && a.emitter && a.emitter.handleDOM(...s);
    });
  });
});
class F extends Rk {
  constructor() {
    super(), this.domListeners = {}, this.on("error", ei.error);
  }
  emit() {
    for (var e = arguments.length, s = new Array(e), r = 0; r < e; r++)
      s[r] = arguments[r];
    return ei.log.call(ei, ...s), super.emit(...s);
  }
  handleDOM(e) {
    for (var s = arguments.length, r = new Array(s > 1 ? s - 1 : 0), i = 1; i < s; i++)
      r[i - 1] = arguments[i];
    (this.domListeners[e.type] || []).forEach((a) => {
      let {
        node: n,
        handler: o
      } = a;
      (e.target === n || n.contains(e.target)) && o(e, ...r);
    });
  }
  listenDOM(e, s, r) {
    this.domListeners[e] || (this.domListeners[e] = []), this.domListeners[e].push({
      node: s,
      handler: r
    });
  }
}
B(F, "events", {
  EDITOR_CHANGE: "editor-change",
  SCROLL_BEFORE_UPDATE: "scroll-before-update",
  SCROLL_BLOT_MOUNT: "scroll-blot-mount",
  SCROLL_BLOT_UNMOUNT: "scroll-blot-unmount",
  SCROLL_OPTIMIZE: "scroll-optimize",
  SCROLL_UPDATE: "scroll-update",
  SCROLL_EMBED_UPDATE: "scroll-embed-update",
  SELECTION_CHANGE: "selection-change",
  TEXT_CHANGE: "text-change",
  COMPOSITION_BEFORE_START: "composition-before-start",
  COMPOSITION_START: "composition-start",
  COMPOSITION_BEFORE_END: "composition-before-end",
  COMPOSITION_END: "composition-end"
}), B(F, "sources", {
  API: "api",
  SILENT: "silent",
  USER: "user"
});
const ti = ct("quill:selection");
class Pt {
  constructor(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0;
    this.index = e, this.length = s;
  }
}
class Mk {
  constructor(e, s) {
    this.emitter = s, this.scroll = e, this.composing = !1, this.mouseDown = !1, this.root = this.scroll.domNode, this.cursor = this.scroll.create("cursor", this), this.savedRange = new Pt(0, 0), this.lastRange = this.savedRange, this.lastNative = null, this.handleComposition(), this.handleDragging(), this.emitter.listenDOM("selectionchange", document, () => {
      !this.mouseDown && !this.composing && setTimeout(this.update.bind(this, F.sources.USER), 1);
    }), this.emitter.on(F.events.SCROLL_BEFORE_UPDATE, () => {
      if (!this.hasFocus()) return;
      const r = this.getNativeRange();
      r != null && r.start.node !== this.cursor.textNode && this.emitter.once(F.events.SCROLL_UPDATE, (i, a) => {
        try {
          this.root.contains(r.start.node) && this.root.contains(r.end.node) && this.setNativeRange(r.start.node, r.start.offset, r.end.node, r.end.offset);
          const n = a.some((o) => o.type === "characterData" || o.type === "childList" || o.type === "attributes" && o.target === this.root);
          this.update(n ? F.sources.SILENT : i);
        } catch {
        }
      });
    }), this.emitter.on(F.events.SCROLL_OPTIMIZE, (r, i) => {
      if (i.range) {
        const {
          startNode: a,
          startOffset: n,
          endNode: o,
          endOffset: u
        } = i.range;
        this.setNativeRange(a, n, o, u), this.update(F.sources.SILENT);
      }
    }), this.update(F.sources.SILENT);
  }
  handleComposition() {
    this.emitter.on(F.events.COMPOSITION_BEFORE_START, () => {
      this.composing = !0;
    }), this.emitter.on(F.events.COMPOSITION_END, () => {
      if (this.composing = !1, this.cursor.parent) {
        const e = this.cursor.restore();
        if (!e) return;
        setTimeout(() => {
          this.setNativeRange(e.startNode, e.startOffset, e.endNode, e.endOffset);
        }, 1);
      }
    });
  }
  handleDragging() {
    this.emitter.listenDOM("mousedown", document.body, () => {
      this.mouseDown = !0;
    }), this.emitter.listenDOM("mouseup", document.body, () => {
      this.mouseDown = !1, this.update(F.sources.USER);
    });
  }
  focus() {
    this.hasFocus() || (this.root.focus({
      preventScroll: !0
    }), this.setRange(this.savedRange));
  }
  format(e, s) {
    this.scroll.update();
    const r = this.getNativeRange();
    if (!(r == null || !r.native.collapsed || this.scroll.query(e, V.BLOCK))) {
      if (r.start.node !== this.cursor.textNode) {
        const i = this.scroll.find(r.start.node, !1);
        if (i == null) return;
        if (i instanceof ge) {
          const a = i.split(r.start.offset);
          i.parent.insertBefore(this.cursor, a);
        } else
          i.insertBefore(this.cursor, r.start.node);
        this.cursor.attach();
      }
      this.cursor.format(e, s), this.scroll.optimize(), this.setNativeRange(this.cursor.textNode, this.cursor.textNode.data.length), this.update();
    }
  }
  getBounds(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0;
    const r = this.scroll.length();
    e = Math.min(e, r - 1), s = Math.min(e + s, r - 1) - e;
    let i, [a, n] = this.scroll.leaf(e);
    if (a == null) return null;
    if (s > 0 && n === a.length()) {
      const [g] = this.scroll.leaf(e + 1);
      if (g) {
        const [k] = this.scroll.line(e), [y] = this.scroll.line(e + 1);
        k === y && (a = g, n = 0);
      }
    }
    [i, n] = a.position(n, !0);
    const o = document.createRange();
    if (s > 0)
      return o.setStart(i, n), [a, n] = this.scroll.leaf(e + s), a == null ? null : ([i, n] = a.position(n, !0), o.setEnd(i, n), o.getBoundingClientRect());
    let u = "left", p;
    if (i instanceof Text) {
      if (!i.data.length)
        return null;
      n < i.data.length ? (o.setStart(i, n), o.setEnd(i, n + 1)) : (o.setStart(i, n - 1), o.setEnd(i, n), u = "right"), p = o.getBoundingClientRect();
    } else {
      if (!(a.domNode instanceof Element)) return null;
      p = a.domNode.getBoundingClientRect(), n > 0 && (u = "right");
    }
    return {
      bottom: p.top + p.height,
      height: p.height,
      left: p[u],
      right: p[u],
      top: p.top,
      width: 0
    };
  }
  getNativeRange() {
    const e = document.getSelection();
    if (e == null || e.rangeCount <= 0) return null;
    const s = e.getRangeAt(0);
    if (s == null) return null;
    const r = this.normalizeNative(s);
    return ti.info("getNativeRange", r), r;
  }
  getRange() {
    const e = this.scroll.domNode;
    if ("isConnected" in e && !e.isConnected)
      return [null, null];
    const s = this.getNativeRange();
    return s == null ? [null, null] : [this.normalizedToRange(s), s];
  }
  hasFocus() {
    return document.activeElement === this.root || document.activeElement != null && si(this.root, document.activeElement);
  }
  normalizedToRange(e) {
    const s = [[e.start.node, e.start.offset]];
    e.native.collapsed || s.push([e.end.node, e.end.offset]);
    const r = s.map((n) => {
      const [o, u] = n, p = this.scroll.find(o, !0), g = p.offset(this.scroll);
      return u === 0 ? g : p instanceof ge ? g + p.index(o, u) : g + p.length();
    }), i = Math.min(Math.max(...r), this.scroll.length() - 1), a = Math.min(i, ...r);
    return new Pt(a, i - a);
  }
  normalizeNative(e) {
    if (!si(this.root, e.startContainer) || !e.collapsed && !si(this.root, e.endContainer))
      return null;
    const s = {
      start: {
        node: e.startContainer,
        offset: e.startOffset
      },
      end: {
        node: e.endContainer,
        offset: e.endOffset
      },
      native: e
    };
    return [s.start, s.end].forEach((r) => {
      let {
        node: i,
        offset: a
      } = r;
      for (; !(i instanceof Text) && i.childNodes.length > 0; )
        if (i.childNodes.length > a)
          i = i.childNodes[a], a = 0;
        else if (i.childNodes.length === a)
          i = i.lastChild, i instanceof Text ? a = i.data.length : i.childNodes.length > 0 ? a = i.childNodes.length : a = i.childNodes.length + 1;
        else
          break;
      r.node = i, r.offset = a;
    }), s;
  }
  rangeToNative(e) {
    const s = this.scroll.length(), r = (i, a) => {
      i = Math.min(s - 1, i);
      const [n, o] = this.scroll.leaf(i);
      return n ? n.position(o, a) : [null, -1];
    };
    return [...r(e.index, !1), ...r(e.index + e.length, !0)];
  }
  setNativeRange(e, s) {
    let r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : e, i = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : s, a = arguments.length > 4 && arguments[4] !== void 0 ? arguments[4] : !1;
    if (ti.info("setNativeRange", e, s, r, i), e != null && (this.root.parentNode == null || e.parentNode == null || // @ts-expect-error Fix me later
    r.parentNode == null))
      return;
    const n = document.getSelection();
    if (n != null)
      if (e != null) {
        this.hasFocus() || this.root.focus({
          preventScroll: !0
        });
        const {
          native: o
        } = this.getNativeRange() || {};
        if (o == null || a || e !== o.startContainer || s !== o.startOffset || r !== o.endContainer || i !== o.endOffset) {
          e instanceof Element && e.tagName === "BR" && (s = Array.from(e.parentNode.childNodes).indexOf(e), e = e.parentNode), r instanceof Element && r.tagName === "BR" && (i = Array.from(r.parentNode.childNodes).indexOf(r), r = r.parentNode);
          const u = document.createRange();
          u.setStart(e, s), u.setEnd(r, i), n.removeAllRanges(), n.addRange(u);
        }
      } else
        n.removeAllRanges(), this.root.blur();
  }
  setRange(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : F.sources.API;
    if (typeof s == "string" && (r = s, s = !1), ti.info("setRange", e), e != null) {
      const i = this.rangeToNative(e);
      this.setNativeRange(...i, s);
    } else
      this.setNativeRange(null);
    this.update(r);
  }
  update() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : F.sources.USER;
    const s = this.lastRange, [r, i] = this.getRange();
    if (this.lastRange = r, this.lastNative = i, this.lastRange != null && (this.savedRange = this.lastRange), !Hi(s, this.lastRange)) {
      if (!this.composing && i != null && i.native.collapsed && i.start.node !== this.cursor.textNode) {
        const n = this.cursor.restore();
        n && this.setNativeRange(n.startNode, n.startOffset, n.endNode, n.endOffset);
      }
      const a = [F.events.SELECTION_CHANGE, rs(this.lastRange), rs(s), e];
      this.emitter.emit(F.events.EDITOR_CHANGE, ...a), e !== F.sources.SILENT && this.emitter.emit(...a);
    }
  }
}
function si(t, e) {
  try {
    e.parentNode;
  } catch {
    return !1;
  }
  return t.contains(e);
}
const Fk = /^[ -~]*$/;
class Uk {
  constructor(e) {
    this.scroll = e, this.delta = this.getDelta();
  }
  applyDelta(e) {
    this.scroll.update();
    let s = this.scroll.length();
    this.scroll.batchStart();
    const r = ja(e), i = new j();
    return Vk(r.ops.slice()).reduce((n, o) => {
      const u = Ie.Op.length(o);
      let p = o.attributes || {}, g = !1, k = !1;
      if (o.insert != null) {
        if (i.retain(u), typeof o.insert == "string") {
          const v = o.insert;
          k = !v.endsWith(`
`) && (s <= n || !!this.scroll.descendant(Ne, n)[0]), this.scroll.insertAt(n, v);
          const [E, S] = this.scroll.line(n);
          let _ = yt({}, Te(E));
          if (E instanceof ce) {
            const [O] = E.descendant(ge, S);
            O && (_ = yt(_, Te(O)));
          }
          p = Ie.AttributeMap.diff(_, p) || {};
        } else if (typeof o.insert == "object") {
          const v = Object.keys(o.insert)[0];
          if (v == null) return n;
          const E = this.scroll.query(v, V.INLINE) != null;
          if (E)
            (s <= n || this.scroll.descendant(Ne, n)[0]) && (k = !0);
          else if (n > 0) {
            const [S, _] = this.scroll.descendant(ge, n - 1);
            S instanceof je ? S.value()[_] !== `
` && (g = !0) : S instanceof Ae && S.statics.scope === V.INLINE_BLOT && (g = !0);
          }
          if (this.scroll.insertAt(n, v, o.insert[v]), E) {
            const [S] = this.scroll.descendant(ge, n);
            if (S) {
              const _ = yt({}, Te(S));
              p = Ie.AttributeMap.diff(_, p) || {};
            }
          }
        }
        s += u;
      } else if (i.push(o), o.retain !== null && typeof o.retain == "object") {
        const v = Object.keys(o.retain)[0];
        if (v == null) return n;
        this.scroll.updateEmbedAt(n, v, o.retain[v]);
      }
      Object.keys(p).forEach((v) => {
        this.scroll.formatAt(n, u, v, p[v]);
      });
      const y = g ? 1 : 0, b = k ? 1 : 0;
      return s += y + b, i.retain(y), i.delete(b), n + u + y + b;
    }, 0), i.reduce((n, o) => typeof o.delete == "number" ? (this.scroll.deleteAt(n, o.delete), n) : n + Ie.Op.length(o), 0), this.scroll.batchEnd(), this.scroll.optimize(), this.update(r);
  }
  deleteText(e, s) {
    return this.scroll.deleteAt(e, s), this.update(new j().retain(e).delete(s));
  }
  formatLine(e, s) {
    let r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : {};
    this.scroll.update(), Object.keys(r).forEach((a) => {
      this.scroll.lines(e, Math.max(s, 1)).forEach((n) => {
        n.format(a, r[a]);
      });
    }), this.scroll.optimize();
    const i = new j().retain(e).retain(s, rs(r));
    return this.update(i);
  }
  formatText(e, s) {
    let r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : {};
    Object.keys(r).forEach((a) => {
      this.scroll.formatAt(e, s, a, r[a]);
    });
    const i = new j().retain(e).retain(s, rs(r));
    return this.update(i);
  }
  getContents(e, s) {
    return this.delta.slice(e, e + s);
  }
  getDelta() {
    return this.scroll.lines().reduce((e, s) => e.concat(s.delta()), new j());
  }
  getFormat(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0, r = [], i = [];
    s === 0 ? this.scroll.path(e).forEach((o) => {
      const [u] = o;
      u instanceof ce ? r.push(u) : u instanceof ge && i.push(u);
    }) : (r = this.scroll.lines(e, s), i = this.scroll.descendants(ge, e, s));
    const [a, n] = [r, i].map((o) => {
      const u = o.shift();
      if (u == null) return {};
      let p = Te(u);
      for (; Object.keys(p).length > 0; ) {
        const g = o.shift();
        if (g == null) return p;
        p = jk(Te(g), p);
      }
      return p;
    });
    return {
      ...a,
      ...n
    };
  }
  getHTML(e, s) {
    const [r, i] = this.scroll.line(e);
    if (r) {
      const a = r.length();
      return r.length() >= i + s && !(i === 0 && s === a) ? Ws(r, i, s, !0) : Ws(this.scroll, e, s, !0);
    }
    return "";
  }
  getText(e, s) {
    return this.getContents(e, s).filter((r) => typeof r.insert == "string").map((r) => r.insert).join("");
  }
  insertContents(e, s) {
    const r = ja(s), i = new j().retain(e).concat(r);
    return this.scroll.insertContents(e, r), this.update(i);
  }
  insertEmbed(e, s, r) {
    return this.scroll.insertAt(e, s, r), this.update(new j().retain(e).insert({
      [s]: r
    }));
  }
  insertText(e, s) {
    let r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : {};
    return s = s.replace(/\r\n/g, `
`).replace(/\r/g, `
`), this.scroll.insertAt(e, s), Object.keys(r).forEach((i) => {
      this.scroll.formatAt(e, s.length, i, r[i]);
    }), this.update(new j().retain(e).insert(s, rs(r)));
  }
  isBlank() {
    if (this.scroll.children.length === 0) return !0;
    if (this.scroll.children.length > 1) return !1;
    const e = this.scroll.children.head;
    if ((e == null ? void 0 : e.statics.blotName) !== ce.blotName) return !1;
    const s = e;
    return s.children.length > 1 ? !1 : s.children.head instanceof He;
  }
  removeFormat(e, s) {
    const r = this.getText(e, s), [i, a] = this.scroll.line(e + s);
    let n = 0, o = new j();
    i != null && (n = i.length() - a, o = i.delta().slice(a, a + n - 1).insert(`
`));
    const p = this.getContents(e, s + n).diff(new j().insert(r).concat(o)), g = new j().retain(e).concat(p);
    return this.applyDelta(g);
  }
  update(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : void 0;
    const i = this.delta;
    if (s.length === 1 && s[0].type === "characterData" && // @ts-expect-error Fix me later
    s[0].target.data.match(Fk) && this.scroll.find(s[0].target)) {
      const a = this.scroll.find(s[0].target), n = Te(a), o = a.offset(this.scroll), u = s[0].oldValue.replace(us.CONTENTS, ""), p = new j().insert(u), g = new j().insert(a.value()), k = r && {
        oldRange: Va(r.oldRange, -o),
        newRange: Va(r.newRange, -o)
      };
      e = new j().retain(o).concat(p.diff(g, k)).reduce((b, v) => v.insert ? b.insert(v.insert, n) : b.push(v), new j()), this.delta = i.compose(e);
    } else
      this.delta = this.getDelta(), (!e || !Hi(i.compose(e), this.delta)) && (e = i.diff(this.delta, r));
    return e;
  }
}
function ss(t, e, s) {
  if (t.length === 0) {
    const [b] = ni(s.pop());
    return e <= 0 ? `</li></${b}>` : `</li></${b}>${ss([], e - 1, s)}`;
  }
  const [{
    child: r,
    offset: i,
    length: a,
    indent: n,
    type: o
  }, ...u] = t, [p, g] = ni(o);
  if (n > e)
    return s.push(o), n === e + 1 ? `<${p}><li${g}>${Ws(r, i, a)}${ss(u, n, s)}` : `<${p}><li>${ss(t, e + 1, s)}`;
  const k = s[s.length - 1];
  if (n === e && o === k)
    return `</li><li${g}>${Ws(r, i, a)}${ss(u, n, s)}`;
  const [y] = ni(s.pop());
  return `</li></${y}>${ss(t, e - 1, s)}`;
}
function Ws(t, e, s) {
  let r = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : !1;
  if ("html" in t && typeof t.html == "function")
    return t.html(e, s);
  if (t instanceof je)
    return Jn(t.value().slice(e, e + s)).replaceAll(" ", "&nbsp;");
  if (t instanceof Ue) {
    if (t.statics.blotName === "list-container") {
      const p = [];
      return t.children.forEachAt(e, s, (g, k, y) => {
        const b = "formats" in g && typeof g.formats == "function" ? g.formats() : {};
        p.push({
          child: g,
          offset: k,
          length: y,
          indent: b.indent || 0,
          type: b.list
        });
      }), ss(p, -1, []);
    }
    const i = [];
    if (t.children.forEachAt(e, s, (p, g, k) => {
      i.push(Ws(p, g, k));
    }), r || t.statics.blotName === "list")
      return i.join("");
    const {
      outerHTML: a,
      innerHTML: n
    } = t.domNode, [o, u] = a.split(`>${n}<`);
    return o === "<table" ? `<table style="border: 1px solid #000;">${i.join("")}<${u}` : `${o}>${i.join("")}<${u}`;
  }
  return t.domNode instanceof Element ? t.domNode.outerHTML : "";
}
function jk(t, e) {
  return Object.keys(e).reduce((s, r) => {
    if (t[r] == null) return s;
    const i = e[r];
    return i === t[r] ? s[r] = i : Array.isArray(i) ? i.indexOf(t[r]) < 0 ? s[r] = i.concat([t[r]]) : s[r] = i : s[r] = [i, t[r]], s;
  }, {});
}
function ni(t) {
  const e = t === "ordered" ? "ol" : "ul";
  switch (t) {
    case "checked":
      return [e, ' data-list="checked"'];
    case "unchecked":
      return [e, ' data-list="unchecked"'];
    default:
      return [e, ""];
  }
}
function ja(t) {
  return t.reduce((e, s) => {
    if (typeof s.insert == "string") {
      const r = s.insert.replace(/\r\n/g, `
`).replace(/\r/g, `
`);
      return e.insert(r, s.attributes);
    }
    return e.push(s);
  }, new j());
}
function Va(t, e) {
  let {
    index: s,
    length: r
  } = t;
  return new Pt(s + e, r);
}
function Vk(t) {
  const e = [];
  return t.forEach((s) => {
    typeof s.insert == "string" ? s.insert.split(`
`).forEach((i, a) => {
      a && e.push({
        insert: `
`,
        attributes: s.attributes
      }), i && e.push({
        insert: i,
        attributes: s.attributes
      });
    }) : e.push(s);
  }), e;
}
class ze {
  constructor(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
    this.quill = e, this.options = s;
  }
}
B(ze, "DEFAULTS", {});
const Ln = "\uFEFF";
class Yi extends Ae {
  constructor(e, s) {
    super(e, s), this.contentNode = document.createElement("span"), this.contentNode.setAttribute("contenteditable", "false"), Array.from(this.domNode.childNodes).forEach((r) => {
      this.contentNode.appendChild(r);
    }), this.leftGuard = document.createTextNode(Ln), this.rightGuard = document.createTextNode(Ln), this.domNode.appendChild(this.leftGuard), this.domNode.appendChild(this.contentNode), this.domNode.appendChild(this.rightGuard);
  }
  index(e, s) {
    return e === this.leftGuard ? 0 : e === this.rightGuard ? 1 : super.index(e, s);
  }
  restore(e) {
    let s = null, r;
    const i = e.data.split(Ln).join("");
    if (e === this.leftGuard)
      if (this.prev instanceof je) {
        const a = this.prev.length();
        this.prev.insertAt(a, i), s = {
          startNode: this.prev.domNode,
          startOffset: a + i.length
        };
      } else
        r = document.createTextNode(i), this.parent.insertBefore(this.scroll.create(r), this), s = {
          startNode: r,
          startOffset: i.length
        };
    else e === this.rightGuard && (this.next instanceof je ? (this.next.insertAt(0, i), s = {
      startNode: this.next.domNode,
      startOffset: i.length
    }) : (r = document.createTextNode(i), this.parent.insertBefore(this.scroll.create(r), this.next), s = {
      startNode: r,
      startOffset: i.length
    }));
    return e.data = Ln, s;
  }
  update(e, s) {
    e.forEach((r) => {
      if (r.type === "characterData" && (r.target === this.leftGuard || r.target === this.rightGuard)) {
        const i = this.restore(r.target);
        i && (s.range = i);
      }
    });
  }
}
class Hk {
  constructor(e, s) {
    B(this, "isComposing", !1);
    this.scroll = e, this.emitter = s, this.setupListeners();
  }
  setupListeners() {
    this.scroll.domNode.addEventListener("compositionstart", (e) => {
      this.isComposing || this.handleCompositionStart(e);
    }), this.scroll.domNode.addEventListener("compositionend", (e) => {
      this.isComposing && queueMicrotask(() => {
        this.handleCompositionEnd(e);
      });
    });
  }
  handleCompositionStart(e) {
    const s = e.target instanceof Node ? this.scroll.find(e.target, !0) : null;
    s && !(s instanceof Yi) && (this.emitter.emit(F.events.COMPOSITION_BEFORE_START, e), this.scroll.batchStart(), this.emitter.emit(F.events.COMPOSITION_START, e), this.isComposing = !0);
  }
  handleCompositionEnd(e) {
    this.emitter.emit(F.events.COMPOSITION_BEFORE_END, e), this.scroll.batchEnd(), this.emitter.emit(F.events.COMPOSITION_END, e), this.isComposing = !1;
  }
}
const Us = class Us {
  constructor(e, s) {
    B(this, "modules", {});
    this.quill = e, this.options = s;
  }
  init() {
    Object.keys(this.options.modules).forEach((e) => {
      this.modules[e] == null && this.addModule(e);
    });
  }
  addModule(e) {
    const s = this.quill.constructor.import(`modules/${e}`);
    return this.modules[e] = new s(this.quill, this.options.modules[e] || {}), this.modules[e];
  }
};
B(Us, "DEFAULTS", {
  modules: {}
}), B(Us, "themes", {
  default: Us
});
let ds = Us;
const zk = (t) => t.parentElement || t.getRootNode().host || null, Gk = (t) => {
  const e = t.getBoundingClientRect(), s = "offsetWidth" in t && Math.abs(e.width) / t.offsetWidth || 1, r = "offsetHeight" in t && Math.abs(e.height) / t.offsetHeight || 1;
  return {
    top: e.top,
    right: e.left + t.clientWidth * s,
    bottom: e.top + t.clientHeight * r,
    left: e.left
  };
}, qn = (t) => {
  const e = parseInt(t, 10);
  return Number.isNaN(e) ? 0 : e;
}, Ha = (t, e, s, r, i, a) => t < s && e > r ? 0 : t < s ? -(s - t + i) : e > r ? e - t > r - s ? t + i - s : e - r + a : 0, Kk = (t, e) => {
  var a, n, o;
  const s = t.ownerDocument;
  let r = e, i = t;
  for (; i; ) {
    const u = i === s.body, p = u ? {
      top: 0,
      right: ((a = window.visualViewport) == null ? void 0 : a.width) ?? s.documentElement.clientWidth,
      bottom: ((n = window.visualViewport) == null ? void 0 : n.height) ?? s.documentElement.clientHeight,
      left: 0
    } : Gk(i), g = getComputedStyle(i), k = Ha(r.left, r.right, p.left, p.right, qn(g.scrollPaddingLeft), qn(g.scrollPaddingRight)), y = Ha(r.top, r.bottom, p.top, p.bottom, qn(g.scrollPaddingTop), qn(g.scrollPaddingBottom));
    if (k || y)
      if (u)
        (o = s.defaultView) == null || o.scrollBy(k, y);
      else {
        const {
          scrollLeft: b,
          scrollTop: v
        } = i;
        y && (i.scrollTop += y), k && (i.scrollLeft += k);
        const E = i.scrollLeft - b, S = i.scrollTop - v;
        r = {
          left: r.left - E,
          top: r.top - S,
          right: r.right - E,
          bottom: r.bottom - S
        };
      }
    i = u || g.position === "fixed" ? null : zk(i);
  }
}, Wk = 100, Zk = ["block", "break", "cursor", "inline", "scroll", "text"], Xk = (t, e, s) => {
  const r = new ls();
  return Zk.forEach((i) => {
    const a = e.query(i);
    a && r.register(a);
  }), t.forEach((i) => {
    let a = e.query(i);
    a || s.error(`Cannot register "${i}" specified in "formats" config. Are you sure it was registered?`);
    let n = 0;
    for (; a; )
      if (r.register(a), a = "blotName" in a ? a.requiredContainer ?? null : null, n += 1, n > Wk) {
        s.error(`Cycle detected in registering blot requiredContainer: "${i}"`);
        break;
      }
  }), r;
}, as = ct("quill"), On = new ls();
Ue.uiClass = "ql-ui";
const Re = class Re {
  static debug(e) {
    e === !0 && (e = "log"), ct.level(e);
  }
  static find(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1;
    return Ai.get(e) || On.find(e, s);
  }
  static import(e) {
    return this.imports[e] == null && as.error(`Cannot import ${e}. Are you sure it was registered?`), this.imports[e];
  }
  static register() {
    if (typeof (arguments.length <= 0 ? void 0 : arguments[0]) != "string") {
      const e = arguments.length <= 0 ? void 0 : arguments[0], s = !!(!(arguments.length <= 1) && arguments[1]), r = "attrName" in e ? e.attrName : e.blotName;
      typeof r == "string" ? this.register(`formats/${r}`, e, s) : Object.keys(e).forEach((i) => {
        this.register(i, e[i], s);
      });
    } else {
      const e = arguments.length <= 0 ? void 0 : arguments[0], s = arguments.length <= 1 ? void 0 : arguments[1], r = !!(!(arguments.length <= 2) && arguments[2]);
      this.imports[e] != null && !r && as.warn(`Overwriting ${e} with`, s), this.imports[e] = s, (e.startsWith("blots/") || e.startsWith("formats/")) && s && typeof s != "boolean" && s.blotName !== "abstract" && On.register(s), typeof s.register == "function" && s.register(On);
    }
  }
  constructor(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
    if (this.options = Yk(e, s), this.container = this.options.container, this.container == null) {
      as.error("Invalid Quill container", e);
      return;
    }
    this.options.debug && Re.debug(this.options.debug);
    const r = this.container.innerHTML.trim();
    this.container.classList.add("ql-container"), this.container.innerHTML = "", Ai.set(this.container, this), this.root = this.addContainer("ql-editor"), this.root.classList.add("ql-blank"), this.emitter = new F();
    const i = Gi.blotName, a = this.options.registry.query(i);
    if (!a || !("blotName" in a))
      throw new Error(`Cannot initialize Quill without "${i}" blot`);
    if (this.scroll = new a(this.options.registry, this.root, {
      emitter: this.emitter
    }), this.editor = new Uk(this.scroll), this.selection = new Mk(this.scroll, this.emitter), this.composition = new Hk(this.scroll, this.emitter), this.theme = new this.options.theme(this, this.options), this.keyboard = this.theme.addModule("keyboard"), this.clipboard = this.theme.addModule("clipboard"), this.history = this.theme.addModule("history"), this.uploader = this.theme.addModule("uploader"), this.theme.addModule("input"), this.theme.addModule("uiNode"), this.theme.init(), this.emitter.on(F.events.EDITOR_CHANGE, (n) => {
      n === F.events.TEXT_CHANGE && this.root.classList.toggle("ql-blank", this.editor.isBlank());
    }), this.emitter.on(F.events.SCROLL_UPDATE, (n, o) => {
      const u = this.selection.lastRange, [p] = this.selection.getRange(), g = u && p ? {
        oldRange: u,
        newRange: p
      } : void 0;
      De.call(this, () => this.editor.update(null, o, g), n);
    }), this.emitter.on(F.events.SCROLL_EMBED_UPDATE, (n, o) => {
      const u = this.selection.lastRange, [p] = this.selection.getRange(), g = u && p ? {
        oldRange: u,
        newRange: p
      } : void 0;
      De.call(this, () => {
        const k = new j().retain(n.offset(this)).retain({
          [n.statics.blotName]: o
        });
        return this.editor.update(k, [], g);
      }, Re.sources.USER);
    }), r) {
      const n = this.clipboard.convert({
        html: `${r}<p><br></p>`,
        text: `
`
      });
      this.setContents(n);
    }
    this.history.clear(), this.options.placeholder && this.root.setAttribute("data-placeholder", this.options.placeholder), this.options.readOnly && this.disable(), this.allowReadOnlyEdits = !1;
  }
  addContainer(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : null;
    if (typeof e == "string") {
      const r = e;
      e = document.createElement("div"), e.classList.add(r);
    }
    return this.container.insertBefore(e, s), e;
  }
  blur() {
    this.selection.setRange(null);
  }
  deleteText(e, s, r) {
    return [e, s, , r] = at(e, s, r), De.call(this, () => this.editor.deleteText(e, s), r, e, -1 * s);
  }
  disable() {
    this.enable(!1);
  }
  editReadOnly(e) {
    this.allowReadOnlyEdits = !0;
    const s = e();
    return this.allowReadOnlyEdits = !1, s;
  }
  enable() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : !0;
    this.scroll.enable(e), this.container.classList.toggle("ql-disabled", !e);
  }
  focus() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    this.selection.focus(), e.preventScroll || this.scrollSelectionIntoView();
  }
  format(e, s) {
    let r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : F.sources.API;
    return De.call(this, () => {
      const i = this.getSelection(!0);
      let a = new j();
      if (i == null) return a;
      if (this.scroll.query(e, V.BLOCK))
        a = this.editor.formatLine(i.index, i.length, {
          [e]: s
        });
      else {
        if (i.length === 0)
          return this.selection.format(e, s), a;
        a = this.editor.formatText(i.index, i.length, {
          [e]: s
        });
      }
      return this.setSelection(i, F.sources.SILENT), a;
    }, r);
  }
  formatLine(e, s, r, i, a) {
    let n;
    return [e, s, n, a] = at(
      e,
      s,
      // @ts-expect-error
      r,
      i,
      a
    ), De.call(this, () => this.editor.formatLine(e, s, n), a, e, 0);
  }
  formatText(e, s, r, i, a) {
    let n;
    return [e, s, n, a] = at(
      // @ts-expect-error
      e,
      s,
      r,
      i,
      a
    ), De.call(this, () => this.editor.formatText(e, s, n), a, e, 0);
  }
  getBounds(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0, r = null;
    if (typeof e == "number" ? r = this.selection.getBounds(e, s) : r = this.selection.getBounds(e.index, e.length), !r) return null;
    const i = this.container.getBoundingClientRect();
    return {
      bottom: r.bottom - i.top,
      height: r.height,
      left: r.left - i.left,
      right: r.right - i.left,
      top: r.top - i.top,
      width: r.width
    };
  }
  getContents() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 0, s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : this.getLength() - e;
    return [e, s] = at(e, s), this.editor.getContents(e, s);
  }
  getFormat() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : this.getSelection(!0), s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0;
    return typeof e == "number" ? this.editor.getFormat(e, s) : this.editor.getFormat(e.index, e.length);
  }
  getIndex(e) {
    return e.offset(this.scroll);
  }
  getLength() {
    return this.scroll.length();
  }
  getLeaf(e) {
    return this.scroll.leaf(e);
  }
  getLine(e) {
    return this.scroll.line(e);
  }
  getLines() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 0, s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Number.MAX_VALUE;
    return typeof e != "number" ? this.scroll.lines(e.index, e.length) : this.scroll.lines(e, s);
  }
  getModule(e) {
    return this.theme.modules[e];
  }
  getSelection() {
    return (arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : !1) && this.focus(), this.update(), this.selection.getRange()[0];
  }
  getSemanticHTML() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 0, s = arguments.length > 1 ? arguments[1] : void 0;
    return typeof e == "number" && (s = s ?? this.getLength() - e), [e, s] = at(e, s), this.editor.getHTML(e, s);
  }
  getText() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 0, s = arguments.length > 1 ? arguments[1] : void 0;
    return typeof e == "number" && (s = s ?? this.getLength() - e), [e, s] = at(e, s), this.editor.getText(e, s);
  }
  hasFocus() {
    return this.selection.hasFocus();
  }
  insertEmbed(e, s, r) {
    let i = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : Re.sources.API;
    return De.call(this, () => this.editor.insertEmbed(e, s, r), i, e);
  }
  insertText(e, s, r, i, a) {
    let n;
    return [e, , n, a] = at(e, 0, r, i, a), De.call(this, () => this.editor.insertText(e, s, n), a, e, s.length);
  }
  isEnabled() {
    return this.scroll.isEnabled();
  }
  off() {
    return this.emitter.off(...arguments);
  }
  on() {
    return this.emitter.on(...arguments);
  }
  once() {
    return this.emitter.once(...arguments);
  }
  removeFormat(e, s, r) {
    return [e, s, , r] = at(e, s, r), De.call(this, () => this.editor.removeFormat(e, s), r, e);
  }
  scrollRectIntoView(e) {
    Kk(this.root, e);
  }
  /**
   * @deprecated Use Quill#scrollSelectionIntoView() instead.
   */
  scrollIntoView() {
    console.warn("Quill#scrollIntoView() has been deprecated and will be removed in the near future. Please use Quill#scrollSelectionIntoView() instead."), this.scrollSelectionIntoView();
  }
  /**
   * Scroll the current selection into the visible area.
   * If the selection is already visible, no scrolling will occur.
   */
  scrollSelectionIntoView() {
    const e = this.selection.lastRange, s = e && this.selection.getBounds(e.index, e.length);
    s && this.scrollRectIntoView(s);
  }
  setContents(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : F.sources.API;
    return De.call(this, () => {
      e = new j(e);
      const r = this.getLength(), i = this.editor.deleteText(0, r), a = this.editor.insertContents(0, e), n = this.editor.deleteText(this.getLength() - 1, 1);
      return i.compose(a).compose(n);
    }, s);
  }
  setSelection(e, s, r) {
    e == null ? this.selection.setRange(null, s || Re.sources.API) : ([e, s, , r] = at(e, s, r), this.selection.setRange(new Pt(Math.max(0, e), s), r), r !== F.sources.SILENT && this.scrollSelectionIntoView());
  }
  setText(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : F.sources.API;
    const r = new j().insert(e);
    return this.setContents(r, s);
  }
  update() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : F.sources.USER;
    const s = this.scroll.update(e);
    return this.selection.update(e), s;
  }
  updateContents(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : F.sources.API;
    return De.call(this, () => (e = new j(e), this.editor.applyDelta(e)), s, !0);
  }
};
B(Re, "DEFAULTS", {
  bounds: null,
  modules: {
    clipboard: !0,
    keyboard: !0,
    history: !0,
    uploader: !0
  },
  placeholder: "",
  readOnly: !1,
  registry: On,
  theme: "default"
}), B(Re, "events", F.events), B(Re, "sources", F.sources), B(Re, "version", "2.0.3"), B(Re, "imports", {
  delta: j,
  parchment: $k,
  "core/module": ze,
  "core/theme": ds
});
let N = Re;
function za(t) {
  return typeof t == "string" ? document.querySelector(t) : t;
}
function ri(t) {
  return Object.entries(t ?? {}).reduce((e, s) => {
    let [r, i] = s;
    return {
      ...e,
      [r]: i === !0 ? {} : i
    };
  }, {});
}
function Ga(t) {
  return Object.fromEntries(Object.entries(t).filter((e) => e[1] !== void 0));
}
function Yk(t, e) {
  const s = za(t);
  if (!s)
    throw new Error("Invalid Quill container");
  const i = !e.theme || e.theme === N.DEFAULTS.theme ? ds : N.import(`themes/${e.theme}`);
  if (!i)
    throw new Error(`Invalid theme ${e.theme}. Did you register it?`);
  const {
    modules: a,
    ...n
  } = N.DEFAULTS, {
    modules: o,
    ...u
  } = i.DEFAULTS;
  let p = ri(e.modules);
  p != null && p.toolbar && p.toolbar.constructor !== Object && (p = {
    ...p,
    toolbar: {
      container: p.toolbar
    }
  });
  const g = yt({}, ri(a), ri(o), p), k = {
    ...n,
    ...Ga(u),
    ...Ga(e)
  };
  let y = e.registry;
  return y ? e.formats && as.warn('Ignoring "formats" option because "registry" is specified') : y = e.formats ? Xk(e.formats, k.registry, as) : k.registry, {
    ...k,
    registry: y,
    container: s,
    theme: i,
    modules: Object.entries(g).reduce((b, v) => {
      let [E, S] = v;
      if (!S) return b;
      const _ = N.import(`modules/${E}`);
      return _ == null ? (as.error(`Cannot load ${E} module. Are you sure you registered it?`), b) : {
        ...b,
        // @ts-expect-error
        [E]: yt({}, _.DEFAULTS || {}, S)
      };
    }, {}),
    bounds: za(k.bounds)
  };
}
function De(t, e, s, r) {
  if (!this.isEnabled() && e === F.sources.USER && !this.allowReadOnlyEdits)
    return new j();
  let i = s == null ? null : this.getSelection();
  const a = this.editor.delta, n = t();
  if (i != null && (s === !0 && (s = i.index), r == null ? i = Ka(i, n, e) : r !== 0 && (i = Ka(i, s, r, e)), this.setSelection(i, F.sources.SILENT)), n.length() > 0) {
    const o = [F.events.TEXT_CHANGE, n, a, e];
    this.emitter.emit(F.events.EDITOR_CHANGE, ...o), e !== F.sources.SILENT && this.emitter.emit(...o);
  }
  return n;
}
function at(t, e, s, r, i) {
  let a = {};
  return typeof t.index == "number" && typeof t.length == "number" ? typeof e != "number" ? (i = r, r = s, s = e, e = t.length, t = t.index) : (e = t.length, t = t.index) : typeof e != "number" && (i = r, r = s, s = e, e = 0), typeof s == "object" ? (a = s, i = r) : typeof s == "string" && (r != null ? a[s] = r : i = s), i = i || F.sources.API, [t, e, a, i];
}
function Ka(t, e, s, r) {
  const i = typeof s == "number" ? s : 0;
  if (t == null) return null;
  let a, n;
  return e && typeof e.transformPosition == "function" ? [a, n] = [t.index, t.index + t.length].map((o) => (
    // @ts-expect-error -- TODO: add a better type guard around `index`
    e.transformPosition(o, r !== F.sources.USER)
  )) : [a, n] = [t.index, t.index + t.length].map((o) => o < e || o === e && r === F.sources.USER ? o : i >= 0 ? o + i : Math.max(e, o + i)), new Pt(a, n - a);
}
class Mt extends Zn {
}
function Wa(t) {
  return t instanceof ce || t instanceof Ne;
}
function Za(t) {
  return typeof t.updateContent == "function";
}
class ns extends Gi {
  constructor(e, s, r) {
    let {
      emitter: i
    } = r;
    super(e, s), this.emitter = i, this.batch = !1, this.optimize(), this.enable(), this.domNode.addEventListener("dragstart", (a) => this.handleDragStart(a));
  }
  batchStart() {
    Array.isArray(this.batch) || (this.batch = []);
  }
  batchEnd() {
    if (!this.batch) return;
    const e = this.batch;
    this.batch = !1, this.update(e);
  }
  emitMount(e) {
    this.emitter.emit(F.events.SCROLL_BLOT_MOUNT, e);
  }
  emitUnmount(e) {
    this.emitter.emit(F.events.SCROLL_BLOT_UNMOUNT, e);
  }
  emitEmbedUpdate(e, s) {
    this.emitter.emit(F.events.SCROLL_EMBED_UPDATE, e, s);
  }
  deleteAt(e, s) {
    const [r, i] = this.line(e), [a] = this.line(e + s);
    if (super.deleteAt(e, s), a != null && r !== a && i > 0) {
      if (r instanceof Ne || a instanceof Ne) {
        this.optimize();
        return;
      }
      const n = a.children.head instanceof He ? null : a.children.head;
      r.moveChildren(a, n), r.remove();
    }
    this.optimize();
  }
  enable() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : !0;
    this.domNode.setAttribute("contenteditable", e ? "true" : "false");
  }
  formatAt(e, s, r, i) {
    super.formatAt(e, s, r, i), this.optimize();
  }
  insertAt(e, s, r) {
    if (e >= this.length())
      if (r == null || this.scroll.query(s, V.BLOCK) == null) {
        const i = this.scroll.create(this.statics.defaultChild.blotName);
        this.appendChild(i), r == null && s.endsWith(`
`) ? i.insertAt(0, s.slice(0, -1), r) : i.insertAt(0, s, r);
      } else {
        const i = this.scroll.create(s, r);
        this.appendChild(i);
      }
    else
      super.insertAt(e, s, r);
    this.optimize();
  }
  insertBefore(e, s) {
    if (e.statics.scope === V.INLINE_BLOT) {
      const r = this.scroll.create(this.statics.defaultChild.blotName);
      r.appendChild(e), super.insertBefore(r, s);
    } else
      super.insertBefore(e, s);
  }
  insertContents(e, s) {
    const r = this.deltaToRenderBlocks(s.concat(new j().insert(`
`))), i = r.pop();
    if (i == null) return;
    this.batchStart();
    const a = r.shift();
    if (a) {
      const u = a.type === "block" && (a.delta.length() === 0 || !this.descendant(Ne, e)[0] && e < this.length()), p = a.type === "block" ? a.delta : new j().insert({
        [a.key]: a.value
      });
      ii(this, e, p);
      const g = a.type === "block" ? 1 : 0, k = e + p.length() + g;
      u && this.insertAt(k - 1, `
`);
      const y = Te(this.line(e)[0]), b = Ie.AttributeMap.diff(y, a.attributes) || {};
      Object.keys(b).forEach((v) => {
        this.formatAt(k - 1, 1, v, b[v]);
      }), e = k;
    }
    let [n, o] = this.children.find(e);
    if (r.length && (n && (n = n.split(o), o = 0), r.forEach((u) => {
      if (u.type === "block") {
        const p = this.createBlock(u.attributes, n || void 0);
        ii(p, 0, u.delta);
      } else {
        const p = this.create(u.key, u.value);
        this.insertBefore(p, n || void 0), Object.keys(u.attributes).forEach((g) => {
          p.format(g, u.attributes[g]);
        });
      }
    })), i.type === "block" && i.delta.length()) {
      const u = n ? n.offset(n.scroll) + o : this.length();
      ii(this, u, i.delta);
    }
    this.batchEnd(), this.optimize();
  }
  isEnabled() {
    return this.domNode.getAttribute("contenteditable") === "true";
  }
  leaf(e) {
    const s = this.path(e).pop();
    if (!s)
      return [null, -1];
    const [r, i] = s;
    return r instanceof ge ? [r, i] : [null, -1];
  }
  line(e) {
    return e === this.length() ? this.line(e - 1) : this.descendant(Wa, e);
  }
  lines() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 0, s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Number.MAX_VALUE;
    const r = (i, a, n) => {
      let o = [], u = n;
      return i.children.forEachAt(a, n, (p, g, k) => {
        Wa(p) ? o.push(p) : p instanceof Zn && (o = o.concat(r(p, g, u))), u -= k;
      }), o;
    };
    return r(this, e, s);
  }
  optimize() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
    this.batch || (super.optimize(e, s), e.length > 0 && this.emitter.emit(F.events.SCROLL_OPTIMIZE, e, s));
  }
  path(e) {
    return super.path(e).slice(1);
  }
  remove() {
  }
  update(e) {
    if (this.batch) {
      Array.isArray(e) && (this.batch = this.batch.concat(e));
      return;
    }
    let s = F.sources.USER;
    typeof e == "string" && (s = e), Array.isArray(e) || (e = this.observer.takeRecords()), e = e.filter((r) => {
      let {
        target: i
      } = r;
      const a = this.find(i, !0);
      return a && !Za(a);
    }), e.length > 0 && this.emitter.emit(F.events.SCROLL_BEFORE_UPDATE, s, e), super.update(e.concat([])), e.length > 0 && this.emitter.emit(F.events.SCROLL_UPDATE, s, e);
  }
  updateEmbedAt(e, s, r) {
    const [i] = this.descendant((a) => a instanceof Ne, e);
    i && i.statics.blotName === s && Za(i) && i.updateContent(r);
  }
  handleDragStart(e) {
    e.preventDefault();
  }
  deltaToRenderBlocks(e) {
    const s = [];
    let r = new j();
    return e.forEach((i) => {
      const a = i == null ? void 0 : i.insert;
      if (a)
        if (typeof a == "string") {
          const n = a.split(`
`);
          n.slice(0, -1).forEach((u) => {
            r.insert(u, i.attributes), s.push({
              type: "block",
              delta: r,
              attributes: i.attributes ?? {}
            }), r = new j();
          });
          const o = n[n.length - 1];
          o && r.insert(o, i.attributes);
        } else {
          const n = Object.keys(a)[0];
          if (!n) return;
          this.query(n, V.INLINE) ? r.push(i) : (r.length() && s.push({
            type: "block",
            delta: r,
            attributes: {}
          }), r = new j(), s.push({
            type: "blockEmbed",
            key: n,
            value: a[n],
            attributes: i.attributes ?? {}
          }));
        }
    }), r.length() && s.push({
      type: "block",
      delta: r,
      attributes: {}
    }), s;
  }
  createBlock(e, s) {
    let r;
    const i = {};
    Object.entries(e).forEach((o) => {
      let [u, p] = o;
      this.query(u, V.BLOCK & V.BLOT) != null ? r = u : i[u] = p;
    });
    const a = this.create(r || this.statics.defaultChild.blotName, r ? e[r] : void 0);
    this.insertBefore(a, s || void 0);
    const n = a.length();
    return Object.entries(i).forEach((o) => {
      let [u, p] = o;
      a.formatAt(0, n, u, p);
    }), a;
  }
}
B(ns, "blotName", "scroll"), B(ns, "className", "ql-editor"), B(ns, "tagName", "DIV"), B(ns, "defaultChild", ce), B(ns, "allowedChildren", [ce, Ne, Mt]);
function ii(t, e, s) {
  s.reduce((r, i) => {
    const a = Ie.Op.length(i);
    let n = i.attributes || {};
    if (i.insert != null) {
      if (typeof i.insert == "string") {
        const o = i.insert;
        t.insertAt(r, o);
        const [u] = t.descendant(ge, r), p = Te(u);
        n = Ie.AttributeMap.diff(p, n) || {};
      } else if (typeof i.insert == "object") {
        const o = Object.keys(i.insert)[0];
        if (o == null) return r;
        if (t.insertAt(r, o, i.insert[o]), t.scroll.query(o, V.INLINE) != null) {
          const [p] = t.descendant(ge, r), g = Te(p);
          n = Ie.AttributeMap.diff(g, n) || {};
        }
      }
    }
    return Object.keys(n).forEach((o) => {
      t.formatAt(r, a, o, n[o]);
    }), r + a;
  }, e);
}
const Qi = {
  scope: V.BLOCK,
  whitelist: ["right", "center", "justify"]
}, Qk = new Je("align", "align", Qi), xo = new Ve("align", "ql-align", Qi), el = new wt("align", "text-align", Qi);
class tl extends wt {
  value(e) {
    let s = super.value(e);
    return s.startsWith("rgb(") ? (s = s.replace(/^[^\d]+/, "").replace(/[^\d]+$/, ""), `#${s.split(",").map((i) => `00${parseInt(i, 10).toString(16)}`.slice(-2)).join("")}`) : s;
  }
}
const Jk = new Ve("color", "ql-color", {
  scope: V.INLINE
}), Ji = new tl("color", "color", {
  scope: V.INLINE
}), xk = new Ve("background", "ql-bg", {
  scope: V.INLINE
}), xi = new tl("background", "background-color", {
  scope: V.INLINE
});
class Ft extends Mt {
  static create(e) {
    const s = super.create(e);
    return s.setAttribute("spellcheck", "false"), s;
  }
  code(e, s) {
    return this.children.map((r) => r.length() <= 1 ? "" : r.domNode.innerText).join(`
`).slice(e, e + s);
  }
  html(e, s) {
    return `<pre>
${Jn(this.code(e, s))}
</pre>`;
  }
}
class me extends ce {
  static register() {
    N.register(Ft);
  }
}
B(me, "TAB", "  ");
class ea extends xe {
}
ea.blotName = "code";
ea.tagName = "CODE";
me.blotName = "code-block";
me.className = "ql-code-block";
me.tagName = "DIV";
Ft.blotName = "code-block-container";
Ft.className = "ql-code-block-container";
Ft.tagName = "DIV";
Ft.allowedChildren = [me];
me.allowedChildren = [je, He, us];
me.requiredContainer = Ft;
const ta = {
  scope: V.BLOCK,
  whitelist: ["rtl"]
}, sl = new Je("direction", "dir", ta), nl = new Ve("direction", "ql-direction", ta), rl = new wt("direction", "direction", ta), il = {
  scope: V.INLINE,
  whitelist: ["serif", "monospace"]
}, al = new Ve("font", "ql-font", il);
class ew extends wt {
  value(e) {
    return super.value(e).replace(/["']/g, "");
  }
}
const ol = new ew("font", "font-family", il), ll = new Ve("size", "ql-size", {
  scope: V.INLINE,
  whitelist: ["small", "large", "huge"]
}), ul = new wt("size", "font-size", {
  scope: V.INLINE,
  whitelist: ["10px", "18px", "32px"]
}), tw = ct("quill:keyboard"), sw = /Mac/i.test(navigator.platform) ? "metaKey" : "ctrlKey";
class xn extends ze {
  static match(e, s) {
    return ["altKey", "ctrlKey", "metaKey", "shiftKey"].some((r) => !!s[r] !== e[r] && s[r] !== null) ? !1 : s.key === e.key || s.key === e.which;
  }
  constructor(e, s) {
    super(e, s), this.bindings = {}, Object.keys(this.options.bindings).forEach((r) => {
      this.options.bindings[r] && this.addBinding(this.options.bindings[r]);
    }), this.addBinding({
      key: "Enter",
      shiftKey: null
    }, this.handleEnter), this.addBinding({
      key: "Enter",
      metaKey: null,
      ctrlKey: null,
      altKey: null
    }, () => {
    }), /Firefox/i.test(navigator.userAgent) ? (this.addBinding({
      key: "Backspace"
    }, {
      collapsed: !0
    }, this.handleBackspace), this.addBinding({
      key: "Delete"
    }, {
      collapsed: !0
    }, this.handleDelete)) : (this.addBinding({
      key: "Backspace"
    }, {
      collapsed: !0,
      prefix: /^.?$/
    }, this.handleBackspace), this.addBinding({
      key: "Delete"
    }, {
      collapsed: !0,
      suffix: /^.?$/
    }, this.handleDelete)), this.addBinding({
      key: "Backspace"
    }, {
      collapsed: !1
    }, this.handleDeleteRange), this.addBinding({
      key: "Delete"
    }, {
      collapsed: !1
    }, this.handleDeleteRange), this.addBinding({
      key: "Backspace",
      altKey: null,
      ctrlKey: null,
      metaKey: null,
      shiftKey: null
    }, {
      collapsed: !0,
      offset: 0
    }, this.handleBackspace), this.listen();
  }
  addBinding(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : {};
    const i = rw(e);
    if (i == null) {
      tw.warn("Attempted to add invalid keyboard binding", i);
      return;
    }
    typeof s == "function" && (s = {
      handler: s
    }), typeof r == "function" && (r = {
      handler: r
    }), (Array.isArray(i.key) ? i.key : [i.key]).forEach((n) => {
      const o = {
        ...i,
        key: n,
        ...s,
        ...r
      };
      this.bindings[o.key] = this.bindings[o.key] || [], this.bindings[o.key].push(o);
    });
  }
  listen() {
    this.quill.root.addEventListener("keydown", (e) => {
      if (e.defaultPrevented || e.isComposing || e.keyCode === 229 && (e.key === "Enter" || e.key === "Backspace")) return;
      const i = (this.bindings[e.key] || []).concat(this.bindings[e.which] || []).filter((_) => xn.match(e, _));
      if (i.length === 0) return;
      const a = N.find(e.target, !0);
      if (a && a.scroll !== this.quill.scroll) return;
      const n = this.quill.getSelection();
      if (n == null || !this.quill.hasFocus()) return;
      const [o, u] = this.quill.getLine(n.index), [p, g] = this.quill.getLeaf(n.index), [k, y] = n.length === 0 ? [p, g] : this.quill.getLeaf(n.index + n.length), b = p instanceof jn ? p.value().slice(0, g) : "", v = k instanceof jn ? k.value().slice(y) : "", E = {
        collapsed: n.length === 0,
        // @ts-expect-error Fix me later
        empty: n.length === 0 && o.length() <= 1,
        format: this.quill.getFormat(n),
        line: o,
        offset: u,
        prefix: b,
        suffix: v,
        event: e
      };
      i.some((_) => {
        if (_.collapsed != null && _.collapsed !== E.collapsed || _.empty != null && _.empty !== E.empty || _.offset != null && _.offset !== E.offset)
          return !1;
        if (Array.isArray(_.format)) {
          if (_.format.every((O) => E.format[O] == null))
            return !1;
        } else if (typeof _.format == "object" && !Object.keys(_.format).every((O) => _.format[O] === !0 ? E.format[O] != null : _.format[O] === !1 ? E.format[O] == null : Hi(_.format[O], E.format[O])))
          return !1;
        return _.prefix != null && !_.prefix.test(E.prefix) || _.suffix != null && !_.suffix.test(E.suffix) ? !1 : _.handler.call(this, n, E, _) !== !0;
      }) && e.preventDefault();
    });
  }
  handleBackspace(e, s) {
    const r = /[\uD800-\uDBFF][\uDC00-\uDFFF]$/.test(s.prefix) ? 2 : 1;
    if (e.index === 0 || this.quill.getLength() <= 1) return;
    let i = {};
    const [a] = this.quill.getLine(e.index);
    let n = new j().retain(e.index - r).delete(r);
    if (s.offset === 0) {
      const [o] = this.quill.getLine(e.index - 1);
      if (o && !(o.statics.blotName === "block" && o.length() <= 1)) {
        const p = a.formats(), g = this.quill.getFormat(e.index - 1, 1);
        if (i = Ie.AttributeMap.diff(p, g) || {}, Object.keys(i).length > 0) {
          const k = new j().retain(e.index + a.length() - 2).retain(1, i);
          n = n.compose(k);
        }
      }
    }
    this.quill.updateContents(n, N.sources.USER), this.quill.focus();
  }
  handleDelete(e, s) {
    const r = /^[\uD800-\uDBFF][\uDC00-\uDFFF]/.test(s.suffix) ? 2 : 1;
    if (e.index >= this.quill.getLength() - r) return;
    let i = {};
    const [a] = this.quill.getLine(e.index);
    let n = new j().retain(e.index).delete(r);
    if (s.offset >= a.length() - 1) {
      const [o] = this.quill.getLine(e.index + 1);
      if (o) {
        const u = a.formats(), p = this.quill.getFormat(e.index, 1);
        i = Ie.AttributeMap.diff(u, p) || {}, Object.keys(i).length > 0 && (n = n.retain(o.length() - 1).retain(1, i));
      }
    }
    this.quill.updateContents(n, N.sources.USER), this.quill.focus();
  }
  handleDeleteRange(e) {
    sa({
      range: e,
      quill: this.quill
    }), this.quill.focus();
  }
  handleEnter(e, s) {
    const r = Object.keys(s.format).reduce((a, n) => (this.quill.scroll.query(n, V.BLOCK) && !Array.isArray(s.format[n]) && (a[n] = s.format[n]), a), {}), i = new j().retain(e.index).delete(e.length).insert(`
`, r);
    this.quill.updateContents(i, N.sources.USER), this.quill.setSelection(e.index + 1, N.sources.SILENT), this.quill.focus();
  }
}
const nw = {
  bindings: {
    bold: ai("bold"),
    italic: ai("italic"),
    underline: ai("underline"),
    indent: {
      // highlight tab or tab at beginning of list, indent or blockquote
      key: "Tab",
      format: ["blockquote", "indent", "list"],
      handler(t, e) {
        return e.collapsed && e.offset !== 0 ? !0 : (this.quill.format("indent", "+1", N.sources.USER), !1);
      }
    },
    outdent: {
      key: "Tab",
      shiftKey: !0,
      format: ["blockquote", "indent", "list"],
      // highlight tab or tab at beginning of list, indent or blockquote
      handler(t, e) {
        return e.collapsed && e.offset !== 0 ? !0 : (this.quill.format("indent", "-1", N.sources.USER), !1);
      }
    },
    "outdent backspace": {
      key: "Backspace",
      collapsed: !0,
      shiftKey: null,
      metaKey: null,
      ctrlKey: null,
      altKey: null,
      format: ["indent", "list"],
      offset: 0,
      handler(t, e) {
        e.format.indent != null ? this.quill.format("indent", "-1", N.sources.USER) : e.format.list != null && this.quill.format("list", !1, N.sources.USER);
      }
    },
    "indent code-block": Xa(!0),
    "outdent code-block": Xa(!1),
    "remove tab": {
      key: "Tab",
      shiftKey: !0,
      collapsed: !0,
      prefix: /\t$/,
      handler(t) {
        this.quill.deleteText(t.index - 1, 1, N.sources.USER);
      }
    },
    tab: {
      key: "Tab",
      handler(t, e) {
        if (e.format.table) return !0;
        this.quill.history.cutoff();
        const s = new j().retain(t.index).delete(t.length).insert("	");
        return this.quill.updateContents(s, N.sources.USER), this.quill.history.cutoff(), this.quill.setSelection(t.index + 1, N.sources.SILENT), !1;
      }
    },
    "blockquote empty enter": {
      key: "Enter",
      collapsed: !0,
      format: ["blockquote"],
      empty: !0,
      handler() {
        this.quill.format("blockquote", !1, N.sources.USER);
      }
    },
    "list empty enter": {
      key: "Enter",
      collapsed: !0,
      format: ["list"],
      empty: !0,
      handler(t, e) {
        const s = {
          list: !1
        };
        e.format.indent && (s.indent = !1), this.quill.formatLine(t.index, t.length, s, N.sources.USER);
      }
    },
    "checklist enter": {
      key: "Enter",
      collapsed: !0,
      format: {
        list: "checked"
      },
      handler(t) {
        const [e, s] = this.quill.getLine(t.index), r = {
          // @ts-expect-error Fix me later
          ...e.formats(),
          list: "checked"
        }, i = new j().retain(t.index).insert(`
`, r).retain(e.length() - s - 1).retain(1, {
          list: "unchecked"
        });
        this.quill.updateContents(i, N.sources.USER), this.quill.setSelection(t.index + 1, N.sources.SILENT), this.quill.scrollSelectionIntoView();
      }
    },
    "header enter": {
      key: "Enter",
      collapsed: !0,
      format: ["header"],
      suffix: /^$/,
      handler(t, e) {
        const [s, r] = this.quill.getLine(t.index), i = new j().retain(t.index).insert(`
`, e.format).retain(s.length() - r - 1).retain(1, {
          header: null
        });
        this.quill.updateContents(i, N.sources.USER), this.quill.setSelection(t.index + 1, N.sources.SILENT), this.quill.scrollSelectionIntoView();
      }
    },
    "table backspace": {
      key: "Backspace",
      format: ["table"],
      collapsed: !0,
      offset: 0,
      handler() {
      }
    },
    "table delete": {
      key: "Delete",
      format: ["table"],
      collapsed: !0,
      suffix: /^$/,
      handler() {
      }
    },
    "table enter": {
      key: "Enter",
      shiftKey: null,
      format: ["table"],
      handler(t) {
        const e = this.quill.getModule("table");
        if (e) {
          const [s, r, i, a] = e.getTable(t), n = iw(s, r, i, a);
          if (n == null) return;
          let o = s.offset();
          if (n < 0) {
            const u = new j().retain(o).insert(`
`);
            this.quill.updateContents(u, N.sources.USER), this.quill.setSelection(t.index + 1, t.length, N.sources.SILENT);
          } else if (n > 0) {
            o += s.length();
            const u = new j().retain(o).insert(`
`);
            this.quill.updateContents(u, N.sources.USER), this.quill.setSelection(o, N.sources.USER);
          }
        }
      }
    },
    "table tab": {
      key: "Tab",
      shiftKey: null,
      format: ["table"],
      handler(t, e) {
        const {
          event: s,
          line: r
        } = e, i = r.offset(this.quill.scroll);
        s.shiftKey ? this.quill.setSelection(i - 1, N.sources.USER) : this.quill.setSelection(i + r.length(), N.sources.USER);
      }
    },
    "list autofill": {
      key: " ",
      shiftKey: null,
      collapsed: !0,
      format: {
        "code-block": !1,
        blockquote: !1,
        table: !1
      },
      prefix: /^\s*?(\d+\.|-|\*|\[ ?\]|\[x\])$/,
      handler(t, e) {
        if (this.quill.scroll.query("list") == null) return !0;
        const {
          length: s
        } = e.prefix, [r, i] = this.quill.getLine(t.index);
        if (i > s) return !0;
        let a;
        switch (e.prefix.trim()) {
          case "[]":
          case "[ ]":
            a = "unchecked";
            break;
          case "[x]":
            a = "checked";
            break;
          case "-":
          case "*":
            a = "bullet";
            break;
          default:
            a = "ordered";
        }
        this.quill.insertText(t.index, " ", N.sources.USER), this.quill.history.cutoff();
        const n = new j().retain(t.index - i).delete(s + 1).retain(r.length() - 2 - i).retain(1, {
          list: a
        });
        return this.quill.updateContents(n, N.sources.USER), this.quill.history.cutoff(), this.quill.setSelection(t.index - s, N.sources.SILENT), !1;
      }
    },
    "code exit": {
      key: "Enter",
      collapsed: !0,
      format: ["code-block"],
      prefix: /^$/,
      suffix: /^\s*$/,
      handler(t) {
        const [e, s] = this.quill.getLine(t.index);
        let r = 2, i = e;
        for (; i != null && i.length() <= 1 && i.formats()["code-block"]; )
          if (i = i.prev, r -= 1, r <= 0) {
            const a = new j().retain(t.index + e.length() - s - 2).retain(1, {
              "code-block": null
            }).delete(1);
            return this.quill.updateContents(a, N.sources.USER), this.quill.setSelection(t.index - 1, N.sources.SILENT), !1;
          }
        return !0;
      }
    },
    "embed left": Pn("ArrowLeft", !1),
    "embed left shift": Pn("ArrowLeft", !0),
    "embed right": Pn("ArrowRight", !1),
    "embed right shift": Pn("ArrowRight", !0),
    "table down": Ya(!1),
    "table up": Ya(!0)
  }
};
xn.DEFAULTS = nw;
function Xa(t) {
  return {
    key: "Tab",
    shiftKey: !t,
    format: {
      "code-block": !0
    },
    handler(e, s) {
      let {
        event: r
      } = s;
      const i = this.quill.scroll.query("code-block"), {
        TAB: a
      } = i;
      if (e.length === 0 && !r.shiftKey) {
        this.quill.insertText(e.index, a, N.sources.USER), this.quill.setSelection(e.index + a.length, N.sources.SILENT);
        return;
      }
      const n = e.length === 0 ? this.quill.getLines(e.index, 1) : this.quill.getLines(e);
      let {
        index: o,
        length: u
      } = e;
      n.forEach((p, g) => {
        t ? (p.insertAt(0, a), g === 0 ? o += a.length : u += a.length) : p.domNode.textContent.startsWith(a) && (p.deleteAt(0, a.length), g === 0 ? o -= a.length : u -= a.length);
      }), this.quill.update(N.sources.USER), this.quill.setSelection(o, u, N.sources.SILENT);
    }
  };
}
function Pn(t, e) {
  return {
    key: t,
    shiftKey: e,
    altKey: null,
    [t === "ArrowLeft" ? "prefix" : "suffix"]: /^$/,
    handler(r) {
      let {
        index: i
      } = r;
      t === "ArrowRight" && (i += r.length + 1);
      const [a] = this.quill.getLeaf(i);
      return a instanceof Ae ? (t === "ArrowLeft" ? e ? this.quill.setSelection(r.index - 1, r.length + 1, N.sources.USER) : this.quill.setSelection(r.index - 1, N.sources.USER) : e ? this.quill.setSelection(r.index, r.length + 1, N.sources.USER) : this.quill.setSelection(r.index + r.length + 1, N.sources.USER), !1) : !0;
    }
  };
}
function ai(t) {
  return {
    key: t[0],
    shortKey: !0,
    handler(e, s) {
      this.quill.format(t, !s.format[t], N.sources.USER);
    }
  };
}
function Ya(t) {
  return {
    key: t ? "ArrowUp" : "ArrowDown",
    collapsed: !0,
    format: ["table"],
    handler(e, s) {
      const r = t ? "prev" : "next", i = s.line, a = i.parent[r];
      if (a != null) {
        if (a.statics.blotName === "table-row") {
          let n = a.children.head, o = i;
          for (; o.prev != null; )
            o = o.prev, n = n.next;
          const u = n.offset(this.quill.scroll) + Math.min(s.offset, n.length() - 1);
          this.quill.setSelection(u, 0, N.sources.USER);
        }
      } else {
        const n = i.table()[r];
        n != null && (t ? this.quill.setSelection(n.offset(this.quill.scroll) + n.length() - 1, 0, N.sources.USER) : this.quill.setSelection(n.offset(this.quill.scroll), 0, N.sources.USER));
      }
      return !1;
    }
  };
}
function rw(t) {
  if (typeof t == "string" || typeof t == "number")
    t = {
      key: t
    };
  else if (typeof t == "object")
    t = rs(t);
  else
    return null;
  return t.shortKey && (t[sw] = t.shortKey, delete t.shortKey), t;
}
function sa(t) {
  let {
    quill: e,
    range: s
  } = t;
  const r = e.getLines(s);
  let i = {};
  if (r.length > 1) {
    const a = r[0].formats(), n = r[r.length - 1].formats();
    i = Ie.AttributeMap.diff(n, a) || {};
  }
  e.deleteText(s, N.sources.USER), Object.keys(i).length > 0 && e.formatLine(s.index, 1, i, N.sources.USER), e.setSelection(s.index, N.sources.SILENT);
}
function iw(t, e, s, r) {
  return e.prev == null && e.next == null ? s.prev == null && s.next == null ? r === 0 ? -1 : 1 : s.prev == null ? -1 : 1 : e.prev == null ? -1 : e.next == null ? 1 : null;
}
const aw = /font-weight:\s*normal/, ow = ["P", "OL", "UL"], Qa = (t) => t && ow.includes(t.tagName), lw = (t) => {
  Array.from(t.querySelectorAll("br")).filter((e) => Qa(e.previousElementSibling) && Qa(e.nextElementSibling)).forEach((e) => {
    var s;
    (s = e.parentNode) == null || s.removeChild(e);
  });
}, uw = (t) => {
  Array.from(t.querySelectorAll('b[style*="font-weight"]')).filter((e) => {
    var s;
    return (s = e.getAttribute("style")) == null ? void 0 : s.match(aw);
  }).forEach((e) => {
    var r;
    const s = t.createDocumentFragment();
    s.append(...e.childNodes), (r = e.parentNode) == null || r.replaceChild(s, e);
  });
};
function dw(t) {
  t.querySelector('[id^="docs-internal-guid-"]') && (uw(t), lw(t));
}
const cw = /\bmso-list:[^;]*ignore/i, fw = /\bmso-list:[^;]*\bl(\d+)/i, pw = /\bmso-list:[^;]*\blevel(\d+)/i, hw = (t, e) => {
  const s = t.getAttribute("style"), r = s == null ? void 0 : s.match(fw);
  if (!r)
    return null;
  const i = Number(r[1]), a = s == null ? void 0 : s.match(pw), n = a ? Number(a[1]) : 1, o = new RegExp(`@list l${i}:level${n}\\s*\\{[^\\}]*mso-level-number-format:\\s*([\\w-]+)`, "i"), u = e.match(o), p = u && u[1] === "bullet" ? "bullet" : "ordered";
  return {
    id: i,
    indent: n,
    type: p,
    element: t
  };
}, gw = (t) => {
  var n, o;
  const e = Array.from(t.querySelectorAll("[style*=mso-list]")), s = [], r = [];
  e.forEach((u) => {
    (u.getAttribute("style") || "").match(cw) ? s.push(u) : r.push(u);
  }), s.forEach((u) => {
    var p;
    return (p = u.parentNode) == null ? void 0 : p.removeChild(u);
  });
  const i = t.documentElement.innerHTML, a = r.map((u) => hw(u, i)).filter((u) => u);
  for (; a.length; ) {
    const u = [];
    let p = a.shift();
    for (; p; )
      u.push(p), p = a.length && ((n = a[0]) == null ? void 0 : n.element) === p.element.nextElementSibling && // Different id means the next item doesn't belong to this group.
      a[0].id === p.id ? a.shift() : null;
    const g = document.createElement("ul");
    u.forEach((b) => {
      const v = document.createElement("li");
      v.setAttribute("data-list", b.type), b.indent > 1 && v.setAttribute("class", `ql-indent-${b.indent - 1}`), v.innerHTML = b.element.innerHTML, g.appendChild(v);
    });
    const k = (o = u[0]) == null ? void 0 : o.element, {
      parentNode: y
    } = k ?? {};
    k && (y == null || y.replaceChild(g, k)), u.slice(1).forEach((b) => {
      let {
        element: v
      } = b;
      y == null || y.removeChild(v);
    });
  }
};
function mw(t) {
  t.documentElement.getAttribute("xmlns:w") === "urn:schemas-microsoft-com:office:word" && gw(t);
}
const vw = [mw, dw], bw = (t) => {
  t.documentElement && vw.forEach((e) => {
    e(t);
  });
}, yw = ct("quill:clipboard"), $w = [[Node.TEXT_NODE, qw], [Node.TEXT_NODE, xa], ["br", Ew], [Node.ELEMENT_NODE, xa], [Node.ELEMENT_NODE, Aw], [Node.ELEMENT_NODE, Cw], [Node.ELEMENT_NODE, Iw], ["li", _w], ["ol, ul", Nw], ["pre", Sw], ["tr", Lw], ["b", oi("bold")], ["i", oi("italic")], ["strike", oi("strike")], ["style", Tw]], kw = [Qk, sl].reduce((t, e) => (t[e.keyName] = e, t), {}), Ja = [el, xi, Ji, rl, ol, ul].reduce((t, e) => (t[e.keyName] = e, t), {});
class dl extends ze {
  constructor(e, s) {
    super(e, s), this.quill.root.addEventListener("copy", (r) => this.onCaptureCopy(r, !1)), this.quill.root.addEventListener("cut", (r) => this.onCaptureCopy(r, !0)), this.quill.root.addEventListener("paste", this.onCapturePaste.bind(this)), this.matchers = [], $w.concat(this.options.matchers ?? []).forEach((r) => {
      let [i, a] = r;
      this.addMatcher(i, a);
    });
  }
  addMatcher(e, s) {
    this.matchers.push([e, s]);
  }
  convert(e) {
    let {
      html: s,
      text: r
    } = e, i = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
    if (i[me.blotName])
      return new j().insert(r || "", {
        [me.blotName]: i[me.blotName]
      });
    if (!s)
      return new j().insert(r || "", i);
    const a = this.convertHTML(s);
    return Qs(a, `
`) && (a.ops[a.ops.length - 1].attributes == null || i.table) ? a.compose(new j().retain(a.length() - 1).delete(1)) : a;
  }
  normalizeHTML(e) {
    bw(e);
  }
  convertHTML(e) {
    const s = new DOMParser().parseFromString(e, "text/html");
    this.normalizeHTML(s);
    const r = s.body, i = /* @__PURE__ */ new WeakMap(), [a, n] = this.prepareMatching(r, i);
    return na(this.quill.scroll, r, a, n, i);
  }
  dangerouslyPasteHTML(e, s) {
    let r = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : N.sources.API;
    if (typeof e == "string") {
      const i = this.convert({
        html: e,
        text: ""
      });
      this.quill.setContents(i, s), this.quill.setSelection(0, N.sources.SILENT);
    } else {
      const i = this.convert({
        html: s,
        text: ""
      });
      this.quill.updateContents(new j().retain(e).concat(i), r), this.quill.setSelection(e + i.length(), N.sources.SILENT);
    }
  }
  onCaptureCopy(e) {
    var n, o;
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1;
    if (e.defaultPrevented) return;
    e.preventDefault();
    const [r] = this.quill.selection.getRange();
    if (r == null) return;
    const {
      html: i,
      text: a
    } = this.onCopy(r, s);
    (n = e.clipboardData) == null || n.setData("text/plain", a), (o = e.clipboardData) == null || o.setData("text/html", i), s && sa({
      range: r,
      quill: this.quill
    });
  }
  /*
   * https://www.iana.org/assignments/media-types/text/uri-list
   */
  normalizeURIList(e) {
    return e.split(/\r?\n/).filter((s) => s[0] !== "#").join(`
`);
  }
  onCapturePaste(e) {
    var n, o, u, p, g;
    if (e.defaultPrevented || !this.quill.isEnabled()) return;
    e.preventDefault();
    const s = this.quill.getSelection(!0);
    if (s == null) return;
    const r = (n = e.clipboardData) == null ? void 0 : n.getData("text/html");
    let i = (o = e.clipboardData) == null ? void 0 : o.getData("text/plain");
    if (!r && !i) {
      const k = (u = e.clipboardData) == null ? void 0 : u.getData("text/uri-list");
      k && (i = this.normalizeURIList(k));
    }
    const a = Array.from(((p = e.clipboardData) == null ? void 0 : p.files) || []);
    if (!r && a.length > 0) {
      this.quill.uploader.upload(s, a);
      return;
    }
    if (r && a.length > 0) {
      const k = new DOMParser().parseFromString(r, "text/html");
      if (k.body.childElementCount === 1 && ((g = k.body.firstElementChild) == null ? void 0 : g.tagName) === "IMG") {
        this.quill.uploader.upload(s, a);
        return;
      }
    }
    this.onPaste(s, {
      html: r,
      text: i
    });
  }
  onCopy(e) {
    const s = this.quill.getText(e);
    return {
      html: this.quill.getSemanticHTML(e),
      text: s
    };
  }
  onPaste(e, s) {
    let {
      text: r,
      html: i
    } = s;
    const a = this.quill.getFormat(e.index), n = this.convert({
      text: r,
      html: i
    }, a);
    yw.log("onPaste", n, {
      text: r,
      html: i
    });
    const o = new j().retain(e.index).delete(e.length).concat(n);
    this.quill.updateContents(o, N.sources.USER), this.quill.setSelection(o.length() - e.length, N.sources.SILENT), this.quill.scrollSelectionIntoView();
  }
  prepareMatching(e, s) {
    const r = [], i = [];
    return this.matchers.forEach((a) => {
      const [n, o] = a;
      switch (n) {
        case Node.TEXT_NODE:
          i.push(o);
          break;
        case Node.ELEMENT_NODE:
          r.push(o);
          break;
        default:
          Array.from(e.querySelectorAll(n)).forEach((u) => {
            if (s.has(u)) {
              const p = s.get(u);
              p == null || p.push(o);
            } else
              s.set(u, [o]);
          });
          break;
      }
    }), [r, i];
  }
}
B(dl, "DEFAULTS", {
  matchers: []
});
function Ut(t, e, s, r) {
  return r.query(e) ? t.reduce((i, a) => {
    if (!a.insert) return i;
    if (a.attributes && a.attributes[e])
      return i.push(a);
    const n = s ? {
      [e]: s
    } : {};
    return i.insert(a.insert, {
      ...n,
      ...a.attributes
    });
  }, new j()) : t;
}
function Qs(t, e) {
  let s = "";
  for (let r = t.ops.length - 1; r >= 0 && s.length < e.length; --r) {
    const i = t.ops[r];
    if (typeof i.insert != "string") break;
    s = i.insert + s;
  }
  return s.slice(-1 * e.length) === e;
}
function vt(t, e) {
  if (!(t instanceof Element)) return !1;
  const s = e.query(t);
  return s && s.prototype instanceof Ae ? !1 : ["address", "article", "blockquote", "canvas", "dd", "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "iframe", "li", "main", "nav", "ol", "output", "p", "pre", "section", "table", "td", "tr", "ul", "video"].includes(t.tagName.toLowerCase());
}
function ww(t, e) {
  return t.previousElementSibling && t.nextElementSibling && !vt(t.previousElementSibling, e) && !vt(t.nextElementSibling, e);
}
const Dn = /* @__PURE__ */ new WeakMap();
function cl(t) {
  return t == null ? !1 : (Dn.has(t) || (t.tagName === "PRE" ? Dn.set(t, !0) : Dn.set(t, cl(t.parentNode))), Dn.get(t));
}
function na(t, e, s, r, i) {
  return e.nodeType === e.TEXT_NODE ? r.reduce((a, n) => n(e, a, t), new j()) : e.nodeType === e.ELEMENT_NODE ? Array.from(e.childNodes || []).reduce((a, n) => {
    let o = na(t, n, s, r, i);
    return n.nodeType === e.ELEMENT_NODE && (o = s.reduce((u, p) => p(n, u, t), o), o = (i.get(n) || []).reduce((u, p) => p(n, u, t), o)), a.concat(o);
  }, new j()) : new j();
}
function oi(t) {
  return (e, s, r) => Ut(s, t, !0, r);
}
function Cw(t, e, s) {
  const r = Je.keys(t), i = Ve.keys(t), a = wt.keys(t), n = {};
  return r.concat(i).concat(a).forEach((o) => {
    let u = s.query(o, V.ATTRIBUTE);
    u != null && (n[u.attrName] = u.value(t), n[u.attrName]) || (u = kw[o], u != null && (u.attrName === o || u.keyName === o) && (n[u.attrName] = u.value(t) || void 0), u = Ja[o], u != null && (u.attrName === o || u.keyName === o) && (u = Ja[o], n[u.attrName] = u.value(t) || void 0));
  }), Object.entries(n).reduce((o, u) => {
    let [p, g] = u;
    return Ut(o, p, g, s);
  }, e);
}
function Aw(t, e, s) {
  const r = s.query(t);
  if (r == null) return e;
  if (r.prototype instanceof Ae) {
    const i = {}, a = r.value(t);
    if (a != null)
      return i[r.blotName] = a, new j().insert(i, r.formats(t, s));
  } else if (r.prototype instanceof Gs && !Qs(e, `
`) && e.insert(`
`), "blotName" in r && "formats" in r && typeof r.formats == "function")
    return Ut(e, r.blotName, r.formats(t, s), s);
  return e;
}
function Ew(t, e) {
  return Qs(e, `
`) || e.insert(`
`), e;
}
function Sw(t, e, s) {
  const r = s.query("code-block"), i = r && "formats" in r && typeof r.formats == "function" ? r.formats(t, s) : !0;
  return Ut(e, "code-block", i, s);
}
function Tw() {
  return new j();
}
function _w(t, e, s) {
  const r = s.query(t);
  if (r == null || // @ts-expect-error
  r.blotName !== "list" || !Qs(e, `
`))
    return e;
  let i = -1, a = t.parentNode;
  for (; a != null; )
    ["OL", "UL"].includes(a.tagName) && (i += 1), a = a.parentNode;
  return i <= 0 ? e : e.reduce((n, o) => o.insert ? o.attributes && typeof o.attributes.indent == "number" ? n.push(o) : n.insert(o.insert, {
    indent: i,
    ...o.attributes || {}
  }) : n, new j());
}
function Nw(t, e, s) {
  const r = t;
  let i = r.tagName === "OL" ? "ordered" : "bullet";
  const a = r.getAttribute("data-checked");
  return a && (i = a === "true" ? "checked" : "unchecked"), Ut(e, "list", i, s);
}
function xa(t, e, s) {
  if (!Qs(e, `
`)) {
    if (vt(t, s) && (t.childNodes.length > 0 || t instanceof HTMLParagraphElement))
      return e.insert(`
`);
    if (e.length() > 0 && t.nextSibling) {
      let r = t.nextSibling;
      for (; r != null; ) {
        if (vt(r, s))
          return e.insert(`
`);
        const i = s.query(r);
        if (i && i.prototype instanceof Ne)
          return e.insert(`
`);
        r = r.firstChild;
      }
    }
  }
  return e;
}
function Iw(t, e, s) {
  var a;
  const r = {}, i = t.style || {};
  return i.fontStyle === "italic" && (r.italic = !0), i.textDecoration === "underline" && (r.underline = !0), i.textDecoration === "line-through" && (r.strike = !0), ((a = i.fontWeight) != null && a.startsWith("bold") || // @ts-expect-error Fix me later
  parseInt(i.fontWeight, 10) >= 700) && (r.bold = !0), e = Object.entries(r).reduce((n, o) => {
    let [u, p] = o;
    return Ut(n, u, p, s);
  }, e), parseFloat(i.textIndent || 0) > 0 ? new j().insert("	").concat(e) : e;
}
function Lw(t, e, s) {
  var i, a;
  const r = ((i = t.parentElement) == null ? void 0 : i.tagName) === "TABLE" ? t.parentElement : (a = t.parentElement) == null ? void 0 : a.parentElement;
  if (r != null) {
    const o = Array.from(r.querySelectorAll("tr")).indexOf(t) + 1;
    return Ut(e, "table", o, s);
  }
  return e;
}
function qw(t, e, s) {
  var i;
  let r = t.data;
  if (((i = t.parentElement) == null ? void 0 : i.tagName) === "O:P")
    return e.insert(r.trim());
  if (!cl(t)) {
    if (r.trim().length === 0 && r.includes(`
`) && !ww(t, s))
      return e;
    r = r.replace(/[^\S\u00a0]/g, " "), r = r.replace(/ {2,}/g, " "), (t.previousSibling == null && t.parentElement != null && vt(t.parentElement, s) || t.previousSibling instanceof Element && vt(t.previousSibling, s)) && (r = r.replace(/^ /, "")), (t.nextSibling == null && t.parentElement != null && vt(t.parentElement, s) || t.nextSibling instanceof Element && vt(t.nextSibling, s)) && (r = r.replace(/ $/, "")), r = r.replaceAll(" ", " ");
  }
  return e.insert(r);
}
class fl extends ze {
  constructor(s, r) {
    super(s, r);
    B(this, "lastRecorded", 0);
    B(this, "ignoreChange", !1);
    B(this, "stack", {
      undo: [],
      redo: []
    });
    B(this, "currentRange", null);
    this.quill.on(N.events.EDITOR_CHANGE, (i, a, n, o) => {
      i === N.events.SELECTION_CHANGE ? a && o !== N.sources.SILENT && (this.currentRange = a) : i === N.events.TEXT_CHANGE && (this.ignoreChange || (!this.options.userOnly || o === N.sources.USER ? this.record(a, n) : this.transform(a)), this.currentRange = Ti(this.currentRange, a));
    }), this.quill.keyboard.addBinding({
      key: "z",
      shortKey: !0
    }, this.undo.bind(this)), this.quill.keyboard.addBinding({
      key: ["z", "Z"],
      shortKey: !0,
      shiftKey: !0
    }, this.redo.bind(this)), /Win/i.test(navigator.platform) && this.quill.keyboard.addBinding({
      key: "y",
      shortKey: !0
    }, this.redo.bind(this)), this.quill.root.addEventListener("beforeinput", (i) => {
      i.inputType === "historyUndo" ? (this.undo(), i.preventDefault()) : i.inputType === "historyRedo" && (this.redo(), i.preventDefault());
    });
  }
  change(s, r) {
    if (this.stack[s].length === 0) return;
    const i = this.stack[s].pop();
    if (!i) return;
    const a = this.quill.getContents(), n = i.delta.invert(a);
    this.stack[r].push({
      delta: n,
      range: Ti(i.range, n)
    }), this.lastRecorded = 0, this.ignoreChange = !0, this.quill.updateContents(i.delta, N.sources.USER), this.ignoreChange = !1, this.restoreSelection(i);
  }
  clear() {
    this.stack = {
      undo: [],
      redo: []
    };
  }
  cutoff() {
    this.lastRecorded = 0;
  }
  record(s, r) {
    if (s.ops.length === 0) return;
    this.stack.redo = [];
    let i = s.invert(r), a = this.currentRange;
    const n = Date.now();
    if (
      // @ts-expect-error Fix me later
      this.lastRecorded + this.options.delay > n && this.stack.undo.length > 0
    ) {
      const o = this.stack.undo.pop();
      o && (i = i.compose(o.delta), a = o.range);
    } else
      this.lastRecorded = n;
    i.length() !== 0 && (this.stack.undo.push({
      delta: i,
      range: a
    }), this.stack.undo.length > this.options.maxStack && this.stack.undo.shift());
  }
  redo() {
    this.change("redo", "undo");
  }
  transform(s) {
    eo(this.stack.undo, s), eo(this.stack.redo, s);
  }
  undo() {
    this.change("undo", "redo");
  }
  restoreSelection(s) {
    if (s.range)
      this.quill.setSelection(s.range, N.sources.USER);
    else {
      const r = Pw(this.quill.scroll, s.delta);
      this.quill.setSelection(r, N.sources.USER);
    }
  }
}
B(fl, "DEFAULTS", {
  delay: 1e3,
  maxStack: 100,
  userOnly: !1
});
function eo(t, e) {
  let s = e;
  for (let r = t.length - 1; r >= 0; r -= 1) {
    const i = t[r];
    t[r] = {
      delta: s.transform(i.delta, !0),
      range: i.range && Ti(i.range, s)
    }, s = i.delta.transform(s), t[r].delta.length() === 0 && t.splice(r, 1);
  }
}
function Ow(t, e) {
  const s = e.ops[e.ops.length - 1];
  return s == null ? !1 : s.insert != null ? typeof s.insert == "string" && s.insert.endsWith(`
`) : s.attributes != null ? Object.keys(s.attributes).some((r) => t.query(r, V.BLOCK) != null) : !1;
}
function Pw(t, e) {
  const s = e.reduce((i, a) => i + (a.delete || 0), 0);
  let r = e.length() - s;
  return Ow(t, e) && (r -= 1), r;
}
function Ti(t, e) {
  if (!t) return t;
  const s = e.transformPosition(t.index), r = e.transformPosition(t.index + t.length);
  return {
    index: s,
    length: r - s
  };
}
class pl extends ze {
  constructor(e, s) {
    super(e, s), e.root.addEventListener("drop", (r) => {
      var n;
      r.preventDefault();
      let i = null;
      if (document.caretRangeFromPoint)
        i = document.caretRangeFromPoint(r.clientX, r.clientY);
      else if (document.caretPositionFromPoint) {
        const o = document.caretPositionFromPoint(r.clientX, r.clientY);
        i = document.createRange(), i.setStart(o.offsetNode, o.offset), i.setEnd(o.offsetNode, o.offset);
      }
      const a = i && e.selection.normalizeNative(i);
      if (a) {
        const o = e.selection.normalizedToRange(a);
        (n = r.dataTransfer) != null && n.files && this.upload(o, r.dataTransfer.files);
      }
    });
  }
  upload(e, s) {
    const r = [];
    Array.from(s).forEach((i) => {
      var a;
      i && ((a = this.options.mimetypes) != null && a.includes(i.type)) && r.push(i);
    }), r.length > 0 && this.options.handler.call(this, e, r);
  }
}
pl.DEFAULTS = {
  mimetypes: ["image/png", "image/jpeg"],
  handler(t, e) {
    if (!this.quill.scroll.query("image"))
      return;
    const s = e.map((r) => new Promise((i) => {
      const a = new FileReader();
      a.onload = () => {
        i(a.result);
      }, a.readAsDataURL(r);
    }));
    Promise.all(s).then((r) => {
      const i = r.reduce((a, n) => a.insert({
        image: n
      }), new j().retain(t.index).delete(t.length));
      this.quill.updateContents(i, F.sources.USER), this.quill.setSelection(t.index + r.length, F.sources.SILENT);
    });
  }
};
const Dw = ["insertText", "insertReplacementText"];
class Rw extends ze {
  constructor(e, s) {
    super(e, s), e.root.addEventListener("beforeinput", (r) => {
      this.handleBeforeInput(r);
    }), /Android/i.test(navigator.userAgent) || e.on(N.events.COMPOSITION_BEFORE_START, () => {
      this.handleCompositionStart();
    });
  }
  deleteRange(e) {
    sa({
      range: e,
      quill: this.quill
    });
  }
  replaceText(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "";
    if (e.length === 0) return !1;
    if (s) {
      const r = this.quill.getFormat(e.index, 1);
      this.deleteRange(e), this.quill.updateContents(new j().retain(e.index).insert(s, r), N.sources.USER);
    } else
      this.deleteRange(e);
    return this.quill.setSelection(e.index + s.length, 0, N.sources.SILENT), !0;
  }
  handleBeforeInput(e) {
    if (this.quill.composition.isComposing || e.defaultPrevented || !Dw.includes(e.inputType))
      return;
    const s = e.getTargetRanges ? e.getTargetRanges()[0] : null;
    if (!s || s.collapsed === !0)
      return;
    const r = Bw(e);
    if (r == null)
      return;
    const i = this.quill.selection.normalizeNative(s), a = i ? this.quill.selection.normalizedToRange(i) : null;
    a && this.replaceText(a, r) && e.preventDefault();
  }
  handleCompositionStart() {
    const e = this.quill.getSelection();
    e && this.replaceText(e);
  }
}
function Bw(t) {
  var e;
  return typeof t.data == "string" ? t.data : (e = t.dataTransfer) != null && e.types.includes("text/plain") ? t.dataTransfer.getData("text/plain") : null;
}
const Mw = /Mac/i.test(navigator.platform), Fw = 100, Uw = (t) => !!(t.key === "ArrowLeft" || t.key === "ArrowRight" || // RTL scripts or moving from the end of the previous line
t.key === "ArrowUp" || t.key === "ArrowDown" || t.key === "Home" || Mw && t.key === "a" && t.ctrlKey === !0);
class jw extends ze {
  constructor(s, r) {
    super(s, r);
    B(this, "isListening", !1);
    B(this, "selectionChangeDeadline", 0);
    this.handleArrowKeys(), this.handleNavigationShortcuts();
  }
  handleArrowKeys() {
    this.quill.keyboard.addBinding({
      key: ["ArrowLeft", "ArrowRight"],
      offset: 0,
      shiftKey: null,
      handler(s, r) {
        let {
          line: i,
          event: a
        } = r;
        if (!(i instanceof Ue) || !i.uiNode)
          return !0;
        const n = getComputedStyle(i.domNode).direction === "rtl";
        return n && a.key !== "ArrowRight" || !n && a.key !== "ArrowLeft" ? !0 : (this.quill.setSelection(s.index - 1, s.length + (a.shiftKey ? 1 : 0), N.sources.USER), !1);
      }
    });
  }
  handleNavigationShortcuts() {
    this.quill.root.addEventListener("keydown", (s) => {
      !s.defaultPrevented && Uw(s) && this.ensureListeningToSelectionChange();
    });
  }
  /**
   * We only listen to the `selectionchange` event when
   * there is an intention of moving the caret to the beginning using shortcuts.
   * This is primarily implemented to prevent infinite loops, as we are changing
   * the selection within the handler of a `selectionchange` event.
   */
  ensureListeningToSelectionChange() {
    if (this.selectionChangeDeadline = Date.now() + Fw, this.isListening) return;
    this.isListening = !0;
    const s = () => {
      this.isListening = !1, Date.now() <= this.selectionChangeDeadline && this.handleSelectionChange();
    };
    document.addEventListener("selectionchange", s, {
      once: !0
    });
  }
  handleSelectionChange() {
    const s = document.getSelection();
    if (!s) return;
    const r = s.getRangeAt(0);
    if (r.collapsed !== !0 || r.startOffset !== 0) return;
    const i = this.quill.scroll.find(r.startContainer);
    if (!(i instanceof Ue) || !i.uiNode) return;
    const a = document.createRange();
    a.setStartAfter(i.uiNode), a.setEndAfter(i.uiNode), s.removeAllRanges(), s.addRange(a);
  }
}
N.register({
  "blots/block": ce,
  "blots/block/embed": Ne,
  "blots/break": He,
  "blots/container": Mt,
  "blots/cursor": us,
  "blots/embed": Yi,
  "blots/inline": xe,
  "blots/scroll": ns,
  "blots/text": je,
  "modules/clipboard": dl,
  "modules/history": fl,
  "modules/keyboard": xn,
  "modules/uploader": pl,
  "modules/input": Rw,
  "modules/uiNode": jw
});
class Vw extends Ve {
  add(e, s) {
    let r = 0;
    if (s === "+1" || s === "-1") {
      const i = this.value(e) || 0;
      r = s === "+1" ? i + 1 : i - 1;
    } else typeof s == "number" && (r = s);
    return r === 0 ? (this.remove(e), !0) : super.add(e, r.toString());
  }
  canAdd(e, s) {
    return super.canAdd(e, s) || super.canAdd(e, parseInt(s, 10));
  }
  value(e) {
    return parseInt(super.value(e), 10) || void 0;
  }
}
const Hw = new Vw("indent", "ql-indent", {
  scope: V.BLOCK,
  // @ts-expect-error
  whitelist: [1, 2, 3, 4, 5, 6, 7, 8]
});
class _i extends ce {
}
B(_i, "blotName", "blockquote"), B(_i, "tagName", "blockquote");
class Ni extends ce {
  static formats(e) {
    return this.tagName.indexOf(e.tagName) + 1;
  }
}
B(Ni, "blotName", "header"), B(Ni, "tagName", ["H1", "H2", "H3", "H4", "H5", "H6"]);
class Js extends Mt {
}
Js.blotName = "list-container";
Js.tagName = "OL";
class xs extends ce {
  static create(e) {
    const s = super.create();
    return s.setAttribute("data-list", e), s;
  }
  static formats(e) {
    return e.getAttribute("data-list") || void 0;
  }
  static register() {
    N.register(Js);
  }
  constructor(e, s) {
    super(e, s);
    const r = s.ownerDocument.createElement("span"), i = (a) => {
      if (!e.isEnabled()) return;
      const n = this.statics.formats(s, e);
      n === "checked" ? (this.format("list", "unchecked"), a.preventDefault()) : n === "unchecked" && (this.format("list", "checked"), a.preventDefault());
    };
    r.addEventListener("mousedown", i), r.addEventListener("touchstart", i), this.attachUI(r);
  }
  format(e, s) {
    e === this.statics.blotName && s ? this.domNode.setAttribute("data-list", s) : super.format(e, s);
  }
}
xs.blotName = "list";
xs.tagName = "LI";
Js.allowedChildren = [xs];
xs.requiredContainer = Js;
class Zs extends xe {
  static create() {
    return super.create();
  }
  static formats() {
    return !0;
  }
  optimize(e) {
    super.optimize(e), this.domNode.tagName !== this.statics.tagName[0] && this.replaceWith(this.statics.blotName);
  }
}
B(Zs, "blotName", "bold"), B(Zs, "tagName", ["STRONG", "B"]);
class Ii extends Zs {
}
B(Ii, "blotName", "italic"), B(Ii, "tagName", ["EM", "I"]);
class bt extends xe {
  static create(e) {
    const s = super.create(e);
    return s.setAttribute("href", this.sanitize(e)), s.setAttribute("rel", "noopener noreferrer"), s.setAttribute("target", "_blank"), s;
  }
  static formats(e) {
    return e.getAttribute("href");
  }
  static sanitize(e) {
    return hl(e, this.PROTOCOL_WHITELIST) ? e : this.SANITIZED_URL;
  }
  format(e, s) {
    e !== this.statics.blotName || !s ? super.format(e, s) : this.domNode.setAttribute("href", this.constructor.sanitize(s));
  }
}
B(bt, "blotName", "link"), B(bt, "tagName", "A"), B(bt, "SANITIZED_URL", "about:blank"), B(bt, "PROTOCOL_WHITELIST", ["http", "https", "mailto", "tel", "sms"]);
function hl(t, e) {
  const s = document.createElement("a");
  s.href = t;
  const r = s.href.slice(0, s.href.indexOf(":"));
  return e.indexOf(r) > -1;
}
class Li extends xe {
  static create(e) {
    return e === "super" ? document.createElement("sup") : e === "sub" ? document.createElement("sub") : super.create(e);
  }
  static formats(e) {
    if (e.tagName === "SUB") return "sub";
    if (e.tagName === "SUP") return "super";
  }
}
B(Li, "blotName", "script"), B(Li, "tagName", ["SUB", "SUP"]);
class qi extends Zs {
}
B(qi, "blotName", "strike"), B(qi, "tagName", ["S", "STRIKE"]);
class Oi extends xe {
}
B(Oi, "blotName", "underline"), B(Oi, "tagName", "U");
class Bn extends Yi {
  static create(e) {
    if (window.katex == null)
      throw new Error("Formula module requires KaTeX.");
    const s = super.create(e);
    return typeof e == "string" && (window.katex.render(e, s, {
      throwOnError: !1,
      errorColor: "#f00"
    }), s.setAttribute("data-value", e)), s;
  }
  static value(e) {
    return e.getAttribute("data-value");
  }
  html() {
    const {
      formula: e
    } = this.value();
    return `<span>${e}</span>`;
  }
}
B(Bn, "blotName", "formula"), B(Bn, "className", "ql-formula"), B(Bn, "tagName", "SPAN");
const to = ["alt", "height", "width"];
class Pi extends Ae {
  static create(e) {
    const s = super.create(e);
    return typeof e == "string" && s.setAttribute("src", this.sanitize(e)), s;
  }
  static formats(e) {
    return to.reduce((s, r) => (e.hasAttribute(r) && (s[r] = e.getAttribute(r)), s), {});
  }
  static match(e) {
    return /\.(jpe?g|gif|png)$/.test(e) || /^data:image\/.+;base64/.test(e);
  }
  static sanitize(e) {
    return hl(e, ["http", "https", "data"]) ? e : "//:0";
  }
  static value(e) {
    return e.getAttribute("src");
  }
  format(e, s) {
    to.indexOf(e) > -1 ? s ? this.domNode.setAttribute(e, s) : this.domNode.removeAttribute(e) : super.format(e, s);
  }
}
B(Pi, "blotName", "image"), B(Pi, "tagName", "IMG");
const so = ["height", "width"];
var Ds;
let zw = (Ds = class extends Ne {
  static create(e) {
    const s = super.create(e);
    return s.setAttribute("frameborder", "0"), s.setAttribute("allowfullscreen", "true"), s.setAttribute("src", this.sanitize(e)), s;
  }
  static formats(e) {
    return so.reduce((s, r) => (e.hasAttribute(r) && (s[r] = e.getAttribute(r)), s), {});
  }
  static sanitize(e) {
    return bt.sanitize(e);
  }
  static value(e) {
    return e.getAttribute("src");
  }
  format(e, s) {
    so.indexOf(e) > -1 ? s ? this.domNode.setAttribute(e, s) : this.domNode.removeAttribute(e) : super.format(e, s);
  }
  html() {
    const {
      video: e
    } = this.value();
    return `<a href="${e}">${e}</a>`;
  }
}, B(Ds, "blotName", "video"), B(Ds, "className", "ql-video"), B(Ds, "tagName", "IFRAME"), Ds);
const Bs = new Ve("code-token", "hljs", {
  scope: V.INLINE
});
class lt extends xe {
  static formats(e, s) {
    for (; e != null && e !== s.domNode; ) {
      if (e.classList && e.classList.contains(me.className))
        return super.formats(e, s);
      e = e.parentNode;
    }
  }
  constructor(e, s, r) {
    super(e, s, r), Bs.add(this.domNode, r);
  }
  format(e, s) {
    e !== lt.blotName ? super.format(e, s) : s ? Bs.add(this.domNode, s) : (Bs.remove(this.domNode), this.domNode.classList.remove(this.statics.className));
  }
  optimize() {
    super.optimize(...arguments), Bs.value(this.domNode) || this.unwrap();
  }
}
lt.blotName = "code-token";
lt.className = "ql-token";
class _e extends me {
  static create(e) {
    const s = super.create(e);
    return typeof e == "string" && s.setAttribute("data-language", e), s;
  }
  static formats(e) {
    return e.getAttribute("data-language") || "plain";
  }
  static register() {
  }
  // Syntax module will register
  format(e, s) {
    e === this.statics.blotName && s ? this.domNode.setAttribute("data-language", s) : super.format(e, s);
  }
  replaceWith(e, s) {
    return this.formatAt(0, this.length(), lt.blotName, !1), super.replaceWith(e, s);
  }
}
class Fs extends Ft {
  attach() {
    super.attach(), this.forceNext = !1, this.scroll.emitMount(this);
  }
  format(e, s) {
    e === _e.blotName && (this.forceNext = !0, this.children.forEach((r) => {
      r.format(e, s);
    }));
  }
  formatAt(e, s, r, i) {
    r === _e.blotName && (this.forceNext = !0), super.formatAt(e, s, r, i);
  }
  highlight(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1;
    if (this.children.head == null) return;
    const i = `${Array.from(this.domNode.childNodes).filter((n) => n !== this.uiNode).map((n) => n.textContent).join(`
`)}
`, a = _e.formats(this.children.head.domNode);
    if (s || this.forceNext || this.cachedText !== i) {
      if (i.trim().length > 0 || this.cachedText == null) {
        const n = this.children.reduce((u, p) => u.concat(Yo(p, !1)), new j()), o = e(i, a);
        n.diff(o).reduce((u, p) => {
          let {
            retain: g,
            attributes: k
          } = p;
          return g ? (k && Object.keys(k).forEach((y) => {
            [_e.blotName, lt.blotName].includes(y) && this.formatAt(u, g, y, k[y]);
          }), u + g) : u;
        }, 0);
      }
      this.cachedText = i, this.forceNext = !1;
    }
  }
  html(e, s) {
    const [r] = this.children.find(e);
    return `<pre data-language="${r ? _e.formats(r.domNode) : "plain"}">
${Jn(this.code(e, s))}
</pre>`;
  }
  optimize(e) {
    if (super.optimize(e), this.parent != null && this.children.head != null && this.uiNode != null) {
      const s = _e.formats(this.children.head.domNode);
      s !== this.uiNode.value && (this.uiNode.value = s);
    }
  }
}
Fs.allowedChildren = [_e];
_e.requiredContainer = Fs;
_e.allowedChildren = [lt, us, je, He];
const Gw = (t, e, s) => {
  if (typeof t.versionString == "string") {
    const r = t.versionString.split(".")[0];
    if (parseInt(r, 10) >= 11)
      return t.highlight(s, {
        language: e
      }).value;
  }
  return t.highlight(e, s).value;
};
class gl extends ze {
  static register() {
    N.register(lt, !0), N.register(_e, !0), N.register(Fs, !0);
  }
  constructor(e, s) {
    if (super(e, s), this.options.hljs == null)
      throw new Error("Syntax module requires highlight.js. Please include the library on the page before Quill.");
    this.languages = this.options.languages.reduce((r, i) => {
      let {
        key: a
      } = i;
      return r[a] = !0, r;
    }, {}), this.highlightBlot = this.highlightBlot.bind(this), this.initListener(), this.initTimer();
  }
  initListener() {
    this.quill.on(N.events.SCROLL_BLOT_MOUNT, (e) => {
      if (!(e instanceof Fs)) return;
      const s = this.quill.root.ownerDocument.createElement("select");
      this.options.languages.forEach((r) => {
        let {
          key: i,
          label: a
        } = r;
        const n = s.ownerDocument.createElement("option");
        n.textContent = a, n.setAttribute("value", i), s.appendChild(n);
      }), s.addEventListener("change", () => {
        e.format(_e.blotName, s.value), this.quill.root.focus(), this.highlight(e, !0);
      }), e.uiNode == null && (e.attachUI(s), e.children.head && (s.value = _e.formats(e.children.head.domNode)));
    });
  }
  initTimer() {
    let e = null;
    this.quill.on(N.events.SCROLL_OPTIMIZE, () => {
      e && clearTimeout(e), e = setTimeout(() => {
        this.highlight(), e = null;
      }, this.options.interval);
    });
  }
  highlight() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : null, s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1;
    if (this.quill.selection.composing) return;
    this.quill.update(N.sources.USER);
    const r = this.quill.getSelection();
    (e == null ? this.quill.scroll.descendants(Fs) : [e]).forEach((a) => {
      a.highlight(this.highlightBlot, s);
    }), this.quill.update(N.sources.SILENT), r != null && this.quill.setSelection(r, N.sources.SILENT);
  }
  highlightBlot(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "plain";
    if (s = this.languages[s] ? s : "plain", s === "plain")
      return Jn(e).split(`
`).reduce((i, a, n) => (n !== 0 && i.insert(`
`, {
        [me.blotName]: s
      }), i.insert(a)), new j());
    const r = this.quill.root.ownerDocument.createElement("div");
    return r.classList.add(me.className), r.innerHTML = Gw(this.options.hljs, s, e), na(this.quill.scroll, r, [(i, a) => {
      const n = Bs.value(i);
      return n ? a.compose(new j().retain(a.length(), {
        [lt.blotName]: n
      })) : a;
    }], [(i, a) => i.data.split(`
`).reduce((n, o, u) => (u !== 0 && n.insert(`
`, {
      [me.blotName]: s
    }), n.insert(o)), a)], /* @__PURE__ */ new WeakMap());
  }
}
gl.DEFAULTS = {
  hljs: window.hljs,
  interval: 1e3,
  languages: [{
    key: "plain",
    label: "Plain"
  }, {
    key: "bash",
    label: "Bash"
  }, {
    key: "cpp",
    label: "C++"
  }, {
    key: "cs",
    label: "C#"
  }, {
    key: "css",
    label: "CSS"
  }, {
    key: "diff",
    label: "Diff"
  }, {
    key: "xml",
    label: "HTML/XML"
  }, {
    key: "java",
    label: "Java"
  }, {
    key: "javascript",
    label: "JavaScript"
  }, {
    key: "markdown",
    label: "Markdown"
  }, {
    key: "php",
    label: "PHP"
  }, {
    key: "python",
    label: "Python"
  }, {
    key: "ruby",
    label: "Ruby"
  }, {
    key: "sql",
    label: "SQL"
  }]
};
const js = class js extends ce {
  static create(e) {
    const s = super.create();
    return e ? s.setAttribute("data-row", e) : s.setAttribute("data-row", ra()), s;
  }
  static formats(e) {
    if (e.hasAttribute("data-row"))
      return e.getAttribute("data-row");
  }
  cellOffset() {
    return this.parent ? this.parent.children.indexOf(this) : -1;
  }
  format(e, s) {
    e === js.blotName && s ? this.domNode.setAttribute("data-row", s) : super.format(e, s);
  }
  row() {
    return this.parent;
  }
  rowOffset() {
    return this.row() ? this.row().rowOffset() : -1;
  }
  table() {
    return this.row() && this.row().table();
  }
};
B(js, "blotName", "table"), B(js, "tagName", "TD");
let Me = js;
class ut extends Mt {
  checkMerge() {
    if (super.checkMerge() && this.next.children.head != null) {
      const e = this.children.head.formats(), s = this.children.tail.formats(), r = this.next.children.head.formats(), i = this.next.children.tail.formats();
      return e.table === s.table && e.table === r.table && e.table === i.table;
    }
    return !1;
  }
  optimize(e) {
    super.optimize(e), this.children.forEach((s) => {
      if (s.next == null) return;
      const r = s.formats(), i = s.next.formats();
      if (r.table !== i.table) {
        const a = this.splitAfter(s);
        a && a.optimize(), this.prev && this.prev.optimize();
      }
    });
  }
  rowOffset() {
    return this.parent ? this.parent.children.indexOf(this) : -1;
  }
  table() {
    return this.parent && this.parent.parent;
  }
}
B(ut, "blotName", "table-row"), B(ut, "tagName", "TR");
class Qe extends Mt {
}
B(Qe, "blotName", "table-body"), B(Qe, "tagName", "TBODY");
class cs extends Mt {
  balanceCells() {
    const e = this.descendants(ut), s = e.reduce((r, i) => Math.max(i.children.length, r), 0);
    e.forEach((r) => {
      new Array(s - r.children.length).fill(0).forEach(() => {
        let i;
        r.children.head != null && (i = Me.formats(r.children.head.domNode));
        const a = this.scroll.create(Me.blotName, i);
        r.appendChild(a), a.optimize();
      });
    });
  }
  cells(e) {
    return this.rows().map((s) => s.children.at(e));
  }
  deleteColumn(e) {
    const [s] = this.descendant(Qe);
    s == null || s.children.head == null || s.children.forEach((r) => {
      const i = r.children.at(e);
      i != null && i.remove();
    });
  }
  insertColumn(e) {
    const [s] = this.descendant(Qe);
    s == null || s.children.head == null || s.children.forEach((r) => {
      const i = r.children.at(e), a = Me.formats(r.children.head.domNode), n = this.scroll.create(Me.blotName, a);
      r.insertBefore(n, i);
    });
  }
  insertRow(e) {
    const [s] = this.descendant(Qe);
    if (s == null || s.children.head == null) return;
    const r = ra(), i = this.scroll.create(ut.blotName);
    s.children.head.children.forEach(() => {
      const n = this.scroll.create(Me.blotName, r);
      i.appendChild(n);
    });
    const a = s.children.at(e);
    s.insertBefore(i, a);
  }
  rows() {
    const e = this.children.head;
    return e == null ? [] : e.children.map((s) => s);
  }
}
B(cs, "blotName", "table-container"), B(cs, "tagName", "TABLE");
cs.allowedChildren = [Qe];
Qe.requiredContainer = cs;
Qe.allowedChildren = [ut];
ut.requiredContainer = Qe;
ut.allowedChildren = [Me];
Me.requiredContainer = ut;
function ra() {
  return `row-${Math.random().toString(36).slice(2, 6)}`;
}
class Kw extends ze {
  static register() {
    N.register(Me), N.register(ut), N.register(Qe), N.register(cs);
  }
  constructor() {
    super(...arguments), this.listenBalanceCells();
  }
  balanceTables() {
    this.quill.scroll.descendants(cs).forEach((e) => {
      e.balanceCells();
    });
  }
  deleteColumn() {
    const [e, , s] = this.getTable();
    s != null && (e.deleteColumn(s.cellOffset()), this.quill.update(N.sources.USER));
  }
  deleteRow() {
    const [, e] = this.getTable();
    e != null && (e.remove(), this.quill.update(N.sources.USER));
  }
  deleteTable() {
    const [e] = this.getTable();
    if (e == null) return;
    const s = e.offset();
    e.remove(), this.quill.update(N.sources.USER), this.quill.setSelection(s, N.sources.SILENT);
  }
  getTable() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : this.quill.getSelection();
    if (e == null) return [null, null, null, -1];
    const [s, r] = this.quill.getLine(e.index);
    if (s == null || s.statics.blotName !== Me.blotName)
      return [null, null, null, -1];
    const i = s.parent;
    return [i.parent.parent, i, s, r];
  }
  insertColumn(e) {
    const s = this.quill.getSelection();
    if (!s) return;
    const [r, i, a] = this.getTable(s);
    if (a == null) return;
    const n = a.cellOffset();
    r.insertColumn(n + e), this.quill.update(N.sources.USER);
    let o = i.rowOffset();
    e === 0 && (o += 1), this.quill.setSelection(s.index + o, s.length, N.sources.SILENT);
  }
  insertColumnLeft() {
    this.insertColumn(0);
  }
  insertColumnRight() {
    this.insertColumn(1);
  }
  insertRow(e) {
    const s = this.quill.getSelection();
    if (!s) return;
    const [r, i, a] = this.getTable(s);
    if (a == null) return;
    const n = i.rowOffset();
    r.insertRow(n + e), this.quill.update(N.sources.USER), e > 0 ? this.quill.setSelection(s, N.sources.SILENT) : this.quill.setSelection(s.index + i.children.length, s.length, N.sources.SILENT);
  }
  insertRowAbove() {
    this.insertRow(0);
  }
  insertRowBelow() {
    this.insertRow(1);
  }
  insertTable(e, s) {
    const r = this.quill.getSelection();
    if (r == null) return;
    const i = new Array(e).fill(0).reduce((a) => {
      const n = new Array(s).fill(`
`).join("");
      return a.insert(n, {
        table: ra()
      });
    }, new j().retain(r.index));
    this.quill.updateContents(i, N.sources.USER), this.quill.setSelection(r.index, N.sources.SILENT), this.balanceTables();
  }
  listenBalanceCells() {
    this.quill.on(N.events.SCROLL_OPTIMIZE, (e) => {
      e.some((s) => ["TD", "TR", "TBODY", "TABLE"].includes(s.target.tagName) ? (this.quill.once(N.events.TEXT_CHANGE, (r, i, a) => {
        a === N.sources.USER && this.balanceTables();
      }), !0) : !1);
    });
  }
}
const no = ct("quill:toolbar");
class ia extends ze {
  constructor(e, s) {
    var r, i;
    if (super(e, s), Array.isArray(this.options.container)) {
      const a = document.createElement("div");
      a.setAttribute("role", "toolbar"), Ww(a, this.options.container), (i = (r = e.container) == null ? void 0 : r.parentNode) == null || i.insertBefore(a, e.container), this.container = a;
    } else typeof this.options.container == "string" ? this.container = document.querySelector(this.options.container) : this.container = this.options.container;
    if (!(this.container instanceof HTMLElement)) {
      no.error("Container required for toolbar", this.options);
      return;
    }
    this.container.classList.add("ql-toolbar"), this.controls = [], this.handlers = {}, this.options.handlers && Object.keys(this.options.handlers).forEach((a) => {
      var o;
      const n = (o = this.options.handlers) == null ? void 0 : o[a];
      n && this.addHandler(a, n);
    }), Array.from(this.container.querySelectorAll("button, select")).forEach((a) => {
      this.attach(a);
    }), this.quill.on(N.events.EDITOR_CHANGE, () => {
      const [a] = this.quill.selection.getRange();
      this.update(a);
    });
  }
  addHandler(e, s) {
    this.handlers[e] = s;
  }
  attach(e) {
    let s = Array.from(e.classList).find((i) => i.indexOf("ql-") === 0);
    if (!s) return;
    if (s = s.slice(3), e.tagName === "BUTTON" && e.setAttribute("type", "button"), this.handlers[s] == null && this.quill.scroll.query(s) == null) {
      no.warn("ignoring attaching to nonexistent format", s, e);
      return;
    }
    const r = e.tagName === "SELECT" ? "change" : "click";
    e.addEventListener(r, (i) => {
      let a;
      if (e.tagName === "SELECT") {
        if (e.selectedIndex < 0) return;
        const o = e.options[e.selectedIndex];
        o.hasAttribute("selected") ? a = !1 : a = o.value || !1;
      } else
        e.classList.contains("ql-active") ? a = !1 : a = e.value || !e.hasAttribute("value"), i.preventDefault();
      this.quill.focus();
      const [n] = this.quill.selection.getRange();
      if (this.handlers[s] != null)
        this.handlers[s].call(this, a);
      else if (
        // @ts-expect-error
        this.quill.scroll.query(s).prototype instanceof Ae
      ) {
        if (a = prompt(`Enter ${s}`), !a) return;
        this.quill.updateContents(new j().retain(n.index).delete(n.length).insert({
          [s]: a
        }), N.sources.USER);
      } else
        this.quill.format(s, a, N.sources.USER);
      this.update(n);
    }), this.controls.push([s, e]);
  }
  update(e) {
    const s = e == null ? {} : this.quill.getFormat(e);
    this.controls.forEach((r) => {
      const [i, a] = r;
      if (a.tagName === "SELECT") {
        let n = null;
        if (e == null)
          n = null;
        else if (s[i] == null)
          n = a.querySelector("option[selected]");
        else if (!Array.isArray(s[i])) {
          let o = s[i];
          typeof o == "string" && (o = o.replace(/"/g, '\\"')), n = a.querySelector(`option[value="${o}"]`);
        }
        n == null ? (a.value = "", a.selectedIndex = -1) : n.selected = !0;
      } else if (e == null)
        a.classList.remove("ql-active"), a.setAttribute("aria-pressed", "false");
      else if (a.hasAttribute("value")) {
        const n = s[i], o = n === a.getAttribute("value") || n != null && n.toString() === a.getAttribute("value") || n == null && !a.getAttribute("value");
        a.classList.toggle("ql-active", o), a.setAttribute("aria-pressed", o.toString());
      } else {
        const n = s[i] != null;
        a.classList.toggle("ql-active", n), a.setAttribute("aria-pressed", n.toString());
      }
    });
  }
}
ia.DEFAULTS = {};
function ro(t, e, s) {
  const r = document.createElement("button");
  r.setAttribute("type", "button"), r.classList.add(`ql-${e}`), r.setAttribute("aria-pressed", "false"), s != null ? (r.value = s, r.setAttribute("aria-label", `${e}: ${s}`)) : r.setAttribute("aria-label", e), t.appendChild(r);
}
function Ww(t, e) {
  Array.isArray(e[0]) || (e = [e]), e.forEach((s) => {
    const r = document.createElement("span");
    r.classList.add("ql-formats"), s.forEach((i) => {
      if (typeof i == "string")
        ro(r, i);
      else {
        const a = Object.keys(i)[0], n = i[a];
        Array.isArray(n) ? Zw(r, a, n) : ro(r, a, n);
      }
    }), t.appendChild(r);
  });
}
function Zw(t, e, s) {
  const r = document.createElement("select");
  r.classList.add(`ql-${e}`), s.forEach((i) => {
    const a = document.createElement("option");
    i !== !1 ? a.setAttribute("value", String(i)) : a.setAttribute("selected", "selected"), r.appendChild(a);
  }), t.appendChild(r);
}
ia.DEFAULTS = {
  container: null,
  handlers: {
    clean() {
      const t = this.quill.getSelection();
      if (t != null)
        if (t.length === 0) {
          const e = this.quill.getFormat();
          Object.keys(e).forEach((s) => {
            this.quill.scroll.query(s, V.INLINE) != null && this.quill.format(s, !1, N.sources.USER);
          });
        } else
          this.quill.removeFormat(t.index, t.length, N.sources.USER);
    },
    direction(t) {
      const {
        align: e
      } = this.quill.getFormat();
      t === "rtl" && e == null ? this.quill.format("align", "right", N.sources.USER) : !t && e === "right" && this.quill.format("align", !1, N.sources.USER), this.quill.format("direction", t, N.sources.USER);
    },
    indent(t) {
      const e = this.quill.getSelection(), s = this.quill.getFormat(e), r = parseInt(s.indent || 0, 10);
      if (t === "+1" || t === "-1") {
        let i = t === "+1" ? 1 : -1;
        s.direction === "rtl" && (i *= -1), this.quill.format("indent", r + i, N.sources.USER);
      }
    },
    link(t) {
      t === !0 && (t = prompt("Enter link URL:")), this.quill.format("link", t, N.sources.USER);
    },
    list(t) {
      const e = this.quill.getSelection(), s = this.quill.getFormat(e);
      t === "check" ? s.list === "checked" || s.list === "unchecked" ? this.quill.format("list", !1, N.sources.USER) : this.quill.format("list", "unchecked", N.sources.USER) : this.quill.format("list", t, N.sources.USER);
    }
  }
};
const Xw = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="3" x2="15" y1="9" y2="9"/><line class="ql-stroke" x1="3" x2="13" y1="14" y2="14"/><line class="ql-stroke" x1="3" x2="9" y1="4" y2="4"/></svg>', Yw = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="15" x2="3" y1="9" y2="9"/><line class="ql-stroke" x1="14" x2="4" y1="14" y2="14"/><line class="ql-stroke" x1="12" x2="6" y1="4" y2="4"/></svg>', Qw = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="15" x2="3" y1="9" y2="9"/><line class="ql-stroke" x1="15" x2="5" y1="14" y2="14"/><line class="ql-stroke" x1="15" x2="9" y1="4" y2="4"/></svg>', Jw = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="15" x2="3" y1="9" y2="9"/><line class="ql-stroke" x1="15" x2="3" y1="14" y2="14"/><line class="ql-stroke" x1="15" x2="3" y1="4" y2="4"/></svg>', xw = '<svg viewbox="0 0 18 18"><g class="ql-fill ql-color-label"><polygon points="6 6.868 6 6 5 6 5 7 5.942 7 6 6.868"/><rect height="1" width="1" x="4" y="4"/><polygon points="6.817 5 6 5 6 6 6.38 6 6.817 5"/><rect height="1" width="1" x="2" y="6"/><rect height="1" width="1" x="3" y="5"/><rect height="1" width="1" x="4" y="7"/><polygon points="4 11.439 4 11 3 11 3 12 3.755 12 4 11.439"/><rect height="1" width="1" x="2" y="12"/><rect height="1" width="1" x="2" y="9"/><rect height="1" width="1" x="2" y="15"/><polygon points="4.63 10 4 10 4 11 4.192 11 4.63 10"/><rect height="1" width="1" x="3" y="8"/><path d="M10.832,4.2L11,4.582V4H10.708A1.948,1.948,0,0,1,10.832,4.2Z"/><path d="M7,4.582L7.168,4.2A1.929,1.929,0,0,1,7.292,4H7V4.582Z"/><path d="M8,13H7.683l-0.351.8a1.933,1.933,0,0,1-.124.2H8V13Z"/><rect height="1" width="1" x="12" y="2"/><rect height="1" width="1" x="11" y="3"/><path d="M9,3H8V3.282A1.985,1.985,0,0,1,9,3Z"/><rect height="1" width="1" x="2" y="3"/><rect height="1" width="1" x="6" y="2"/><rect height="1" width="1" x="3" y="2"/><rect height="1" width="1" x="5" y="3"/><rect height="1" width="1" x="9" y="2"/><rect height="1" width="1" x="15" y="14"/><polygon points="13.447 10.174 13.469 10.225 13.472 10.232 13.808 11 14 11 14 10 13.37 10 13.447 10.174"/><rect height="1" width="1" x="13" y="7"/><rect height="1" width="1" x="15" y="5"/><rect height="1" width="1" x="14" y="6"/><rect height="1" width="1" x="15" y="8"/><rect height="1" width="1" x="14" y="9"/><path d="M3.775,14H3v1H4V14.314A1.97,1.97,0,0,1,3.775,14Z"/><rect height="1" width="1" x="14" y="3"/><polygon points="12 6.868 12 6 11.62 6 12 6.868"/><rect height="1" width="1" x="15" y="2"/><rect height="1" width="1" x="12" y="5"/><rect height="1" width="1" x="13" y="4"/><polygon points="12.933 9 13 9 13 8 12.495 8 12.933 9"/><rect height="1" width="1" x="9" y="14"/><rect height="1" width="1" x="8" y="15"/><path d="M6,14.926V15H7V14.316A1.993,1.993,0,0,1,6,14.926Z"/><rect height="1" width="1" x="5" y="15"/><path d="M10.668,13.8L10.317,13H10v1h0.792A1.947,1.947,0,0,1,10.668,13.8Z"/><rect height="1" width="1" x="11" y="15"/><path d="M14.332,12.2a1.99,1.99,0,0,1,.166.8H15V12H14.245Z"/><rect height="1" width="1" x="14" y="15"/><rect height="1" width="1" x="15" y="11"/></g><polyline class="ql-stroke" points="5.5 13 9 5 12.5 13"/><line class="ql-stroke" x1="11.63" x2="6.38" y1="11" y2="11"/></svg>', eC = '<svg viewbox="0 0 18 18"><rect class="ql-fill ql-stroke" height="3" width="3" x="4" y="5"/><rect class="ql-fill ql-stroke" height="3" width="3" x="11" y="5"/><path class="ql-even ql-fill ql-stroke" d="M7,8c0,4.031-3,5-3,5"/><path class="ql-even ql-fill ql-stroke" d="M14,8c0,4.031-3,5-3,5"/></svg>', tC = '<svg viewbox="0 0 18 18"><path class="ql-stroke" d="M5,4H9.5A2.5,2.5,0,0,1,12,6.5v0A2.5,2.5,0,0,1,9.5,9H5A0,0,0,0,1,5,9V4A0,0,0,0,1,5,4Z"/><path class="ql-stroke" d="M5,9h5.5A2.5,2.5,0,0,1,13,11.5v0A2.5,2.5,0,0,1,10.5,14H5a0,0,0,0,1,0,0V9A0,0,0,0,1,5,9Z"/></svg>', sC = '<svg class="" viewbox="0 0 18 18"><line class="ql-stroke" x1="5" x2="13" y1="3" y2="3"/><line class="ql-stroke" x1="6" x2="9.35" y1="12" y2="3"/><line class="ql-stroke" x1="11" x2="15" y1="11" y2="15"/><line class="ql-stroke" x1="15" x2="11" y1="11" y2="15"/><rect class="ql-fill" height="1" rx="0.5" ry="0.5" width="7" x="2" y="14"/></svg>', io = '<svg viewbox="0 0 18 18"><polyline class="ql-even ql-stroke" points="5 7 3 9 5 11"/><polyline class="ql-even ql-stroke" points="13 7 15 9 13 11"/><line class="ql-stroke" x1="10" x2="8" y1="5" y2="13"/></svg>', nC = '<svg viewbox="0 0 18 18"><line class="ql-color-label ql-stroke ql-transparent" x1="3" x2="15" y1="15" y2="15"/><polyline class="ql-stroke" points="5.5 11 9 3 12.5 11"/><line class="ql-stroke" x1="11.63" x2="6.38" y1="9" y2="9"/></svg>', rC = '<svg viewbox="0 0 18 18"><polygon class="ql-stroke ql-fill" points="3 11 5 9 3 7 3 11"/><line class="ql-stroke ql-fill" x1="15" x2="11" y1="4" y2="4"/><path class="ql-fill" d="M11,3a3,3,0,0,0,0,6h1V3H11Z"/><rect class="ql-fill" height="11" width="1" x="11" y="4"/><rect class="ql-fill" height="11" width="1" x="13" y="4"/></svg>', iC = '<svg viewbox="0 0 18 18"><polygon class="ql-stroke ql-fill" points="15 12 13 10 15 8 15 12"/><line class="ql-stroke ql-fill" x1="9" x2="5" y1="4" y2="4"/><path class="ql-fill" d="M5,3A3,3,0,0,0,5,9H6V3H5Z"/><rect class="ql-fill" height="11" width="1" x="5" y="4"/><rect class="ql-fill" height="11" width="1" x="7" y="4"/></svg>', aC = '<svg viewbox="0 0 18 18"><path class="ql-fill" d="M11.759,2.482a2.561,2.561,0,0,0-3.53.607A7.656,7.656,0,0,0,6.8,6.2C6.109,9.188,5.275,14.677,4.15,14.927a1.545,1.545,0,0,0-1.3-.933A0.922,0.922,0,0,0,2,15.036S1.954,16,4.119,16s3.091-2.691,3.7-5.553c0.177-.826.36-1.726,0.554-2.6L8.775,6.2c0.381-1.421.807-2.521,1.306-2.676a1.014,1.014,0,0,0,1.02.56A0.966,0.966,0,0,0,11.759,2.482Z"/><rect class="ql-fill" height="1.6" rx="0.8" ry="0.8" width="5" x="5.15" y="6.2"/><path class="ql-fill" d="M13.663,12.027a1.662,1.662,0,0,1,.266-0.276q0.193,0.069.456,0.138a2.1,2.1,0,0,0,.535.069,1.075,1.075,0,0,0,.767-0.3,1.044,1.044,0,0,0,.314-0.8,0.84,0.84,0,0,0-.238-0.619,0.8,0.8,0,0,0-.594-0.239,1.154,1.154,0,0,0-.781.3,4.607,4.607,0,0,0-.781,1q-0.091.15-.218,0.346l-0.246.38c-0.068-.288-0.137-0.582-0.212-0.885-0.459-1.847-2.494-.984-2.941-0.8-0.482.2-.353,0.647-0.094,0.529a0.869,0.869,0,0,1,1.281.585c0.217,0.751.377,1.436,0.527,2.038a5.688,5.688,0,0,1-.362.467,2.69,2.69,0,0,1-.264.271q-0.221-.08-0.471-0.147a2.029,2.029,0,0,0-.522-0.066,1.079,1.079,0,0,0-.768.3A1.058,1.058,0,0,0,9,15.131a0.82,0.82,0,0,0,.832.852,1.134,1.134,0,0,0,.787-0.3,5.11,5.11,0,0,0,.776-0.993q0.141-.219.215-0.34c0.046-.076.122-0.194,0.223-0.346a2.786,2.786,0,0,0,.918,1.726,2.582,2.582,0,0,0,2.376-.185c0.317-.181.212-0.565,0-0.494A0.807,0.807,0,0,1,14.176,15a5.159,5.159,0,0,1-.913-2.446l0,0Q13.487,12.24,13.663,12.027Z"/></svg>', oC = '<svg viewBox="0 0 18 18"><path class="ql-fill" d="M10,4V14a1,1,0,0,1-2,0V10H3v4a1,1,0,0,1-2,0V4A1,1,0,0,1,3,4V8H8V4a1,1,0,0,1,2,0Zm6.06787,9.209H14.98975V7.59863a.54085.54085,0,0,0-.605-.60547h-.62744a1.01119,1.01119,0,0,0-.748.29688L11.645,8.56641a.5435.5435,0,0,0-.022.8584l.28613.30762a.53861.53861,0,0,0,.84717.0332l.09912-.08789a1.2137,1.2137,0,0,0,.2417-.35254h.02246s-.01123.30859-.01123.60547V13.209H12.041a.54085.54085,0,0,0-.605.60547v.43945a.54085.54085,0,0,0,.605.60547h4.02686a.54085.54085,0,0,0,.605-.60547v-.43945A.54085.54085,0,0,0,16.06787,13.209Z"/></svg>', lC = '<svg viewBox="0 0 18 18"><path class="ql-fill" d="M16.73975,13.81445v.43945a.54085.54085,0,0,1-.605.60547H11.855a.58392.58392,0,0,1-.64893-.60547V14.0127c0-2.90527,3.39941-3.42187,3.39941-4.55469a.77675.77675,0,0,0-.84717-.78125,1.17684,1.17684,0,0,0-.83594.38477c-.2749.26367-.561.374-.85791.13184l-.4292-.34082c-.30811-.24219-.38525-.51758-.1543-.81445a2.97155,2.97155,0,0,1,2.45361-1.17676,2.45393,2.45393,0,0,1,2.68408,2.40918c0,2.45312-3.1792,2.92676-3.27832,3.93848h2.79443A.54085.54085,0,0,1,16.73975,13.81445ZM9,3A.99974.99974,0,0,0,8,4V8H3V4A1,1,0,0,0,1,4V14a1,1,0,0,0,2,0V10H8v4a1,1,0,0,0,2,0V4A.99974.99974,0,0,0,9,3Z"/></svg>', uC = '<svg viewBox="0 0 18 18"><path class="ql-fill" d="M16.65186,12.30664a2.6742,2.6742,0,0,1-2.915,2.68457,3.96592,3.96592,0,0,1-2.25537-.6709.56007.56007,0,0,1-.13232-.83594L11.64648,13c.209-.34082.48389-.36328.82471-.1543a2.32654,2.32654,0,0,0,1.12256.33008c.71484,0,1.12207-.35156,1.12207-.78125,0-.61523-.61621-.86816-1.46338-.86816H13.2085a.65159.65159,0,0,1-.68213-.41895l-.05518-.10937a.67114.67114,0,0,1,.14307-.78125l.71533-.86914a8.55289,8.55289,0,0,1,.68213-.7373V8.58887a3.93913,3.93913,0,0,1-.748.05469H11.9873a.54085.54085,0,0,1-.605-.60547V7.59863a.54085.54085,0,0,1,.605-.60547h3.75146a.53773.53773,0,0,1,.60547.59375v.17676a1.03723,1.03723,0,0,1-.27539.748L14.74854,10.0293A2.31132,2.31132,0,0,1,16.65186,12.30664ZM9,3A.99974.99974,0,0,0,8,4V8H3V4A1,1,0,0,0,1,4V14a1,1,0,0,0,2,0V10H8v4a1,1,0,0,0,2,0V4A.99974.99974,0,0,0,9,3Z"/></svg>', dC = '<svg viewBox="0 0 18 18"><path class="ql-fill" d="M10,4V14a1,1,0,0,1-2,0V10H3v4a1,1,0,0,1-2,0V4A1,1,0,0,1,3,4V8H8V4a1,1,0,0,1,2,0Zm7.05371,7.96582v.38477c0,.39648-.165.60547-.46191.60547h-.47314v1.29785a.54085.54085,0,0,1-.605.60547h-.69336a.54085.54085,0,0,1-.605-.60547V12.95605H11.333a.5412.5412,0,0,1-.60547-.60547v-.15332a1.199,1.199,0,0,1,.22021-.748l2.56348-4.05957a.7819.7819,0,0,1,.72607-.39648h1.27637a.54085.54085,0,0,1,.605.60547v3.7627h.33008A.54055.54055,0,0,1,17.05371,11.96582ZM14.28125,8.7207h-.022a4.18969,4.18969,0,0,1-.38525.81348l-1.188,1.80469v.02246h1.5293V9.60059A7.04058,7.04058,0,0,1,14.28125,8.7207Z"/></svg>', cC = '<svg viewBox="0 0 18 18"><path class="ql-fill" d="M16.74023,12.18555a2.75131,2.75131,0,0,1-2.91553,2.80566,3.908,3.908,0,0,1-2.25537-.68164.54809.54809,0,0,1-.13184-.8252L11.73438,13c.209-.34082.48389-.36328.8252-.1543a2.23757,2.23757,0,0,0,1.1001.33008,1.01827,1.01827,0,0,0,1.1001-.96777c0-.61621-.53906-.97949-1.25439-.97949a2.15554,2.15554,0,0,0-.64893.09961,1.15209,1.15209,0,0,1-.814.01074l-.12109-.04395a.64116.64116,0,0,1-.45117-.71484l.231-3.00391a.56666.56666,0,0,1,.62744-.583H15.541a.54085.54085,0,0,1,.605.60547v.43945a.54085.54085,0,0,1-.605.60547H13.41748l-.04395.72559a1.29306,1.29306,0,0,1-.04395.30859h.022a2.39776,2.39776,0,0,1,.57227-.07715A2.53266,2.53266,0,0,1,16.74023,12.18555ZM9,3A.99974.99974,0,0,0,8,4V8H3V4A1,1,0,0,0,1,4V14a1,1,0,0,0,2,0V10H8v4a1,1,0,0,0,2,0V4A.99974.99974,0,0,0,9,3Z"/></svg>', fC = '<svg viewBox="0 0 18 18"><path class="ql-fill" d="M14.51758,9.64453a1.85627,1.85627,0,0,0-1.24316.38477H13.252a1.73532,1.73532,0,0,1,1.72754-1.4082,2.66491,2.66491,0,0,1,.5498.06641c.35254.05469.57227.01074.70508-.40723l.16406-.5166a.53393.53393,0,0,0-.373-.75977,4.83723,4.83723,0,0,0-1.17773-.14258c-2.43164,0-3.7627,2.17773-3.7627,4.43359,0,2.47559,1.60645,3.69629,3.19043,3.69629A2.70585,2.70585,0,0,0,16.96,12.19727,2.43861,2.43861,0,0,0,14.51758,9.64453Zm-.23047,3.58691c-.67187,0-1.22168-.81445-1.22168-1.45215,0-.47363.30762-.583.72559-.583.96875,0,1.27734.59375,1.27734,1.12207A.82182.82182,0,0,1,14.28711,13.23145ZM10,4V14a1,1,0,0,1-2,0V10H3v4a1,1,0,0,1-2,0V4A1,1,0,0,1,3,4V8H8V4a1,1,0,0,1,2,0Z"/></svg>', pC = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="7" x2="13" y1="4" y2="4"/><line class="ql-stroke" x1="5" x2="11" y1="14" y2="14"/><line class="ql-stroke" x1="8" x2="10" y1="14" y2="4"/></svg>', hC = '<svg viewbox="0 0 18 18"><rect class="ql-stroke" height="10" width="12" x="3" y="4"/><circle class="ql-fill" cx="6" cy="7" r="1"/><polyline class="ql-even ql-fill" points="5 12 5 11 7 9 8 10 11 7 13 9 13 12 5 12"/></svg>', gC = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="3" x2="15" y1="14" y2="14"/><line class="ql-stroke" x1="3" x2="15" y1="4" y2="4"/><line class="ql-stroke" x1="9" x2="15" y1="9" y2="9"/><polyline class="ql-fill ql-stroke" points="3 7 3 11 5 9 3 7"/></svg>', mC = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="3" x2="15" y1="14" y2="14"/><line class="ql-stroke" x1="3" x2="15" y1="4" y2="4"/><line class="ql-stroke" x1="9" x2="15" y1="9" y2="9"/><polyline class="ql-stroke" points="5 7 5 11 3 9 5 7"/></svg>', vC = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="7" x2="11" y1="7" y2="11"/><path class="ql-even ql-stroke" d="M8.9,4.577a3.476,3.476,0,0,1,.36,4.679A3.476,3.476,0,0,1,4.577,8.9C3.185,7.5,2.035,6.4,4.217,4.217S7.5,3.185,8.9,4.577Z"/><path class="ql-even ql-stroke" d="M13.423,9.1a3.476,3.476,0,0,0-4.679-.36,3.476,3.476,0,0,0,.36,4.679c1.392,1.392,2.5,2.542,4.679.36S14.815,10.5,13.423,9.1Z"/></svg>', bC = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="6" x2="15" y1="4" y2="4"/><line class="ql-stroke" x1="6" x2="15" y1="9" y2="9"/><line class="ql-stroke" x1="6" x2="15" y1="14" y2="14"/><line class="ql-stroke" x1="3" x2="3" y1="4" y2="4"/><line class="ql-stroke" x1="3" x2="3" y1="9" y2="9"/><line class="ql-stroke" x1="3" x2="3" y1="14" y2="14"/></svg>', yC = '<svg class="" viewbox="0 0 18 18"><line class="ql-stroke" x1="9" x2="15" y1="4" y2="4"/><polyline class="ql-stroke" points="3 4 4 5 6 3"/><line class="ql-stroke" x1="9" x2="15" y1="14" y2="14"/><polyline class="ql-stroke" points="3 14 4 15 6 13"/><line class="ql-stroke" x1="9" x2="15" y1="9" y2="9"/><polyline class="ql-stroke" points="3 9 4 10 6 8"/></svg>', $C = '<svg viewbox="0 0 18 18"><line class="ql-stroke" x1="7" x2="15" y1="4" y2="4"/><line class="ql-stroke" x1="7" x2="15" y1="9" y2="9"/><line class="ql-stroke" x1="7" x2="15" y1="14" y2="14"/><line class="ql-stroke ql-thin" x1="2.5" x2="4.5" y1="5.5" y2="5.5"/><path class="ql-fill" d="M3.5,6A0.5,0.5,0,0,1,3,5.5V3.085l-0.276.138A0.5,0.5,0,0,1,2.053,3c-0.124-.247-0.023-0.324.224-0.447l1-.5A0.5,0.5,0,0,1,4,2.5v3A0.5,0.5,0,0,1,3.5,6Z"/><path class="ql-stroke ql-thin" d="M4.5,10.5h-2c0-.234,1.85-1.076,1.85-2.234A0.959,0.959,0,0,0,2.5,8.156"/><path class="ql-stroke ql-thin" d="M2.5,14.846a0.959,0.959,0,0,0,1.85-.109A0.7,0.7,0,0,0,3.75,14a0.688,0.688,0,0,0,.6-0.736,0.959,0.959,0,0,0-1.85-.109"/></svg>', kC = '<svg viewbox="0 0 18 18"><path class="ql-fill" d="M15.5,15H13.861a3.858,3.858,0,0,0,1.914-2.975,1.8,1.8,0,0,0-1.6-1.751A1.921,1.921,0,0,0,12.021,11.7a0.50013,0.50013,0,1,0,.957.291h0a0.914,0.914,0,0,1,1.053-.725,0.81,0.81,0,0,1,.744.762c0,1.076-1.16971,1.86982-1.93971,2.43082A1.45639,1.45639,0,0,0,12,15.5a0.5,0.5,0,0,0,.5.5h3A0.5,0.5,0,0,0,15.5,15Z"/><path class="ql-fill" d="M9.65,5.241a1,1,0,0,0-1.409.108L6,7.964,3.759,5.349A1,1,0,0,0,2.192,6.59178Q2.21541,6.6213,2.241,6.649L4.684,9.5,2.241,12.35A1,1,0,0,0,3.71,13.70722q0.02557-.02768.049-0.05722L6,11.036,8.241,13.65a1,1,0,1,0,1.567-1.24277Q9.78459,12.3777,9.759,12.35L7.316,9.5,9.759,6.651A1,1,0,0,0,9.65,5.241Z"/></svg>', wC = '<svg viewbox="0 0 18 18"><path class="ql-fill" d="M15.5,7H13.861a4.015,4.015,0,0,0,1.914-2.975,1.8,1.8,0,0,0-1.6-1.751A1.922,1.922,0,0,0,12.021,3.7a0.5,0.5,0,1,0,.957.291,0.917,0.917,0,0,1,1.053-.725,0.81,0.81,0,0,1,.744.762c0,1.077-1.164,1.925-1.934,2.486A1.423,1.423,0,0,0,12,7.5a0.5,0.5,0,0,0,.5.5h3A0.5,0.5,0,0,0,15.5,7Z"/><path class="ql-fill" d="M9.651,5.241a1,1,0,0,0-1.41.108L6,7.964,3.759,5.349a1,1,0,1,0-1.519,1.3L4.683,9.5,2.241,12.35a1,1,0,1,0,1.519,1.3L6,11.036,8.241,13.65a1,1,0,0,0,1.519-1.3L7.317,9.5,9.759,6.651A1,1,0,0,0,9.651,5.241Z"/></svg>', CC = '<svg viewbox="0 0 18 18"><line class="ql-stroke ql-thin" x1="15.5" x2="2.5" y1="8.5" y2="9.5"/><path class="ql-fill" d="M9.007,8C6.542,7.791,6,7.519,6,6.5,6,5.792,7.283,5,9,5c1.571,0,2.765.679,2.969,1.309a1,1,0,0,0,1.9-.617C13.356,4.106,11.354,3,9,3,6.2,3,4,4.538,4,6.5a3.2,3.2,0,0,0,.5,1.843Z"/><path class="ql-fill" d="M8.984,10C11.457,10.208,12,10.479,12,11.5c0,0.708-1.283,1.5-3,1.5-1.571,0-2.765-.679-2.969-1.309a1,1,0,1,0-1.9.617C4.644,13.894,6.646,15,9,15c2.8,0,5-1.538,5-3.5a3.2,3.2,0,0,0-.5-1.843Z"/></svg>', AC = '<svg viewbox="0 0 18 18"><rect class="ql-stroke" height="12" width="12" x="3" y="3"/><rect class="ql-fill" height="2" width="3" x="5" y="5"/><rect class="ql-fill" height="2" width="4" x="9" y="5"/><g class="ql-fill ql-transparent"><rect height="2" width="3" x="5" y="8"/><rect height="2" width="4" x="9" y="8"/><rect height="2" width="3" x="5" y="11"/><rect height="2" width="4" x="9" y="11"/></g></svg>', EC = '<svg viewbox="0 0 18 18"><path class="ql-stroke" d="M5,3V9a4.012,4.012,0,0,0,4,4H9a4.012,4.012,0,0,0,4-4V3"/><rect class="ql-fill" height="1" rx="0.5" ry="0.5" width="12" x="3" y="15"/></svg>', SC = '<svg viewbox="0 0 18 18"><rect class="ql-stroke" height="12" width="12" x="3" y="3"/><rect class="ql-fill" height="12" width="1" x="5" y="3"/><rect class="ql-fill" height="12" width="1" x="12" y="3"/><rect class="ql-fill" height="2" width="8" x="5" y="8"/><rect class="ql-fill" height="1" width="3" x="3" y="5"/><rect class="ql-fill" height="1" width="3" x="3" y="7"/><rect class="ql-fill" height="1" width="3" x="3" y="10"/><rect class="ql-fill" height="1" width="3" x="3" y="12"/><rect class="ql-fill" height="1" width="3" x="12" y="5"/><rect class="ql-fill" height="1" width="3" x="12" y="7"/><rect class="ql-fill" height="1" width="3" x="12" y="10"/><rect class="ql-fill" height="1" width="3" x="12" y="12"/></svg>', Xs = {
  align: {
    "": Xw,
    center: Yw,
    right: Qw,
    justify: Jw
  },
  background: xw,
  blockquote: eC,
  bold: tC,
  clean: sC,
  code: io,
  "code-block": io,
  color: nC,
  direction: {
    "": rC,
    rtl: iC
  },
  formula: aC,
  header: {
    1: oC,
    2: lC,
    3: uC,
    4: dC,
    5: cC,
    6: fC
  },
  italic: pC,
  image: hC,
  indent: {
    "+1": gC,
    "-1": mC
  },
  link: vC,
  list: {
    bullet: bC,
    check: yC,
    ordered: $C
  },
  script: {
    sub: kC,
    super: wC
  },
  strike: CC,
  table: AC,
  underline: EC,
  video: SC
}, TC = '<svg viewbox="0 0 18 18"><polygon class="ql-stroke" points="7 11 9 13 11 11 7 11"/><polygon class="ql-stroke" points="7 7 9 5 11 7 7 7"/></svg>';
let ao = 0;
function oo(t, e) {
  t.setAttribute(e, `${t.getAttribute(e) !== "true"}`);
}
class er {
  constructor(e) {
    this.select = e, this.container = document.createElement("span"), this.buildPicker(), this.select.style.display = "none", this.select.parentNode.insertBefore(this.container, this.select), this.label.addEventListener("mousedown", () => {
      this.togglePicker();
    }), this.label.addEventListener("keydown", (s) => {
      switch (s.key) {
        case "Enter":
          this.togglePicker();
          break;
        case "Escape":
          this.escape(), s.preventDefault();
          break;
      }
    }), this.select.addEventListener("change", this.update.bind(this));
  }
  togglePicker() {
    this.container.classList.toggle("ql-expanded"), oo(this.label, "aria-expanded"), oo(this.options, "aria-hidden");
  }
  buildItem(e) {
    const s = document.createElement("span");
    s.tabIndex = "0", s.setAttribute("role", "button"), s.classList.add("ql-picker-item");
    const r = e.getAttribute("value");
    return r && s.setAttribute("data-value", r), e.textContent && s.setAttribute("data-label", e.textContent), s.addEventListener("click", () => {
      this.selectItem(s, !0);
    }), s.addEventListener("keydown", (i) => {
      switch (i.key) {
        case "Enter":
          this.selectItem(s, !0), i.preventDefault();
          break;
        case "Escape":
          this.escape(), i.preventDefault();
          break;
      }
    }), s;
  }
  buildLabel() {
    const e = document.createElement("span");
    return e.classList.add("ql-picker-label"), e.innerHTML = TC, e.tabIndex = "0", e.setAttribute("role", "button"), e.setAttribute("aria-expanded", "false"), this.container.appendChild(e), e;
  }
  buildOptions() {
    const e = document.createElement("span");
    e.classList.add("ql-picker-options"), e.setAttribute("aria-hidden", "true"), e.tabIndex = "-1", e.id = `ql-picker-options-${ao}`, ao += 1, this.label.setAttribute("aria-controls", e.id), this.options = e, Array.from(this.select.options).forEach((s) => {
      const r = this.buildItem(s);
      e.appendChild(r), s.selected === !0 && this.selectItem(r);
    }), this.container.appendChild(e);
  }
  buildPicker() {
    Array.from(this.select.attributes).forEach((e) => {
      this.container.setAttribute(e.name, e.value);
    }), this.container.classList.add("ql-picker"), this.label = this.buildLabel(), this.buildOptions();
  }
  escape() {
    this.close(), setTimeout(() => this.label.focus(), 1);
  }
  close() {
    this.container.classList.remove("ql-expanded"), this.label.setAttribute("aria-expanded", "false"), this.options.setAttribute("aria-hidden", "true");
  }
  selectItem(e) {
    let s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1;
    const r = this.container.querySelector(".ql-selected");
    e !== r && (r != null && r.classList.remove("ql-selected"), e != null && (e.classList.add("ql-selected"), this.select.selectedIndex = Array.from(e.parentNode.children).indexOf(e), e.hasAttribute("data-value") ? this.label.setAttribute("data-value", e.getAttribute("data-value")) : this.label.removeAttribute("data-value"), e.hasAttribute("data-label") ? this.label.setAttribute("data-label", e.getAttribute("data-label")) : this.label.removeAttribute("data-label"), s && (this.select.dispatchEvent(new Event("change")), this.close())));
  }
  update() {
    let e;
    if (this.select.selectedIndex > -1) {
      const r = (
        // @ts-expect-error Fix me later
        this.container.querySelector(".ql-picker-options").children[this.select.selectedIndex]
      );
      e = this.select.options[this.select.selectedIndex], this.selectItem(r);
    } else
      this.selectItem(null);
    const s = e != null && e !== this.select.querySelector("option[selected]");
    this.label.classList.toggle("ql-active", s);
  }
}
class ml extends er {
  constructor(e, s) {
    super(e), this.label.innerHTML = s, this.container.classList.add("ql-color-picker"), Array.from(this.container.querySelectorAll(".ql-picker-item")).slice(0, 7).forEach((r) => {
      r.classList.add("ql-primary");
    });
  }
  buildItem(e) {
    const s = super.buildItem(e);
    return s.style.backgroundColor = e.getAttribute("value") || "", s;
  }
  selectItem(e, s) {
    super.selectItem(e, s);
    const r = this.label.querySelector(".ql-color-label"), i = e && e.getAttribute("data-value") || "";
    r && (r.tagName === "line" ? r.style.stroke = i : r.style.fill = i);
  }
}
class vl extends er {
  constructor(e, s) {
    super(e), this.container.classList.add("ql-icon-picker"), Array.from(this.container.querySelectorAll(".ql-picker-item")).forEach((r) => {
      r.innerHTML = s[r.getAttribute("data-value") || ""];
    }), this.defaultItem = this.container.querySelector(".ql-selected"), this.selectItem(this.defaultItem);
  }
  selectItem(e, s) {
    super.selectItem(e, s);
    const r = e || this.defaultItem;
    if (r != null) {
      if (this.label.innerHTML === r.innerHTML) return;
      this.label.innerHTML = r.innerHTML;
    }
  }
}
const _C = (t) => {
  const {
    overflowY: e
  } = getComputedStyle(t, null);
  return e !== "visible" && e !== "clip";
};
class bl {
  constructor(e, s) {
    this.quill = e, this.boundsContainer = s || document.body, this.root = e.addContainer("ql-tooltip"), this.root.innerHTML = this.constructor.TEMPLATE, _C(this.quill.root) && this.quill.root.addEventListener("scroll", () => {
      this.root.style.marginTop = `${-1 * this.quill.root.scrollTop}px`;
    }), this.hide();
  }
  hide() {
    this.root.classList.add("ql-hidden");
  }
  position(e) {
    const s = e.left + e.width / 2 - this.root.offsetWidth / 2, r = e.bottom + this.quill.root.scrollTop;
    this.root.style.left = `${s}px`, this.root.style.top = `${r}px`, this.root.classList.remove("ql-flip");
    const i = this.boundsContainer.getBoundingClientRect(), a = this.root.getBoundingClientRect();
    let n = 0;
    if (a.right > i.right && (n = i.right - a.right, this.root.style.left = `${s + n}px`), a.left < i.left && (n = i.left - a.left, this.root.style.left = `${s + n}px`), a.bottom > i.bottom) {
      const o = a.bottom - a.top, u = e.bottom - e.top + o;
      this.root.style.top = `${r - u}px`, this.root.classList.add("ql-flip");
    }
    return n;
  }
  show() {
    this.root.classList.remove("ql-editing"), this.root.classList.remove("ql-hidden");
  }
}
const NC = [!1, "center", "right", "justify"], IC = ["#000000", "#e60000", "#ff9900", "#ffff00", "#008a00", "#0066cc", "#9933ff", "#ffffff", "#facccc", "#ffebcc", "#ffffcc", "#cce8cc", "#cce0f5", "#ebd6ff", "#bbbbbb", "#f06666", "#ffc266", "#ffff66", "#66b966", "#66a3e0", "#c285ff", "#888888", "#a10000", "#b26b00", "#b2b200", "#006100", "#0047b2", "#6b24b2", "#444444", "#5c0000", "#663d00", "#666600", "#003700", "#002966", "#3d1466"], LC = [!1, "serif", "monospace"], qC = ["1", "2", "3", !1], OC = ["small", !1, "large", "huge"];
class en extends ds {
  constructor(e, s) {
    super(e, s);
    const r = (i) => {
      if (!document.body.contains(e.root)) {
        document.body.removeEventListener("click", r);
        return;
      }
      this.tooltip != null && // @ts-expect-error
      !this.tooltip.root.contains(i.target) && // @ts-expect-error
      document.activeElement !== this.tooltip.textbox && !this.quill.hasFocus() && this.tooltip.hide(), this.pickers != null && this.pickers.forEach((a) => {
        a.container.contains(i.target) || a.close();
      });
    };
    e.emitter.listenDOM("click", document.body, r);
  }
  addModule(e) {
    const s = super.addModule(e);
    return e === "toolbar" && this.extendToolbar(s), s;
  }
  buildButtons(e, s) {
    Array.from(e).forEach((r) => {
      (r.getAttribute("class") || "").split(/\s+/).forEach((a) => {
        if (a.startsWith("ql-") && (a = a.slice(3), s[a] != null))
          if (a === "direction")
            r.innerHTML = s[a][""] + s[a].rtl;
          else if (typeof s[a] == "string")
            r.innerHTML = s[a];
          else {
            const n = r.value || "";
            n != null && s[a][n] && (r.innerHTML = s[a][n]);
          }
      });
    });
  }
  buildPickers(e, s) {
    this.pickers = Array.from(e).map((i) => {
      if (i.classList.contains("ql-align") && (i.querySelector("option") == null && Ps(i, NC), typeof s.align == "object"))
        return new vl(i, s.align);
      if (i.classList.contains("ql-background") || i.classList.contains("ql-color")) {
        const a = i.classList.contains("ql-background") ? "background" : "color";
        return i.querySelector("option") == null && Ps(i, IC, a === "background" ? "#ffffff" : "#000000"), new ml(i, s[a]);
      }
      return i.querySelector("option") == null && (i.classList.contains("ql-font") ? Ps(i, LC) : i.classList.contains("ql-header") ? Ps(i, qC) : i.classList.contains("ql-size") && Ps(i, OC)), new er(i);
    });
    const r = () => {
      this.pickers.forEach((i) => {
        i.update();
      });
    };
    this.quill.on(F.events.EDITOR_CHANGE, r);
  }
}
en.DEFAULTS = yt({}, ds.DEFAULTS, {
  modules: {
    toolbar: {
      handlers: {
        formula() {
          this.quill.theme.tooltip.edit("formula");
        },
        image() {
          let t = this.container.querySelector("input.ql-image[type=file]");
          t == null && (t = document.createElement("input"), t.setAttribute("type", "file"), t.setAttribute("accept", this.quill.uploader.options.mimetypes.join(", ")), t.classList.add("ql-image"), t.addEventListener("change", () => {
            const e = this.quill.getSelection(!0);
            this.quill.uploader.upload(e, t.files), t.value = "";
          }), this.container.appendChild(t)), t.click();
        },
        video() {
          this.quill.theme.tooltip.edit("video");
        }
      }
    }
  }
});
class yl extends bl {
  constructor(e, s) {
    super(e, s), this.textbox = this.root.querySelector('input[type="text"]'), this.listen();
  }
  listen() {
    this.textbox.addEventListener("keydown", (e) => {
      e.key === "Enter" ? (this.save(), e.preventDefault()) : e.key === "Escape" && (this.cancel(), e.preventDefault());
    });
  }
  cancel() {
    this.hide(), this.restoreFocus();
  }
  edit() {
    let e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : "link", s = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : null;
    if (this.root.classList.remove("ql-hidden"), this.root.classList.add("ql-editing"), this.textbox == null) return;
    s != null ? this.textbox.value = s : e !== this.root.getAttribute("data-mode") && (this.textbox.value = "");
    const r = this.quill.getBounds(this.quill.selection.savedRange);
    r != null && this.position(r), this.textbox.select(), this.textbox.setAttribute("placeholder", this.textbox.getAttribute(`data-${e}`) || ""), this.root.setAttribute("data-mode", e);
  }
  restoreFocus() {
    this.quill.focus({
      preventScroll: !0
    });
  }
  save() {
    let {
      value: e
    } = this.textbox;
    switch (this.root.getAttribute("data-mode")) {
      case "link": {
        const {
          scrollTop: s
        } = this.quill.root;
        this.linkRange ? (this.quill.formatText(this.linkRange, "link", e, F.sources.USER), delete this.linkRange) : (this.restoreFocus(), this.quill.format("link", e, F.sources.USER)), this.quill.root.scrollTop = s;
        break;
      }
      case "video":
        e = PC(e);
      case "formula": {
        if (!e) break;
        const s = this.quill.getSelection(!0);
        if (s != null) {
          const r = s.index + s.length;
          this.quill.insertEmbed(
            r,
            // @ts-expect-error Fix me later
            this.root.getAttribute("data-mode"),
            e,
            F.sources.USER
          ), this.root.getAttribute("data-mode") === "formula" && this.quill.insertText(r + 1, " ", F.sources.USER), this.quill.setSelection(r + 2, F.sources.USER);
        }
        break;
      }
    }
    this.textbox.value = "", this.hide();
  }
}
function PC(t) {
  let e = t.match(/^(?:(https?):\/\/)?(?:(?:www|m)\.)?youtube\.com\/watch.*v=([a-zA-Z0-9_-]+)/) || t.match(/^(?:(https?):\/\/)?(?:(?:www|m)\.)?youtu\.be\/([a-zA-Z0-9_-]+)/);
  return e ? `${e[1] || "https"}://www.youtube.com/embed/${e[2]}?showinfo=0` : (e = t.match(/^(?:(https?):\/\/)?(?:www\.)?vimeo\.com\/(\d+)/)) ? `${e[1] || "https"}://player.vimeo.com/video/${e[2]}/` : t;
}
function Ps(t, e) {
  let s = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : !1;
  e.forEach((r) => {
    const i = document.createElement("option");
    r === s ? i.setAttribute("selected", "selected") : i.setAttribute("value", String(r)), t.appendChild(i);
  });
}
const DC = [["bold", "italic", "link"], [{
  header: 1
}, {
  header: 2
}, "blockquote"]];
class $l extends yl {
  constructor(e, s) {
    super(e, s), this.quill.on(F.events.EDITOR_CHANGE, (r, i, a, n) => {
      if (r === F.events.SELECTION_CHANGE)
        if (i != null && i.length > 0 && n === F.sources.USER) {
          this.show(), this.root.style.left = "0px", this.root.style.width = "", this.root.style.width = `${this.root.offsetWidth}px`;
          const o = this.quill.getLines(i.index, i.length);
          if (o.length === 1) {
            const u = this.quill.getBounds(i);
            u != null && this.position(u);
          } else {
            const u = o[o.length - 1], p = this.quill.getIndex(u), g = Math.min(u.length() - 1, i.index + i.length - p), k = this.quill.getBounds(new Pt(p, g));
            k != null && this.position(k);
          }
        } else document.activeElement !== this.textbox && this.quill.hasFocus() && this.hide();
    });
  }
  listen() {
    super.listen(), this.root.querySelector(".ql-close").addEventListener("click", () => {
      this.root.classList.remove("ql-editing");
    }), this.quill.on(F.events.SCROLL_OPTIMIZE, () => {
      setTimeout(() => {
        if (this.root.classList.contains("ql-hidden")) return;
        const e = this.quill.getSelection();
        if (e != null) {
          const s = this.quill.getBounds(e);
          s != null && this.position(s);
        }
      }, 1);
    });
  }
  cancel() {
    this.show();
  }
  position(e) {
    const s = super.position(e), r = this.root.querySelector(".ql-tooltip-arrow");
    return r.style.marginLeft = "", s !== 0 && (r.style.marginLeft = `${-1 * s - r.offsetWidth / 2}px`), s;
  }
}
B($l, "TEMPLATE", ['<span class="ql-tooltip-arrow"></span>', '<div class="ql-tooltip-editor">', '<input type="text" data-formula="e=mc^2" data-link="https://quilljs.com" data-video="Embed URL">', '<a class="ql-close"></a>', "</div>"].join(""));
class kl extends en {
  constructor(e, s) {
    s.modules.toolbar != null && s.modules.toolbar.container == null && (s.modules.toolbar.container = DC), super(e, s), this.quill.container.classList.add("ql-bubble");
  }
  extendToolbar(e) {
    this.tooltip = new $l(this.quill, this.options.bounds), e.container != null && (this.tooltip.root.appendChild(e.container), this.buildButtons(e.container.querySelectorAll("button"), Xs), this.buildPickers(e.container.querySelectorAll("select"), Xs));
  }
}
kl.DEFAULTS = yt({}, en.DEFAULTS, {
  modules: {
    toolbar: {
      handlers: {
        link(t) {
          t ? this.quill.theme.tooltip.edit() : this.quill.format("link", !1, N.sources.USER);
        }
      }
    }
  }
});
const RC = [[{
  header: ["1", "2", "3", !1]
}], ["bold", "italic", "underline", "link"], [{
  list: "ordered"
}, {
  list: "bullet"
}], ["clean"]];
class wl extends yl {
  constructor() {
    super(...arguments);
    B(this, "preview", this.root.querySelector("a.ql-preview"));
  }
  listen() {
    super.listen(), this.root.querySelector("a.ql-action").addEventListener("click", (s) => {
      this.root.classList.contains("ql-editing") ? this.save() : this.edit("link", this.preview.textContent), s.preventDefault();
    }), this.root.querySelector("a.ql-remove").addEventListener("click", (s) => {
      if (this.linkRange != null) {
        const r = this.linkRange;
        this.restoreFocus(), this.quill.formatText(r, "link", !1, F.sources.USER), delete this.linkRange;
      }
      s.preventDefault(), this.hide();
    }), this.quill.on(F.events.SELECTION_CHANGE, (s, r, i) => {
      if (s != null) {
        if (s.length === 0 && i === F.sources.USER) {
          const [a, n] = this.quill.scroll.descendant(bt, s.index);
          if (a != null) {
            this.linkRange = new Pt(s.index - n, a.length());
            const o = bt.formats(a.domNode);
            this.preview.textContent = o, this.preview.setAttribute("href", o), this.show();
            const u = this.quill.getBounds(this.linkRange);
            u != null && this.position(u);
            return;
          }
        } else
          delete this.linkRange;
        this.hide();
      }
    });
  }
  show() {
    super.show(), this.root.removeAttribute("data-mode");
  }
}
B(wl, "TEMPLATE", ['<a class="ql-preview" rel="noopener noreferrer" target="_blank" href="about:blank"></a>', '<input type="text" data-formula="e=mc^2" data-link="https://quilljs.com" data-video="Embed URL">', '<a class="ql-action"></a>', '<a class="ql-remove"></a>'].join(""));
class Cl extends en {
  constructor(e, s) {
    s.modules.toolbar != null && s.modules.toolbar.container == null && (s.modules.toolbar.container = RC), super(e, s), this.quill.container.classList.add("ql-snow");
  }
  extendToolbar(e) {
    e.container != null && (e.container.classList.add("ql-snow"), this.buildButtons(e.container.querySelectorAll("button"), Xs), this.buildPickers(e.container.querySelectorAll("select"), Xs), this.tooltip = new wl(this.quill, this.options.bounds), e.container.querySelector(".ql-link") && this.quill.keyboard.addBinding({
      key: "k",
      shortKey: !0
    }, (s, r) => {
      e.handlers.link.call(e, !r.format.link);
    }));
  }
}
Cl.DEFAULTS = yt({}, en.DEFAULTS, {
  modules: {
    toolbar: {
      handlers: {
        link(t) {
          if (t) {
            const e = this.quill.getSelection();
            if (e == null || e.length === 0) return;
            let s = this.quill.getText(e);
            /^\S+@\S+\.\S+$/.test(s) && s.indexOf("mailto:") !== 0 && (s = `mailto:${s}`);
            const {
              tooltip: r
            } = this.quill.theme;
            r.edit("link", s);
          } else
            this.quill.format("link", !1, N.sources.USER);
        }
      }
    }
  }
});
N.register({
  "attributors/attribute/direction": sl,
  "attributors/class/align": xo,
  "attributors/class/background": xk,
  "attributors/class/color": Jk,
  "attributors/class/direction": nl,
  "attributors/class/font": al,
  "attributors/class/size": ll,
  "attributors/style/align": el,
  "attributors/style/background": xi,
  "attributors/style/color": Ji,
  "attributors/style/direction": rl,
  "attributors/style/font": ol,
  "attributors/style/size": ul
}, !0);
N.register({
  "formats/align": xo,
  "formats/direction": nl,
  "formats/indent": Hw,
  "formats/background": xi,
  "formats/color": Ji,
  "formats/font": al,
  "formats/size": ll,
  "formats/blockquote": _i,
  "formats/code-block": me,
  "formats/header": Ni,
  "formats/list": xs,
  "formats/bold": Zs,
  "formats/code": ea,
  "formats/italic": Ii,
  "formats/link": bt,
  "formats/script": Li,
  "formats/strike": qi,
  "formats/underline": Oi,
  "formats/formula": Bn,
  "formats/image": Pi,
  "formats/video": zw,
  "modules/syntax": gl,
  "modules/table": Kw,
  "modules/toolbar": ia,
  "themes/bubble": kl,
  "themes/snow": Cl,
  "ui/icons": Xs,
  "ui/picker": er,
  "ui/icon-picker": vl,
  "ui/color-picker": ml,
  "ui/tooltip": bl
}, !0);
const BC = C({
  name: "RichTextEditor",
  props: {
    readonly: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(null);
    return Ce(() => {
      e.value && new N(e.value, {
        theme: "snow",
        readOnly: t.readonly,
        modules: {
          toolbar: !t.readonly
        }
      });
    }), {
      editor: e
    };
  }
}), MC = { class: "editor-container" }, FC = ["aria-readonly"];
function UC(t, e, s, r, i, a) {
  return d(), c("div", MC, [
    f("div", {
      ref: "editor",
      "aria-label": "Rich text editor",
      "aria-readonly": t.readonly
    }, null, 8, FC)
  ]);
}
const X4 = /* @__PURE__ */ A(BC, [["render", UC], ["__scopeId", "data-v-a295d163"]]), jC = C({
  name: "RulerAndGuides",
  setup() {
    const t = m(100), e = li([]), s = (a) => {
      console.log(a);
    }, r = (a, n) => {
      e.push({ x: a, y: n });
    }, i = (a) => {
      e.splice(a, 1);
    };
    return Ce(() => {
    }), {
      zoomLevel: t,
      guides: e,
      startMovingGuide: s,
      addGuide: r,
      removeGuide: i
    };
  }
}), VC = { class: "ruler-and-guides" }, HC = {
  class: "ruler",
  ref: "horizontalRuler",
  "aria-label": "Horizontal Ruler"
}, zC = {
  class: "ruler",
  ref: "verticalRuler",
  "aria-label": "Vertical Ruler"
}, GC = { class: "guides" }, KC = ["onMousedown"];
function WC(t, e, s, r, i, a) {
  return d(), c("div", VC, [
    f("div", HC, null, 512),
    f("div", zC, null, 512),
    f("div", GC, [
      (d(!0), c(I, null, L(t.guides, (n, o) => (d(), c("div", {
        key: o,
        style: ne({ left: n.x + "px", top: n.y + "px" }),
        class: "guide",
        "aria-label": "Guide",
        onMousedown: (u) => t.startMovingGuide(o)
      }, null, 44, KC))), 128))
    ])
  ]);
}
const Y4 = /* @__PURE__ */ A(jC, [["render", WC], ["__scopeId", "data-v-53005f5f"]]), ZC = C({
  name: "ScheduleCRUDPanel",
  props: {
    feedbackMessageProp: {
      type: String,
      default: ""
    }
  },
  setup(t) {
    const e = m({
      title: "",
      date: "",
      time: "",
      location: "",
      description: "",
      participants: ""
    }), s = m(t.feedbackMessageProp), r = () => {
      s.value = `Event "${e.value.title}" created successfully.`, n();
    }, i = () => {
      s.value = `Event "${e.value.title}" updated successfully.`;
    }, a = () => {
      s.value = `Event "${e.value.title}" deleted successfully.`, n();
    }, n = () => {
      e.value = {
        title: "",
        date: "",
        time: "",
        location: "",
        description: "",
        participants: ""
      };
    };
    return {
      form: e,
      feedbackMessage: s,
      handleSubmit: r,
      updateEvent: i,
      deleteEvent: a
    };
  }
}), XC = {
  class: "schedule-crud-panel",
  role: "region",
  "aria-label": "Schedule CRUD Panel"
}, YC = { class: "form-group" }, QC = { class: "form-group" }, JC = { class: "form-group" }, xC = { class: "form-group" }, eA = { class: "form-group" }, tA = { class: "form-group" }, sA = { class: "crud-buttons" }, nA = {
  key: 0,
  class: "feedback"
};
function rA(t, e, s, r, i, a) {
  return d(), c("div", XC, [
    f("form", {
      onSubmit: e[8] || (e[8] = de((...n) => t.handleSubmit && t.handleSubmit(...n), ["prevent"]))
    }, [
      f("div", YC, [
        e[9] || (e[9] = f("label", { for: "title" }, "Event Title", -1)),
        R(f("input", {
          type: "text",
          id: "title",
          "onUpdate:modelValue": e[0] || (e[0] = (n) => t.form.title = n),
          required: ""
        }, null, 512), [
          [H, t.form.title]
        ])
      ]),
      f("div", QC, [
        e[10] || (e[10] = f("label", { for: "date" }, "Date", -1)),
        R(f("input", {
          type: "date",
          id: "date",
          "onUpdate:modelValue": e[1] || (e[1] = (n) => t.form.date = n),
          required: ""
        }, null, 512), [
          [H, t.form.date]
        ])
      ]),
      f("div", JC, [
        e[11] || (e[11] = f("label", { for: "time" }, "Time", -1)),
        R(f("input", {
          type: "time",
          id: "time",
          "onUpdate:modelValue": e[2] || (e[2] = (n) => t.form.time = n),
          required: ""
        }, null, 512), [
          [H, t.form.time]
        ])
      ]),
      f("div", xC, [
        e[12] || (e[12] = f("label", { for: "location" }, "Location", -1)),
        R(f("input", {
          type: "text",
          id: "location",
          "onUpdate:modelValue": e[3] || (e[3] = (n) => t.form.location = n)
        }, null, 512), [
          [H, t.form.location]
        ])
      ]),
      f("div", eA, [
        e[13] || (e[13] = f("label", { for: "description" }, "Description", -1)),
        R(f("textarea", {
          id: "description",
          "onUpdate:modelValue": e[4] || (e[4] = (n) => t.form.description = n)
        }, null, 512), [
          [H, t.form.description]
        ])
      ]),
      f("div", tA, [
        e[14] || (e[14] = f("label", { for: "participants" }, "Participants", -1)),
        R(f("input", {
          type: "text",
          id: "participants",
          "onUpdate:modelValue": e[5] || (e[5] = (n) => t.form.participants = n)
        }, null, 512), [
          [H, t.form.participants]
        ])
      ]),
      f("div", sA, [
        e[15] || (e[15] = f("button", { type: "submit" }, "Create Event", -1)),
        f("button", {
          type: "button",
          onClick: e[6] || (e[6] = (...n) => t.updateEvent && t.updateEvent(...n))
        }, "Update Event"),
        f("button", {
          type: "button",
          onClick: e[7] || (e[7] = (...n) => t.deleteEvent && t.deleteEvent(...n))
        }, "Delete Event")
      ])
    ], 32),
    t.feedbackMessage ? (d(), c("div", nA, w(t.feedbackMessage), 1)) : P("", !0)
  ]);
}
const Q4 = /* @__PURE__ */ A(ZC, [["render", rA], ["__scopeId", "data-v-4d6e4564"]]), iA = C({
  name: "ScrollableList",
  props: {
    items: {
      type: Array,
      required: !0
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup() {
    const t = m(null), e = m(!1), s = m(null);
    return { hoveredItem: t, endOfList: e, onScroll: () => {
      if (s.value) {
        const { scrollTop: i, scrollHeight: a, clientHeight: n } = s.value;
        e.value = i + n >= a;
      }
    }, listRef: s };
  }
}), aA = ["aria-disabled"], oA = ["onMouseover"], lA = {
  key: 0,
  class: "end-of-list-message"
};
function uA(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "scrollable-list",
    "aria-disabled": t.disabled ? "true" : "false"
  }, [
    f("ul", {
      class: "scrollable-list-items",
      onScroll: e[1] || (e[1] = (...n) => t.onScroll && t.onScroll(...n)),
      ref: "listRef"
    }, [
      (d(!0), c(I, null, L(t.items, (n) => (d(), c("li", {
        key: n.id,
        class: q(["scrollable-list-item", { disabled: t.disabled, hover: n.id === t.hoveredItem }]),
        onMouseover: (o) => t.hoveredItem = n.id,
        onMouseleave: e[0] || (e[0] = (o) => t.hoveredItem = null)
      }, w(n.label), 43, oA))), 128))
    ], 544),
    t.endOfList ? (d(), c("div", lA, "End of List")) : P("", !0)
  ], 8, aA);
}
const J4 = /* @__PURE__ */ A(iA, [["render", uA], ["__scopeId", "data-v-a0c69f47"]]), dA = C({
  name: "SearchBar",
  props: {
    placeholder: {
      type: String,
      default: "Search..."
    },
    isFocused: {
      type: Boolean,
      default: !1
    },
    isDisabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.isFocused);
    return { handleFocus: () => {
      e.value = !0;
    }, handleBlur: () => {
      e.value = !1;
    } };
  }
}), cA = ["placeholder", "disabled"];
function fA(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["search-bar", { focused: t.isFocused, disabled: t.isDisabled }])
  }, [
    f("input", {
      type: "text",
      placeholder: t.placeholder,
      disabled: t.isDisabled,
      onFocus: e[0] || (e[0] = (...n) => t.handleFocus && t.handleFocus(...n)),
      onBlur: e[1] || (e[1] = (...n) => t.handleBlur && t.handleBlur(...n)),
      "aria-label": "Search"
    }, null, 40, cA)
  ], 2);
}
const x4 = /* @__PURE__ */ A(dA, [["render", fA], ["__scopeId", "data-v-dfc81841"]]), pA = C({
  name: "SearchBarWithSuggestions",
  props: {
    suggestions: {
      type: Array,
      default: () => []
    },
    filterOptions: {
      type: Array,
      default: () => []
    }
  },
  emits: ["search"],
  setup(t, { emit: e }) {
    const s = m(""), r = m([]), i = m(!1), a = () => {
      s.value ? (r.value = t.suggestions.filter(
        (o) => o.toLowerCase().includes(s.value.toLowerCase())
      ), i.value = r.value.length > 0) : i.value = !1;
    };
    return fs(s, a), {
      query: s,
      filteredSuggestions: r,
      showSuggestions: i,
      handleSearch: () => {
        e("search", s.value);
      },
      updateSuggestions: a
    };
  }
}), hA = { class: "search-bar-with-suggestions" }, gA = {
  key: 0,
  class: "suggestions-list",
  "aria-live": "polite"
}, mA = ["onClick"], vA = {
  key: 1,
  class: "no-results"
};
function bA(t, e, s, r, i, a) {
  return d(), c("div", hA, [
    R(f("input", {
      type: "text",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.query = n),
      onInput: e[1] || (e[1] = (...n) => t.updateSuggestions && t.updateSuggestions(...n)),
      onKeyup: e[2] || (e[2] = Rs((...n) => t.handleSearch && t.handleSearch(...n), ["enter"])),
      placeholder: "Search...",
      "aria-label": "Search"
    }, null, 544), [
      [H, t.query]
    ]),
    t.showSuggestions ? (d(), c("ul", gA, [
      (d(!0), c(I, null, L(t.filteredSuggestions, (n) => (d(), c("li", {
        key: n,
        onClick: (o) => {
          t.query = n, t.handleSearch();
        }
      }, w(n), 9, mA))), 128))
    ])) : P("", !0),
    t.query && !t.filteredSuggestions.length ? (d(), c("div", vA, " No results found ")) : P("", !0)
  ]);
}
const e3 = /* @__PURE__ */ A(pA, [["render", bA], ["__scopeId", "data-v-7d9836c1"]]), yA = C({
  name: "SearchInputWithFilterOptions",
  props: {
    placeholder: {
      type: String,
      default: "Search..."
    },
    disabled: {
      type: Boolean,
      default: !1
    },
    filtersActive: {
      type: Boolean,
      default: !1
    },
    noResults: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["update:filtersActive", "input"],
  setup(t, { emit: e }) {
    const s = m("");
    return {
      query: s,
      onInput: () => {
        e("input", s.value);
      },
      toggleFilters: () => {
        e("update:filtersActive", !t.filtersActive);
      }
    };
  }
}), $A = { class: "search-container" }, kA = ["placeholder", "disabled"], wA = ["aria-pressed"], CA = {
  key: 0,
  class: "filter-options"
}, AA = {
  key: 1,
  class: "no-results"
};
function EA(t, e, s, r, i, a) {
  return d(), c("div", $A, [
    R(f("input", {
      type: "text",
      placeholder: t.placeholder,
      disabled: t.disabled,
      "aria-label": "Search input",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.query = n),
      onInput: e[1] || (e[1] = (...n) => t.onInput && t.onInput(...n))
    }, null, 40, kA), [
      [H, t.query]
    ]),
    f("button", {
      "aria-pressed": t.filtersActive,
      onClick: e[2] || (e[2] = (...n) => t.toggleFilters && t.toggleFilters(...n))
    }, " Filters ", 8, wA),
    t.filtersActive ? (d(), c("div", CA, [
      ie(t.$slots, "filters", {}, void 0, !0)
    ])) : P("", !0),
    t.noResults ? (d(), c("div", AA, " No Results Found ")) : P("", !0)
  ]);
}
const t3 = /* @__PURE__ */ A(yA, [["render", EA], ["__scopeId", "data-v-8be8e8b9"]]), SA = C({
  name: "SearchWithAutocomplete",
  props: {
    options: {
      type: Array,
      default: () => []
    },
    query: {
      type: String,
      default: ""
    }
  },
  setup(t) {
    const e = m(t.query), s = W(
      () => t.options.filter(
        (i) => i.toLowerCase().includes(e.value.toLowerCase())
      )
    );
    return { query: e, filteredResults: s, onInput: () => {
    } };
  }
}), TA = { class: "search-autocomplete" }, _A = {
  key: 0,
  class: "results-list"
}, NA = {
  key: 1,
  class: "no-results"
};
function IA(t, e, s, r, i, a) {
  return d(), c("div", TA, [
    R(f("input", {
      type: "text",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.query = n),
      onInput: e[1] || (e[1] = (...n) => t.onInput && t.onInput(...n)),
      placeholder: "Search...",
      "aria-label": "Search input"
    }, null, 544), [
      [H, t.query]
    ]),
    t.query && t.filteredResults.length ? (d(), c("ul", _A, [
      (d(!0), c(I, null, L(t.filteredResults, (n, o) => (d(), c("li", { key: o }, w(n), 1))), 128))
    ])) : P("", !0),
    t.query && !t.filteredResults.length ? (d(), c("p", NA, "No results found.")) : P("", !0)
  ]);
}
const s3 = /* @__PURE__ */ A(SA, [["render", IA], ["__scopeId", "data-v-5ecf543f"]]), LA = C({
  name: "SelectableListWithItemDetails",
  props: {
    items: {
      type: Array,
      required: !0
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(null), s = m(null);
    return { selectedItem: e, openDetails: s, toggleSelection: (a) => {
      t.disabled || (e.value = e.value === a ? null : a);
    }, toggleDetails: (a) => {
      s.value = s.value === a ? null : a;
    } };
  }
}), qA = { class: "selectable-list" }, OA = { class: "selectable-list-items" }, PA = ["onClick"], DA = { class: "item-content" }, RA = ["onClick", "aria-expanded"], BA = {
  key: 0,
  class: "item-details"
};
function MA(t, e, s, r, i, a) {
  return d(), c("div", qA, [
    f("ul", OA, [
      (d(!0), c(I, null, L(t.items, (n) => (d(), c("li", {
        key: n.id,
        class: q(["selectable-list-item", { selected: n.id === t.selectedItem, disabled: t.disabled }]),
        onClick: (o) => t.toggleSelection(n.id)
      }, [
        f("div", DA, [
          Fe(w(n.label) + " ", 1),
          f("button", {
            onClick: de((o) => t.toggleDetails(n.id), ["stop"]),
            class: "details-button",
            "aria-expanded": n.id === t.openDetails ? "true" : "false"
          }, w(n.id === t.openDetails ? "Hide Details" : "Show Details"), 9, RA)
        ]),
        n.id === t.openDetails ? (d(), c("div", BA, w(n.details), 1)) : P("", !0)
      ], 10, PA))), 128))
    ])
  ]);
}
const n3 = /* @__PURE__ */ A(LA, [["render", MA], ["__scopeId", "data-v-213fd947"]]), FA = C({
  name: "ShapeLibrary",
  setup() {
    const t = m(""), e = [
      { name: "Circle", icon: "/icons/circle.svg" },
      { name: "Square", icon: "/icons/square.svg" },
      { name: "Triangle", icon: "/icons/triangle.svg" }
    ], s = W(
      () => e.filter((i) => i.name.toLowerCase().includes(t.value.toLowerCase()))
    );
    return {
      searchQuery: t,
      filteredShapes: s,
      onDragStart: (i) => {
        console.log(i);
      }
    };
  }
}), UA = { class: "shape-library" }, jA = { class: "shape-list" }, VA = ["onDragstart"], HA = ["src", "alt"];
function zA(t, e, s, r, i, a) {
  return d(), c("div", UA, [
    R(f("input", {
      type: "text",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.searchQuery = n),
      placeholder: "Search shapes...",
      "aria-label": "Search shapes"
    }, null, 512), [
      [H, t.searchQuery]
    ]),
    f("div", jA, [
      (d(!0), c(I, null, L(t.filteredShapes, (n, o) => (d(), c("div", {
        key: o,
        class: "shape-item",
        draggable: "true",
        onDragstart: (u) => t.onDragStart(n),
        "aria-label": "Shape"
      }, [
        f("img", {
          src: n.icon,
          alt: n.name
        }, null, 8, HA)
      ], 40, VA))), 128))
    ])
  ]);
}
const r3 = /* @__PURE__ */ A(FA, [["render", zA], ["__scopeId", "data-v-f12478ca"]]), GA = C({
  name: "ShapeTool",
  setup() {
    const t = m(!1), e = m("rectangle"), s = m(50), r = m("#000000"), i = m("#ffffff"), a = m(1);
    return {
      isActive: t,
      selectedShape: e,
      size: s,
      fillColor: r,
      borderColor: i,
      thickness: a,
      toggleActive: () => {
        t.value = !t.value;
      }
    };
  }
}), KA = ["aria-pressed"], WA = {
  key: 0,
  class: "shape-settings"
};
function ZA(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["shape-tool", { active: t.isActive }])
  }, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleActive && t.toggleActive(...n)),
      "aria-pressed": t.isActive,
      class: "shape-button"
    }, "Shape Tool", 8, KA),
    t.isActive ? (d(), c("div", WA, [
      e[7] || (e[7] = f("label", { for: "shape" }, "Shape", -1)),
      R(f("select", {
        id: "shape",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.selectedShape = n),
        "aria-label": "Select Shape"
      }, [...e[6] || (e[6] = [
        f("option", { value: "rectangle" }, "Rectangle", -1),
        f("option", { value: "circle" }, "Circle", -1),
        f("option", { value: "ellipse" }, "Ellipse", -1),
        f("option", { value: "line" }, "Line", -1)
      ])], 512), [
        [ye, t.selectedShape]
      ]),
      e[8] || (e[8] = f("label", { for: "size" }, "Size", -1)),
      R(f("input", {
        id: "size",
        type: "range",
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.size = n),
        min: "1",
        max: "100",
        "aria-valuemin": "1",
        "aria-valuemax": "100",
        "aria-valuenow": "size"
      }, null, 512), [
        [H, t.size]
      ]),
      e[9] || (e[9] = f("label", { for: "fillColor" }, "Fill Color", -1)),
      R(f("input", {
        id: "fillColor",
        type: "color",
        "onUpdate:modelValue": e[3] || (e[3] = (n) => t.fillColor = n),
        "aria-label": "Fill Color"
      }, null, 512), [
        [H, t.fillColor]
      ]),
      e[10] || (e[10] = f("label", { for: "borderColor" }, "Border Color", -1)),
      R(f("input", {
        id: "borderColor",
        type: "color",
        "onUpdate:modelValue": e[4] || (e[4] = (n) => t.borderColor = n),
        "aria-label": "Border Color"
      }, null, 512), [
        [H, t.borderColor]
      ]),
      e[11] || (e[11] = f("label", { for: "thickness" }, "Thickness", -1)),
      R(f("input", {
        id: "thickness",
        type: "range",
        "onUpdate:modelValue": e[5] || (e[5] = (n) => t.thickness = n),
        min: "1",
        max: "10",
        "aria-valuemin": "1",
        "aria-valuemax": "10",
        "aria-valuenow": "thickness"
      }, null, 512), [
        [H, t.thickness]
      ])
    ])) : P("", !0)
  ], 2);
}
const i3 = /* @__PURE__ */ A(GA, [["render", ZA], ["__scopeId", "data-v-f0914fde"]]), XA = C({
  name: "SignalStrengthIndicator",
  props: {
    strength: {
      type: Number,
      default: 0,
      validator: (t) => t >= 0 && t <= 5
    }
  },
  setup(t) {
    const e = [1, 2, 3, 4, 5], s = W(() => {
      switch (t.strength) {
        case 5:
          return "Full Signal";
        case 4:
        case 3:
          return "Good Signal";
        case 2:
        case 1:
          return "Weak Signal";
        default:
          return "No Signal";
      }
    });
    return {
      levels: e,
      ariaLabel: s
    };
  }
}), YA = ["aria-label"];
function QA(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "signal-strength-indicator",
    role: "status",
    "aria-label": t.ariaLabel
  }, [
    (d(!0), c(I, null, L(t.levels, (n) => (d(), c("div", {
      key: n,
      class: q(["bar", { active: n <= t.strength }]),
      style: ne({ height: `${n * 20}%` })
    }, null, 6))), 128))
  ], 8, YA);
}
const a3 = /* @__PURE__ */ A(XA, [["render", QA], ["__scopeId", "data-v-7623f4d7"]]), JA = C({
  name: "SingleChoicePoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    options: {
      type: Array,
      required: !0
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["update:selectedOption"],
  setup(t, { emit: e }) {
    const s = m(null);
    return {
      selectedOption: s,
      handleChange: () => {
        e("update:selectedOption", s.value);
      }
    };
  }
}), xA = {
  role: "group",
  "aria-labelledby": "poll-question",
  class: "poll"
}, eE = { id: "poll-question" }, tE = ["id", "value", "disabled", "aria-checked"], sE = ["for"];
function nE(t, e, s, r, i, a) {
  return d(), c("div", xA, [
    f("p", eE, w(t.question), 1),
    (d(!0), c(I, null, L(t.options, (n) => (d(), c("div", {
      key: n,
      class: "option"
    }, [
      R(f("input", {
        type: "radio",
        id: n,
        value: n,
        "onUpdate:modelValue": e[0] || (e[0] = (o) => t.selectedOption = o),
        disabled: t.isDisabled,
        onChange: e[1] || (e[1] = (...o) => t.handleChange && t.handleChange(...o)),
        "aria-checked": t.selectedOption === n
      }, null, 40, tE), [
        [Il, t.selectedOption]
      ]),
      f("label", { for: n }, w(n), 9, sE)
    ]))), 128))
  ]);
}
const o3 = /* @__PURE__ */ A(JA, [["render", nE], ["__scopeId", "data-v-ff3ebf2c"]]), rE = C({
  name: "SkeletonLoading",
  props: {
    loading: {
      type: Boolean,
      default: !0
    }
  }
}), iE = ["aria-busy"], aE = {
  key: 0,
  class: "skeleton"
};
function oE(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "skeleton-loading",
    "aria-busy": t.loading
  }, [
    t.loading ? (d(), c("div", aE)) : ie(t.$slots, "default", { key: 1 }, void 0, !0)
  ], 8, iE);
}
const l3 = /* @__PURE__ */ A(rE, [["render", oE], ["__scopeId", "data-v-0ddff634"]]), lE = C({
  name: "Slider",
  props: {
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      default: 100
    },
    value: {
      type: Number,
      default: 50
    },
    step: {
      type: Number,
      default: 1
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showValue: {
      type: Boolean,
      default: !1
    }
  },
  setup(t, { emit: e }) {
    return { updateValue: (r) => {
      const i = r.target.valueAsNumber;
      e("update:value", i);
    } };
  }
}), uE = ["min", "max", "value", "step", "disabled"], dE = {
  key: 0,
  class: "slider-value"
};
function cE(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["slider-container", { disabled: t.isDisabled }])
  }, [
    f("input", {
      type: "range",
      min: t.min,
      max: t.max,
      value: t.value,
      step: t.step,
      disabled: t.isDisabled,
      onInput: e[0] || (e[0] = (...n) => t.updateValue && t.updateValue(...n)),
      "aria-label": "Slider"
    }, null, 40, uE),
    t.showValue ? (d(), c("span", dE, w(t.value), 1)) : P("", !0)
  ], 2);
}
const u3 = /* @__PURE__ */ A(lE, [["render", cE], ["__scopeId", "data-v-ee851f84"]]), fE = C({
  name: "SliderPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    min: {
      type: Number,
      default: 1
    },
    max: {
      type: Number,
      default: 100
    },
    initialValue: {
      type: Number,
      default: 50
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialValue), s = m(`slider-${Math.random().toString(36).substr(2, 9)}`);
    return {
      selectedValue: e,
      updateValue: (i) => {
        if (!t.isDisabled) {
          const a = i.target;
          e.value = Number(a.value);
        }
      },
      id: s
    };
  }
}), pE = { class: "slider-poll" }, hE = ["for"], gE = ["id", "min", "max", "value", "disabled", "aria-valuenow"], mE = {
  key: 0,
  class: "results"
};
function vE(t, e, s, r, i, a) {
  return d(), c("div", pE, [
    f("label", {
      for: t.id,
      class: "slider-label"
    }, w(t.question), 9, hE),
    f("input", {
      type: "range",
      id: t.id,
      min: t.min,
      max: t.max,
      value: t.initialValue,
      disabled: t.isDisabled,
      onInput: e[0] || (e[0] = (...n) => t.updateValue && t.updateValue(...n)),
      class: "slider",
      "aria-valuemin": "min",
      "aria-valuemax": "max",
      "aria-valuenow": t.selectedValue,
      "aria-label": "Value slider"
    }, null, 40, gE),
    t.showResults ? (d(), c("div", mE, [
      f("p", null, "Selected Value: " + w(t.selectedValue), 1)
    ])) : P("", !0)
  ]);
}
const d3 = /* @__PURE__ */ A(fE, [["render", vE], ["__scopeId", "data-v-dd791633"]]), bE = C({
  name: "SortControl",
  props: {
    columns: {
      type: Array,
      default: () => []
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["sort"],
  setup(t, { emit: e }) {
    const s = m({});
    return {
      sortState: s,
      toggleSort: (a) => {
        t.disabled || (!s.value[a] || s.value[a] === "desc" ? s.value[a] = "asc" : s.value[a] = "desc", e("sort", { column: a, order: s.value[a] }));
      },
      getSortIcon: (a) => s.value[a] === "asc" ? "↑" : s.value[a] === "desc" ? "↓" : ""
    };
  }
}), yE = { class: "sort-control" }, $E = ["onClick", "aria-disabled"];
function kE(t, e, s, r, i, a) {
  return d(), c("div", yE, [
    (d(!0), c(I, null, L(t.columns, (n) => (d(), c("div", {
      key: n,
      class: q(["sort-button", { disabled: t.disabled }]),
      onClick: (o) => t.toggleSort(n),
      "aria-disabled": t.disabled,
      role: "button"
    }, [
      Fe(w(n) + " ", 1),
      f("span", null, w(t.getSortIcon(n)), 1)
    ], 10, $E))), 128))
  ]);
}
const c3 = /* @__PURE__ */ A(bE, [["render", kE], ["__scopeId", "data-v-07bb3c30"]]), wE = C({
  name: "SortableList",
  props: {
    items: {
      type: Array,
      required: !0
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(null);
    return { onDragStart: (i) => {
      t.disabled || (e.value = i);
    }, onDrop: (i) => {
      if (e.value !== null && e.value !== i && !t.disabled) {
        const a = t.items[e.value];
        t.items.splice(e.value, 1), t.items.splice(i, 0, a), e.value = null;
      }
    }, draggingIndex: e };
  }
}), CE = ["aria-disabled"], AE = ["draggable", "onDragstart", "onDrop"];
function EE(t, e, s, r, i, a) {
  return d(), c("ul", {
    class: "sortable-list",
    "aria-disabled": t.disabled
  }, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("li", {
      key: n.id,
      draggable: !t.disabled,
      onDragstart: (u) => t.onDragStart(o),
      onDragover: e[0] || (e[0] = de(() => {
      }, ["prevent"])),
      onDrop: (u) => t.onDrop(o),
      class: q({ dragging: t.draggingIndex === o })
    }, w(n.label), 43, AE))), 128))
  ], 8, CE);
}
const f3 = /* @__PURE__ */ A(wE, [["render", EE], ["__scopeId", "data-v-2f34b2ff"]]), SE = C({
  name: "SortableTable",
  props: {
    columns: {
      type: Array,
      required: !0
    },
    data: {
      type: Array,
      required: !0
    }
  },
  setup(t) {
    const e = m(null), s = m(1), r = m(""), i = m(null), a = (p) => {
      e.value === p ? s.value = -s.value : (e.value = p, s.value = 1);
    }, n = (p) => {
      i.value = i.value === p ? null : p;
    }, o = (p) => e.value === p ? s.value === 1 ? "asc" : "desc" : "", u = W(() => {
      let p = t.data.filter(
        (g) => Object.values(g).some((k) => k.toString().toLowerCase().includes(r.value.toLowerCase()))
      );
      return e.value && p.sort((g, k) => {
        const y = g[e.value], b = k[e.value];
        return y < b ? -1 * s.value : y > b ? 1 * s.value : 0;
      }), p;
    });
    return { sortBy: a, selectRow: n, getSortDirection: o, filteredAndSortedData: u, filterText: r, selectedRow: i };
  }
}), TE = { class: "sortable-table" }, _E = ["onClick"], NE = ["onClick"];
function IE(t, e, s, r, i, a) {
  return d(), c("div", TE, [
    R(f("input", {
      type: "text",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.filterText = n),
      class: "filter-input",
      placeholder: "Filter table...",
      "aria-label": "Filter table"
    }, null, 512), [
      [H, t.filterText]
    ]),
    f("table", null, [
      f("thead", null, [
        f("tr", null, [
          (d(!0), c(I, null, L(t.columns, (n) => (d(), c("th", {
            key: n.key,
            onClick: (o) => t.sortBy(n.key)
          }, [
            Fe(w(n.label) + " ", 1),
            f("span", {
              class: q(t.getSortDirection(n.key))
            }, null, 2)
          ], 8, _E))), 128))
        ])
      ]),
      f("tbody", null, [
        (d(!0), c(I, null, L(t.filteredAndSortedData, (n) => (d(), c("tr", {
          key: n.id,
          class: q({ selected: n.id === t.selectedRow }),
          onClick: (o) => t.selectRow(n.id)
        }, [
          (d(!0), c(I, null, L(t.columns, (o) => (d(), c("td", {
            key: o.key
          }, w(n[o.key]), 1))), 128))
        ], 10, NE))), 128))
      ])
    ])
  ]);
}
const p3 = /* @__PURE__ */ A(SE, [["render", IE], ["__scopeId", "data-v-339e4c57"]]), LE = C({
  name: "StarRatingPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    totalStars: {
      type: Number,
      default: 5
    },
    initialRating: {
      type: Number,
      default: 0
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialRating);
    return {
      rating: e,
      rate: (r) => {
        t.isDisabled || (e.value = r);
      }
    };
  }
}), qE = {
  class: "star-rating-poll",
  role: "radiogroup",
  "aria-labelledby": "poll-question"
}, OE = { id: "poll-question" }, PE = { class: "stars" }, DE = ["aria-checked", "disabled", "onClick"];
function RE(t, e, s, r, i, a) {
  return d(), c("div", qE, [
    f("p", OE, w(t.question), 1),
    f("div", PE, [
      (d(!0), c(I, null, L(t.totalStars, (n) => (d(), c("button", {
        key: n,
        "aria-checked": n <= t.rating,
        disabled: t.isDisabled,
        onClick: (o) => t.rate(n),
        class: q(["star", { filled: n <= t.rating }]),
        role: "radio"
      }, " ★ ", 10, DE))), 128))
    ])
  ]);
}
const h3 = /* @__PURE__ */ A(LE, [["render", RE], ["__scopeId", "data-v-f5091b77"]]), BE = C({
  name: "StatusDots",
  props: {
    status: {
      type: String,
      default: "offline",
      validator: (t) => ["online", "offline", "busy", "idle"].includes(t)
    }
  },
  setup(t) {
    const e = W(() => {
      switch (t.status) {
        case "online":
          return "var(--status-online-color, #4caf50)";
        case "offline":
          return "var(--status-offline-color, #f44336)";
        case "busy":
          return "var(--status-busy-color, #ff9800)";
        case "idle":
          return "var(--status-idle-color, #ffeb3b)";
        default:
          return "var(--status-offline-color, #f44336)";
      }
    }), s = W(() => {
      switch (t.status) {
        case "online":
          return "User is online";
        case "offline":
          return "User is offline";
        case "busy":
          return "User is busy";
        case "idle":
          return "User is idle";
        default:
          return "User status unknown";
      }
    });
    return {
      statusColor: e,
      ariaLabel: s
    };
  }
}), ME = ["aria-label"];
function FE(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "status-dots",
    role: "status",
    "aria-label": t.ariaLabel
  }, [
    f("span", {
      class: q(["dot", t.status]),
      style: ne({ backgroundColor: t.statusColor })
    }, null, 6)
  ], 8, ME);
}
const g3 = /* @__PURE__ */ A(BE, [["render", FE], ["__scopeId", "data-v-2e464e2a"]]), UE = C({
  name: "Stepper",
  props: {
    steps: {
      type: Array,
      required: !0
    }
  }
}), jE = {
  class: "stepper",
  "aria-label": "Progress steps"
}, VE = ["aria-current"], HE = { class: "step-label" };
function zE(t, e, s, r, i, a) {
  return d(), c("nav", jE, [
    f("ol", null, [
      (d(!0), c(I, null, L(t.steps, (n, o) => (d(), c("li", {
        key: o,
        class: q(["step", n.status]),
        "aria-current": n.status === "active" ? "step" : void 0
      }, [
        f("span", HE, w(n.label), 1)
      ], 10, VE))), 128))
    ])
  ]);
}
const m3 = /* @__PURE__ */ A(UE, [["render", zE], ["__scopeId", "data-v-f866a8b6"]]), GE = C({
  name: "SystemAlertGlobalNotificationBar",
  props: {
    type: {
      type: String,
      required: !0,
      validator: (t) => ["success", "error", "warning", "info"].includes(t)
    },
    message: {
      type: String,
      required: !0
    }
  }
}), KE = ["aria-live"], WE = { class: "notification-message" };
function ZE(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["notification-bar", t.type]),
    role: "alert",
    "aria-live": t.type === "error" ? "assertive" : "polite"
  }, [
    f("span", WE, w(t.message), 1)
  ], 10, KE);
}
const v3 = /* @__PURE__ */ A(GE, [["render", ZE], ["__scopeId", "data-v-d2e84c71"]]), XE = C({
  name: "Tabs",
  props: {
    tabs: {
      type: Array,
      required: !0
    },
    initialActiveIndex: {
      type: Number,
      default: 0
    }
  },
  setup(t) {
    const e = m(t.initialActiveIndex);
    return { activeIndex: e, selectTab: (r) => {
      t.tabs[r].disabled || (e.value = r);
    } };
  }
}), YE = {
  class: "tabs",
  role: "tablist"
}, QE = ["aria-selected", "disabled", "onClick"];
function JE(t, e, s, r, i, a) {
  return d(), c("div", YE, [
    (d(!0), c(I, null, L(t.tabs, (n, o) => (d(), c("button", {
      key: n.id,
      role: "tab",
      "aria-selected": t.activeIndex === o,
      disabled: n.disabled,
      class: q({
        active: t.activeIndex === o,
        disabled: n.disabled
      }),
      onClick: (u) => t.selectTab(o)
    }, w(n.label), 11, QE))), 128))
  ]);
}
const b3 = /* @__PURE__ */ A(XE, [["render", JE], ["__scopeId", "data-v-71783afe"]]), xE = C({
  name: "TaskCompletionCheckList",
  props: {
    tasks: {
      type: Array,
      required: !0
    }
  }
}), eS = { class: "checklist" }, tS = ["checked", "indeterminate", "aria-checked"], sS = { class: "task-label" };
function nS(t, e, s, r, i, a) {
  return d(), c("ul", eS, [
    (d(!0), c(I, null, L(t.tasks, (n, o) => (d(), c("li", {
      key: o,
      class: q({
        checked: n.status === "checked",
        unchecked: n.status === "unchecked",
        partiallyComplete: n.status === "partiallyComplete"
      })
    }, [
      f("input", {
        type: "checkbox",
        checked: n.status === "checked",
        indeterminate: n.status === "partiallyComplete",
        "aria-checked": n.status === "checked" ? "true" : n.status === "partiallyComplete" ? "mixed" : "false",
        disabled: ""
      }, null, 8, tS),
      f("span", sS, w(n.label), 1)
    ], 2))), 128))
  ]);
}
const y3 = /* @__PURE__ */ A(xE, [["render", nS], ["__scopeId", "data-v-1aebe86c"]]), rS = C({
  name: "TextTool",
  setup() {
    const t = m(!1), e = m("Arial"), s = m(16), r = m("#000000"), i = m("left");
    return {
      isActive: t,
      fontStyle: e,
      fontSize: s,
      fontColor: r,
      alignment: i,
      fontStyles: ["Arial", "Verdana", "Times New Roman"],
      alignments: ["left", "center", "right"],
      toggleActive: () => {
        t.value = !t.value;
      }
    };
  }
}), iS = { class: "text-tool" }, aS = {
  key: 0,
  class: "text-options"
}, oS = ["value"], lS = ["value"];
function uS(t, e, s, r, i, a) {
  return d(), c("div", iS, [
    f("button", {
      onClick: e[0] || (e[0] = (...n) => t.toggleActive && t.toggleActive(...n)),
      class: q({ active: t.isActive }),
      "aria-label": "Text Tool"
    }, "Text Tool", 2),
    t.isActive ? (d(), c("div", aS, [
      e[5] || (e[5] = f("label", { for: "font-style" }, "Font Style:", -1)),
      R(f("select", {
        id: "font-style",
        "onUpdate:modelValue": e[1] || (e[1] = (n) => t.fontStyle = n)
      }, [
        (d(!0), c(I, null, L(t.fontStyles, (n) => (d(), c("option", {
          key: n,
          value: n
        }, w(n), 9, oS))), 128))
      ], 512), [
        [ye, t.fontStyle]
      ]),
      e[6] || (e[6] = f("label", { for: "font-size" }, "Font Size:", -1)),
      R(f("input", {
        id: "font-size",
        type: "number",
        "onUpdate:modelValue": e[2] || (e[2] = (n) => t.fontSize = n)
      }, null, 512), [
        [H, t.fontSize]
      ]),
      e[7] || (e[7] = f("label", { for: "font-color" }, "Color:", -1)),
      R(f("input", {
        id: "font-color",
        type: "color",
        "onUpdate:modelValue": e[3] || (e[3] = (n) => t.fontColor = n)
      }, null, 512), [
        [H, t.fontColor]
      ]),
      e[8] || (e[8] = f("label", { for: "alignment" }, "Alignment:", -1)),
      R(f("select", {
        id: "alignment",
        "onUpdate:modelValue": e[4] || (e[4] = (n) => t.alignment = n)
      }, [
        (d(!0), c(I, null, L(t.alignments, (n) => (d(), c("option", {
          key: n,
          value: n
        }, w(n), 9, lS))), 128))
      ], 512), [
        [ye, t.alignment]
      ])
    ])) : P("", !0)
  ]);
}
const $3 = /* @__PURE__ */ A(rS, [["render", uS], ["__scopeId", "data-v-a7cdacd4"]]), dS = C({
  name: "Textarea",
  props: {
    placeholder: {
      type: String,
      default: "Enter text..."
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["input"],
  setup(t, { emit: e }) {
    const s = m("");
    return {
      text: s,
      onInput: () => {
        e("input", s.value);
      }
    };
  }
}), cS = { class: "textarea-container" }, fS = ["placeholder", "disabled"];
function pS(t, e, s, r, i, a) {
  return d(), c("div", cS, [
    R(f("textarea", {
      placeholder: t.placeholder,
      disabled: t.disabled,
      "aria-label": "Textarea input",
      "onUpdate:modelValue": e[0] || (e[0] = (n) => t.text = n),
      onInput: e[1] || (e[1] = (...n) => t.onInput && t.onInput(...n))
    }, null, 40, fS), [
      [H, t.text]
    ])
  ]);
}
const k3 = /* @__PURE__ */ A(dS, [["render", pS], ["__scopeId", "data-v-b0ae56b0"]]), hS = C({
  name: "ThumbsUpThumbsDownPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    initialSelection: {
      type: String,
      default: null
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialSelection);
    return {
      selectedThumb: e,
      selectThumb: (r) => {
        t.isDisabled || (e.value = r);
      }
    };
  }
}), gS = {
  class: "thumbs-poll",
  role: "radiogroup",
  "aria-labelledby": "poll-question"
}, mS = { id: "poll-question" }, vS = { class: "thumbs" }, bS = ["aria-checked", "disabled"], yS = ["aria-checked", "disabled"];
function $S(t, e, s, r, i, a) {
  return d(), c("div", gS, [
    f("p", mS, w(t.question), 1),
    f("div", vS, [
      f("button", {
        "aria-checked": t.selectedThumb === "up",
        disabled: t.isDisabled,
        onClick: e[0] || (e[0] = (n) => t.selectThumb("up")),
        class: q(["thumb", { selected: t.selectedThumb === "up" }]),
        role: "radio"
      }, " 👍 ", 10, bS),
      f("button", {
        "aria-checked": t.selectedThumb === "down",
        disabled: t.isDisabled,
        onClick: e[1] || (e[1] = (n) => t.selectThumb("down")),
        class: q(["thumb", { selected: t.selectedThumb === "down" }]),
        role: "radio"
      }, " 👎 ", 10, yS)
    ])
  ]);
}
const w3 = /* @__PURE__ */ A(hS, [["render", $S], ["__scopeId", "data-v-64adc4b2"]]), kS = C({
  name: "TimelineAdjuster",
  props: {
    feedbackMessage: {
      type: String,
      default: ""
    }
  },
  setup(t) {
    const e = m(1), s = m(0), r = m(t.feedbackMessage), i = m(!1), a = m(0), n = Array.from({ length: 24 }, (E, S) => S);
    return {
      zoomLevel: e,
      timelineOffset: s,
      feedbackMessage: r,
      zoomIn: () => {
        e.value < 3 && (e.value += 1, r.value = `Zoom level: ${e.value}`);
      },
      zoomOut: () => {
        e.value > 1 && (e.value -= 1, r.value = `Zoom level: ${e.value}`);
      },
      startDrag: (E) => {
        i.value = !0, a.value = E.clientX;
      },
      stopDrag: () => {
        i.value = !1;
      },
      drag: (E) => {
        i.value && (s.value += E.clientX - a.value, a.value = E.clientX);
      },
      goToToday: () => {
        r.value = "Navigated to today";
      },
      goToNextDay: () => {
        r.value = "Navigated to next day";
      },
      goToPreviousDay: () => {
        r.value = "Navigated to previous day";
      },
      hours: n
    };
  }
}), wS = {
  class: "timeline-adjuster",
  role: "region",
  "aria-label": "Timeline Adjuster"
}, CS = { class: "zoom-controls" }, AS = { class: "navigation" }, ES = {
  key: 0,
  class: "feedback"
};
function SS(t, e, s, r, i, a) {
  return d(), c("div", wS, [
    f("div", CS, [
      f("button", {
        onClick: e[0] || (e[0] = (...n) => t.zoomIn && t.zoomIn(...n)),
        "aria-label": "Zoom in"
      }, "+"),
      f("button", {
        onClick: e[1] || (e[1] = (...n) => t.zoomOut && t.zoomOut(...n)),
        "aria-label": "Zoom out"
      }, "-")
    ]),
    f("div", {
      class: "timeline-container",
      onMousedown: e[2] || (e[2] = (...n) => t.startDrag && t.startDrag(...n)),
      onMouseup: e[3] || (e[3] = (...n) => t.stopDrag && t.stopDrag(...n)),
      onMouseleave: e[4] || (e[4] = (...n) => t.stopDrag && t.stopDrag(...n)),
      onMousemove: e[5] || (e[5] = (...n) => t.drag && t.drag(...n))
    }, [
      f("div", {
        class: "timeline",
        style: ne({ transform: `translateX(${t.timelineOffset}px)` })
      }, [
        (d(!0), c(I, null, L(t.hours, (n) => (d(), c("div", {
          key: n,
          class: "time-slot"
        }, w(n) + ":00", 1))), 128))
      ], 4)
    ], 32),
    f("div", AS, [
      f("button", {
        onClick: e[6] || (e[6] = (...n) => t.goToToday && t.goToToday(...n)),
        "aria-label": "Go to today"
      }, "Today"),
      f("button", {
        onClick: e[7] || (e[7] = (...n) => t.goToNextDay && t.goToNextDay(...n)),
        "aria-label": "Go to next day"
      }, "Next Day"),
      f("button", {
        onClick: e[8] || (e[8] = (...n) => t.goToPreviousDay && t.goToPreviousDay(...n)),
        "aria-label": "Go to previous day"
      }, "Previous Day")
    ]),
    t.feedbackMessage ? (d(), c("div", ES, w(t.feedbackMessage), 1)) : P("", !0)
  ]);
}
const C3 = /* @__PURE__ */ A(kS, [["render", SS], ["__scopeId", "data-v-e10b0b13"]]), TS = C({
  name: "TimelineList",
  props: {
    items: {
      type: Array,
      required: !0
    },
    activeIndex: {
      type: Number,
      default: 0
    }
  }
}), _S = {
  class: "timeline-list",
  role: "list"
}, NS = { class: "timeline-content" }, IS = { class: "timeline-label" };
function LS(t, e, s, r, i, a) {
  return d(), c("ul", _S, [
    (d(!0), c(I, null, L(t.items, (n, o) => (d(), c("li", {
      key: n.id,
      class: q({
        active: o === t.activeIndex,
        completed: n.completed,
        inactive: !n.completed && o !== t.activeIndex
      }),
      role: "listitem"
    }, [
      f("div", NS, [
        f("span", IS, w(n.label), 1)
      ])
    ], 2))), 128))
  ]);
}
const A3 = /* @__PURE__ */ A(TS, [["render", LS], ["__scopeId", "data-v-553e4b1b"]]), qS = C({
  name: "Toast",
  props: {
    message: {
      type: String,
      required: !0
    },
    type: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(!0);
    return { dismiss: () => {
      t.value = !1;
    }, isVisible: t };
  }
});
function OS(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["toast", t.type]),
    role: "alert",
    "aria-live": "assertive",
    "aria-atomic": "true"
  }, [
    f("span", null, w(t.message), 1),
    f("button", {
      class: "close-btn",
      onClick: e[0] || (e[0] = (...n) => t.dismiss && t.dismiss(...n)),
      "aria-label": "Dismiss"
    }, " × ")
  ], 2);
}
const E3 = /* @__PURE__ */ A(qS, [["render", OS], ["__scopeId", "data-v-761055db"]]), PS = C({
  name: "ToggleSwitch",
  props: {
    checked: {
      type: Boolean,
      default: !1
    },
    disabled: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["change"],
  setup(t, { emit: e }) {
    return {
      onToggle: (r) => {
        e("change", r.target.checked);
      }
    };
  }
}), DS = { class: "toggle-switch" }, RS = ["checked", "disabled", "aria-checked"];
function BS(t, e, s, r, i, a) {
  return d(), c("div", DS, [
    f("input", {
      type: "checkbox",
      checked: t.checked,
      disabled: t.disabled,
      onChange: e[0] || (e[0] = (...n) => t.onToggle && t.onToggle(...n)),
      "aria-checked": t.checked,
      role: "switch"
    }, null, 40, RS),
    e[1] || (e[1] = f("span", { class: "slider" }, null, -1))
  ]);
}
const S3 = /* @__PURE__ */ A(PS, [["render", BS], ["__scopeId", "data-v-ad0fe00a"]]), MS = C({
  name: "TreeviewList",
  props: {
    nodes: {
      type: Array,
      required: !0
    }
  },
  methods: {
    toggleNode(t) {
      t.expanded = !t.expanded;
    }
  }
}), FS = {
  class: "treeview-list",
  role: "tree"
}, US = ["aria-expanded"], jS = ["onClick"], VS = { class: "treeview-label" };
function HS(t, e, s, r, i, a) {
  const n = Ll("TreeviewList", !0);
  return d(), c("ul", FS, [
    (d(!0), c(I, null, L(t.nodes, (o) => (d(), c("li", {
      key: o.id,
      class: q({
        expanded: o.expanded,
        selected: o.selected
      }),
      role: "treeitem",
      "aria-expanded": o.expanded
    }, [
      f("div", {
        class: "treeview-node",
        onClick: (u) => t.toggleNode(o)
      }, [
        f("span", VS, w(o.label), 1)
      ], 8, jS),
      o.children && o.expanded ? (d(), uo(n, {
        key: 0,
        nodes: o.children
      }, null, 8, ["nodes"])) : P("", !0)
    ], 10, US))), 128))
  ]);
}
const T3 = /* @__PURE__ */ A(MS, [["render", HS], ["__scopeId", "data-v-140b42d6"]]), zS = C({
  name: "UndoRedoButtons",
  setup() {
    const t = m(!1), e = m(!1);
    return {
      canUndo: t,
      canRedo: e,
      undo: () => {
        t.value && (e.value = !0, t.value = !1);
      },
      redo: () => {
        e.value && (t.value = !0, e.value = !1);
      }
    };
  }
}), GS = { class: "undo-redo-buttons" }, KS = ["disabled"], WS = ["disabled"];
function ZS(t, e, s, r, i, a) {
  return d(), c("div", GS, [
    f("button", {
      disabled: !t.canUndo,
      onClick: e[0] || (e[0] = (...n) => t.undo && t.undo(...n)),
      "aria-label": "Undo",
      class: q({ active: t.canUndo })
    }, "Undo", 10, KS),
    f("button", {
      disabled: !t.canRedo,
      onClick: e[1] || (e[1] = (...n) => t.redo && t.redo(...n)),
      "aria-label": "Redo",
      class: q({ active: t.canRedo })
    }, "Redo", 10, WS)
  ]);
}
const _3 = /* @__PURE__ */ A(zS, [["render", ZS], ["__scopeId", "data-v-a47f68b7"]]), XS = C({
  name: "Upload",
  props: {
    message: {
      type: String,
      required: !0
    },
    status: {
      type: String,
      required: !0
    },
    progress: {
      type: Number,
      default: 0
    }
  },
  setup(t) {
    const e = m(t.status === "uploading" || t.status === "downloading"), s = m(t.status === "uploading");
    return { progressVisible: e, showCancelButton: s, cancelUpload: () => {
      console.log("Upload cancelled.");
    } };
  }
}), YS = ["value"];
function QS(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["upload", t.status])
  }, [
    f("span", null, w(t.message), 1),
    t.progressVisible ? (d(), c("progress", {
      key: 0,
      value: t.progress,
      max: "100"
    }, null, 8, YS)) : P("", !0),
    t.showCancelButton ? (d(), c("button", {
      key: 1,
      onClick: e[0] || (e[0] = (...n) => t.cancelUpload && t.cancelUpload(...n)),
      class: "cancel-btn",
      "aria-label": "Cancel Upload"
    }, " Cancel ")) : P("", !0)
  ], 2);
}
const N3 = /* @__PURE__ */ A(XS, [["render", QS], ["__scopeId", "data-v-97cfacf5"]]), JS = C({
  name: "ValidationMessages",
  props: {
    type: {
      type: String,
      default: "success",
      validator: (t) => ["success", "error", "warning"].includes(t)
    }
  }
});
function xS(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["validation-message", t.type]),
    role: "alert",
    "aria-live": "assertive"
  }, [
    ie(t.$slots, "default", {}, void 0, !0)
  ], 2);
}
const I3 = /* @__PURE__ */ A(JS, [["render", xS], ["__scopeId", "data-v-3cbe2019"]]), e5 = C({
  name: "Video",
  props: {
    videoSrc: {
      type: String,
      required: !0
    },
    initialState: {
      type: String,
      default: "paused"
    }
  },
  setup(t) {
    const e = m(t.initialState === "uploading"), s = m(t.initialState === "paused"), r = m(t.initialState === "completed"), i = m(t.initialState === "error"), a = m(null);
    return {
      isUploading: e,
      isPaused: s,
      isCompleted: r,
      isError: i,
      videoElement: a,
      onPlay: () => {
        s.value = !1;
      },
      onPause: () => {
        s.value = !0;
      }
    };
  }
}), t5 = {
  class: "video-container",
  role: "region",
  "aria-label": "Video Player"
}, s5 = ["src"], n5 = {
  class: "status",
  "aria-live": "polite"
}, r5 = {
  key: 0,
  class: "status-text"
}, i5 = {
  key: 1,
  class: "status-text"
}, a5 = {
  key: 2,
  class: "status-text"
}, o5 = {
  key: 3,
  class: "status-text"
};
function l5(t, e, s, r, i, a) {
  return d(), c("div", t5, [
    f("video", {
      ref: "videoElement",
      src: t.videoSrc,
      onPlay: e[0] || (e[0] = (...n) => t.onPlay && t.onPlay(...n)),
      onPause: e[1] || (e[1] = (...n) => t.onPause && t.onPause(...n)),
      controls: "",
      class: "video-element"
    }, null, 40, s5),
    f("div", n5, [
      t.isUploading ? (d(), c("span", r5, "Uploading...")) : P("", !0),
      t.isPaused ? (d(), c("span", i5, "Paused")) : P("", !0),
      t.isCompleted ? (d(), c("span", a5, "Completed")) : P("", !0),
      t.isError ? (d(), c("span", o5, "Error")) : P("", !0)
    ])
  ]);
}
const L3 = /* @__PURE__ */ A(e5, [["render", l5], ["__scopeId", "data-v-02494477"]]), u5 = C({
  name: "VideoPlayer",
  props: {
    videoSrc: {
      type: String,
      required: !0
    }
  },
  setup() {
    const t = m(!1), e = m(!1), s = m(null);
    return Ce(() => {
      s.value && (s.value.controls = !1);
    }), {
      isPlaying: t,
      isFullscreen: e,
      videoElement: s,
      togglePlayPause: () => {
        s.value && (s.value.paused ? s.value.play() : s.value.pause());
      },
      toggleFullscreen: () => {
        s.value && (document.fullscreenElement ? document.exitFullscreen() : s.value.requestFullscreen());
      },
      onPlay: () => {
        t.value = !0;
      },
      onPause: () => {
        t.value = !1;
      },
      onBuffering: () => {
        t.value = !1;
      },
      onFullscreenChange: () => {
        e.value = !!document.fullscreenElement;
      }
    };
  }
}), d5 = {
  class: "video-player",
  role: "region",
  "aria-label": "Video Player"
}, c5 = ["src"], f5 = { class: "controls" };
function p5(t, e, s, r, i, a) {
  return d(), c("div", d5, [
    f("video", {
      ref: "videoElement",
      src: t.videoSrc,
      onPlay: e[0] || (e[0] = (...n) => t.onPlay && t.onPlay(...n)),
      onPause: e[1] || (e[1] = (...n) => t.onPause && t.onPause(...n)),
      onWaiting: e[2] || (e[2] = (...n) => t.onBuffering && t.onBuffering(...n)),
      onFullscreenchange: e[3] || (e[3] = (...n) => t.onFullscreenChange && t.onFullscreenChange(...n)),
      controls: "",
      class: "video-element"
    }, null, 40, c5),
    f("div", f5, [
      f("button", {
        onClick: e[4] || (e[4] = (...n) => t.togglePlayPause && t.togglePlayPause(...n)),
        "aria-label": "Play/Pause",
        class: "control-btn"
      }, w(t.isPlaying ? "Pause" : "Play"), 1),
      f("button", {
        onClick: e[5] || (e[5] = (...n) => t.toggleFullscreen && t.toggleFullscreen(...n)),
        "aria-label": "Fullscreen",
        class: "control-btn"
      }, w(t.isFullscreen ? "Exit Fullscreen" : "Fullscreen"), 1)
    ])
  ]);
}
const q3 = /* @__PURE__ */ A(u5, [["render", p5], ["__scopeId", "data-v-2d5e89b2"]]), h5 = C({
  name: "VirtualizedList",
  props: {
    items: {
      type: Array,
      required: !0
    },
    itemHeight: {
      type: Number,
      default: 50
    }
  },
  setup(t) {
    const e = m(400), s = W(() => Math.ceil(e.value / t.itemHeight)), r = m(0), i = m(!1), a = m(!1), n = W(() => t.items.slice(r.value, r.value + s.value)), o = (u) => {
      const p = u.target;
      p.scrollTop + p.clientHeight >= p.scrollHeight && (r.value + s.value < t.items.length ? (i.value = !0, setTimeout(() => {
        r.value += s.value, i.value = !1;
      }, 1e3)) : a.value = !0);
    };
    return Ce(() => {
      var u;
      e.value = ((u = document.querySelector(".virtualized-list")) == null ? void 0 : u.clientHeight) || 400;
    }), { visibleItems: n, onScroll: o, loading: i, endOfList: a };
  }
}), g5 = {
  key: 0,
  class: "loading-indicator"
}, m5 = {
  key: 1,
  class: "end-of-list"
};
function v5(t, e, s, r, i, a) {
  return d(), c("div", {
    class: "virtualized-list",
    role: "list",
    onScroll: e[0] || (e[0] = (...n) => t.onScroll && t.onScroll(...n))
  }, [
    (d(!0), c(I, null, L(t.visibleItems, (n) => (d(), c("div", {
      key: n.id,
      class: "list-item",
      role: "listitem"
    }, w(n.label), 1))), 128)),
    t.loading ? (d(), c("div", g5, "Loading more items...")) : t.endOfList ? (d(), c("div", m5, "End of list")) : P("", !0)
  ], 32);
}
const O3 = /* @__PURE__ */ A(h5, [["render", v5], ["__scopeId", "data-v-a52d90b7"]]), b5 = C({
  name: "VisualCueForAccessibilityFocusIndicator",
  props: {
    label: {
      type: String,
      required: !0
    },
    isFocused: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.isFocused);
    return { handleFocus: () => {
      e.value = !0;
    }, handleBlur: () => {
      e.value = !1;
    } };
  }
});
function y5(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["focus-indicator", { focused: t.isFocused }]),
    tabindex: "0",
    onFocus: e[0] || (e[0] = (...n) => t.handleFocus && t.handleFocus(...n)),
    onBlur: e[1] || (e[1] = (...n) => t.handleBlur && t.handleBlur(...n))
  }, [
    f("span", null, w(t.label), 1)
  ], 34);
}
const P3 = /* @__PURE__ */ A(b5, [["render", y5], ["__scopeId", "data-v-3d5d03e6"]]), $5 = C({
  name: "WinningHandDisplay",
  props: {
    communityCards: {
      type: Array,
      default: () => []
    },
    playerCards: {
      type: Array,
      default: () => []
    },
    winningCards: {
      type: Array,
      default: () => []
    },
    isHidden: {
      type: Boolean,
      default: !1
    }
  }
}), k5 = { class: "cards" };
function w5(t, e, s, r, i, a) {
  return d(), c("div", {
    class: q(["winning-hand-display", { hidden: t.isHidden }]),
    "aria-label": "Winning Hand Display"
  }, [
    f("div", k5, [
      (d(!0), c(I, null, L(t.communityCards, (n, o) => (d(), c("div", {
        key: "community-" + o,
        class: "card community-card"
      }, w(n), 1))), 128)),
      (d(!0), c(I, null, L(t.playerCards, (n, o) => (d(), c("div", {
        key: "player-" + o,
        class: q(["card player-card", { winner: t.winningCards.includes(n) }])
      }, w(n), 3))), 128))
    ])
  ], 2);
}
const D3 = /* @__PURE__ */ A($5, [["render", w5], ["__scopeId", "data-v-65bb899c"]]), C5 = C({
  name: "YesNoPoll",
  props: {
    question: {
      type: String,
      required: !0
    },
    initialSelection: {
      type: String,
      default: null
    },
    isDisabled: {
      type: Boolean,
      default: !1
    },
    showResults: {
      type: Boolean,
      default: !1
    }
  },
  setup(t) {
    const e = m(t.initialSelection);
    return {
      selectedOption: e,
      selectOption: (r) => {
        t.isDisabled || (e.value = r);
      }
    };
  }
}), A5 = {
  class: "yes-no-poll",
  role: "radiogroup",
  "aria-labelledby": "poll-question"
}, E5 = { id: "poll-question" }, S5 = { class: "options" }, T5 = ["aria-checked", "disabled"], _5 = ["aria-checked", "disabled"];
function N5(t, e, s, r, i, a) {
  return d(), c("div", A5, [
    f("p", E5, w(t.question), 1),
    f("div", S5, [
      f("button", {
        "aria-checked": t.selectedOption === "yes",
        disabled: t.isDisabled,
        onClick: e[0] || (e[0] = (n) => t.selectOption("yes")),
        class: q(["option", { selected: t.selectedOption === "yes" }]),
        role: "radio"
      }, " Yes ", 10, T5),
      f("button", {
        "aria-checked": t.selectedOption === "no",
        disabled: t.isDisabled,
        onClick: e[1] || (e[1] = (n) => t.selectOption("no")),
        class: q(["option", { selected: t.selectedOption === "no" }]),
        role: "radio"
      }, " No ", 10, _5)
    ])
  ]);
}
const R3 = /* @__PURE__ */ A(C5, [["render", N5], ["__scopeId", "data-v-5d57e636"]]), I5 = C({
  name: "ZoomTool",
  setup() {
    const t = m(100);
    return {
      zoomLevel: t,
      zoomIn: () => {
        t.value < 500 && (t.value += 10);
      },
      zoomOut: () => {
        t.value > 10 && (t.value -= 10);
      },
      fitToScreen: () => {
        t.value = 100;
      },
      resetZoom: () => {
        t.value = 100;
      }
    };
  }
}), L5 = { class: "zoom-tool" }, q5 = { class: "zoom-controls" }, O5 = { class: "zoom-level" };
function P5(t, e, s, r, i, a) {
  return d(), c("div", L5, [
    f("div", q5, [
      f("button", {
        onClick: e[0] || (e[0] = (...n) => t.zoomIn && t.zoomIn(...n)),
        "aria-label": "Zoom In"
      }, "+"),
      f("span", O5, w(t.zoomLevel) + "%", 1),
      f("button", {
        onClick: e[1] || (e[1] = (...n) => t.zoomOut && t.zoomOut(...n)),
        "aria-label": "Zoom Out"
      }, "-")
    ]),
    f("button", {
      onClick: e[2] || (e[2] = (...n) => t.fitToScreen && t.fitToScreen(...n)),
      "aria-label": "Fit to Screen"
    }, "Fit to Screen"),
    f("button", {
      onClick: e[3] || (e[3] = (...n) => t.resetZoom && t.resetZoom(...n)),
      "aria-label": "Reset Zoom"
    }, "Reset")
  ]);
}
const B3 = /* @__PURE__ */ A(I5, [["render", P5], ["__scopeId", "data-v-e6c5dde0"]]);
export {
  M5 as Accordion,
  F5 as ActionableList,
  U5 as ActivityIndicators,
  j5 as AdminViewScheduler,
  V5 as AudioPlayer,
  H5 as AudioPlayerAdvanced,
  z5 as AudioWaveformDisplay,
  G5 as Avatar,
  K5 as Badge,
  W5 as BadgeWithCounts,
  Z5 as BatteryLevelIndicator,
  X5 as BetSlider,
  Y5 as BottomNavigationBar,
  Q5 as BreadcrumbWithDropdowns,
  J5 as Breadcrumbs,
  x5 as BrushTool,
  eT as Button,
  tT as CalendarView,
  sT as CallButton,
  nT as Canvas,
  rT as Captcha,
  iT as CardActions,
  aT as CardBadge,
  oT as CardBody,
  lT as CardFooter,
  uT as CardHeader,
  dT as CardImage,
  cT as CardbasedList,
  fT as Carousel,
  pT as ChatBubble,
  hT as CheckList,
  gT as Checkbox,
  mT as Chips,
  vT as CollapsibleMenuList,
  bT as ColorPicker,
  yT as ColumnVisibilityToggle,
  $T as CommandPalette,
  kT as CommunityCards,
  wT as ContextualList,
  CT as ContextualNavigation,
  AT as CountdownTimer,
  ET as DarkModeToggle,
  ST as DataExportButton,
  TT as DataFilterPanel,
  _T as DataGrid,
  NT as DataImportDialog,
  IT as DataSummary,
  LT as DataTable,
  qT as DateAndTimePicker,
  OT as DatePicker,
  PT as DealerButton,
  DT as DeckOfCards,
  RT as DiscardPile,
  BT as DragAndDropScheduler,
  MT as DropdownMenu,
  FT as EditableDataTable,
  UT as EmbeddedMediaIframe,
  jT as EmojiReactionPoll,
  VT as EraserTool,
  HT as EventDetailsDialog,
  zT as EventFilterBar,
  GT as EventReminderSystem,
  KT as ExpandableList,
  WT as FavoritesList,
  ZT as FieldEditableDataTable,
  XT as FileInputWithPreview,
  YT as FileUpload,
  QT as FillTool,
  JT as FilterableList,
  xT as FlipCard,
  e4 as FloatingActionButton,
  t4 as FoldButton,
  s4 as GroupedList,
  n4 as HandOfCards,
  r4 as IconButton,
  i4 as ImageChoicePoll,
  a4 as ImageSlider,
  o4 as InteractiveMediaMap,
  l4 as InteractivePollResults,
  u4 as LayerPanel,
  d4 as LiveResultsPoll,
  c4 as LiveStreamPlayer,
  f4 as LoadMoreButtonInList,
  p4 as LoadingBarsWithSteps,
  h4 as LoadingSpinner,
  g4 as MediaGallery,
  m4 as MultipleChoicePoll,
  v4 as MultiselectList,
  b4 as Notification,
  y4 as NotificationBellIcon,
  $4 as NumberInputWithIncrement,
  k4 as NumberedList,
  w4 as OpenEndedPoll,
  C4 as Pagination,
  A4 as PaginationControl,
  E4 as PasswordConfirmationField,
  S4 as PinnedList,
  T4 as PlayingCard,
  _4 as PodcastPlayer,
  N4 as PokerChips,
  I4 as PokerHand,
  L4 as PokerTable,
  q4 as PokerTimer,
  O4 as Pot,
  P4 as ProgressBar,
  D4 as ProgressCircle,
  R4 as PublicViewCalendar,
  B4 as RadioButton,
  M4 as RaiseButton,
  F4 as RangeSlider,
  U4 as RankingPoll,
  j4 as RatingStars,
  V4 as RecurringEventScheduler,
  X4 as RichTextEditor,
  Y4 as RulerAndGuides,
  Q4 as ScheduleCRUDPanel,
  J4 as ScrollableList,
  x4 as SearchBar,
  e3 as SearchBarWithSuggestions,
  t3 as SearchInputWithFilterOptions,
  s3 as SearchWithAutocomplete,
  n3 as SelectableListWithItemDetails,
  r3 as ShapeLibrary,
  i3 as ShapeTool,
  a3 as SignalStrengthIndicator,
  o3 as SingleChoicePoll,
  l3 as SkeletonLoading,
  u3 as Slider,
  d3 as SliderPoll,
  c3 as SortControl,
  f3 as SortableList,
  p3 as SortableTable,
  h3 as StarRatingPoll,
  g3 as StatusDots,
  m3 as Stepper,
  v3 as SystemAlertGlobalNotificationBar,
  b3 as Tabs,
  y3 as TaskCompletionCheckList,
  $3 as TextTool,
  k3 as Textarea,
  B5 as ThreeSixtyDegreeImageViewer,
  w3 as ThumbsUpThumbsDownPoll,
  C3 as TimelineAdjuster,
  A3 as TimelineList,
  E3 as Toast,
  S3 as ToggleSwitch,
  T3 as TreeviewList,
  _3 as UndoRedoButtons,
  N3 as Upload,
  I3 as ValidationMessages,
  L3 as Video,
  q3 as VideoPlayer,
  O3 as VirtualizedList,
  P3 as VisualCueForAccessibilityFocusIndicator,
  D3 as WinningHandDisplay,
  R3 as YesNoPoll,
  B3 as ZoomTool
};
