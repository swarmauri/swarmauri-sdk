var xe = Object.defineProperty;
var Be = (t, e, n) => e in t ? xe(t, e, { enumerable: !0, configurable: !0, writable: !0, value: n }) : t[e] = n;
var te = (t, e, n) => Be(t, typeof e != "symbol" ? e + "" : e, n);
import ze from "eventemitter3";
import { getContext as Te, setContext as ne } from "svelte";
function p() {
}
function oe(t, e) {
  for (const n in e) t[n] = e[n];
  return (
    /** @type {T & S} */
    t
  );
}
function Fe(t) {
  return t();
}
function ve() {
  return /* @__PURE__ */ Object.create(null);
}
function P(t) {
  t.forEach(Fe);
}
function ue(t) {
  return typeof t == "function";
}
function T(t, e) {
  return t != t ? e == e : t !== e || t && typeof t == "object" || typeof t == "function";
}
function Je(t) {
  return Object.keys(t).length === 0;
}
function Ie(t, ...e) {
  if (t == null) {
    for (const s of e)
      s(void 0);
    return p;
  }
  const n = t.subscribe(...e);
  return n.unsubscribe ? () => n.unsubscribe() : n;
}
function $(t, e, n) {
  t.$$.on_destroy.push(Ie(e, n));
}
function fe(t, e, n, s) {
  if (t) {
    const i = je(t, e, n, s);
    return t[0](i);
  }
}
function je(t, e, n, s) {
  return t[1] && s ? oe(n.ctx.slice(), t[1](s(e))) : n.ctx;
}
function ae(t, e, n, s) {
  if (t[2] && s) {
    const i = t[2](s(n));
    if (e.dirty === void 0)
      return i;
    if (typeof i == "object") {
      const c = [], l = Math.max(e.dirty.length, i.length);
      for (let r = 0; r < l; r += 1)
        c[r] = e.dirty[r] | i[r];
      return c;
    }
    return e.dirty | i;
  }
  return e.dirty;
}
function de(t, e, n, s, i, c) {
  if (i) {
    const l = je(e, n, s, c);
    t.p(l, i);
  }
}
function he(t) {
  if (t.ctx.length > 32) {
    const e = [], n = t.ctx.length / 32;
    for (let s = 0; s < n; s++)
      e[s] = -1;
    return e;
  }
  return -1;
}
function Q(t, e) {
  t.appendChild(e);
}
function b(t, e, n) {
  t.insertBefore(e, n || null);
}
function y(t) {
  t.parentNode && t.parentNode.removeChild(t);
}
function F(t) {
  return document.createElement(t);
}
function q(t) {
  return document.createTextNode(t);
}
function _e() {
  return q(" ");
}
function U() {
  return q("");
}
function Ue(t, e, n, s) {
  return t.addEventListener(e, n, s), () => t.removeEventListener(e, n, s);
}
function L(t, e, n) {
  n == null ? t.removeAttribute(e) : t.getAttribute(e) !== n && t.setAttribute(e, n);
}
function Ge(t) {
  return Array.from(t.childNodes);
}
function me(t, e) {
  e = "" + e, t.data !== e && (t.data = /** @type {string} */
  e);
}
function I(t, e, n, s) {
  n == null ? t.style.removeProperty(e) : t.style.setProperty(e, n, "");
}
function Y(t, e, n) {
  t.classList.toggle(e, !!n);
}
function ke(t, e) {
  return new t(e);
}
let pe;
function j(t) {
  pe = t;
}
const A = [], Ee = [];
let D = [];
const Se = [], He = /* @__PURE__ */ Promise.resolve();
let re = !1;
function Ve() {
  re || (re = !0, He.then(qe));
}
function ce(t) {
  D.push(t);
}
const se = /* @__PURE__ */ new Set();
let N = 0;
function qe() {
  if (N !== 0)
    return;
  const t = pe;
  do {
    try {
      for (; N < A.length; ) {
        const e = A[N];
        N++, j(e), Xe(e.$$);
      }
    } catch (e) {
      throw A.length = 0, N = 0, e;
    }
    for (j(null), A.length = 0, N = 0; Ee.length; ) Ee.pop()();
    for (let e = 0; e < D.length; e += 1) {
      const n = D[e];
      se.has(n) || (se.add(n), n());
    }
    D.length = 0;
  } while (A.length);
  for (; Se.length; )
    Se.pop()();
  re = !1, se.clear(), j(t);
}
function Xe(t) {
  if (t.fragment !== null) {
    t.update(), P(t.before_update);
    const e = t.dirty;
    t.dirty = [-1], t.fragment && t.fragment.p(t.ctx, e), t.after_update.forEach(ce);
  }
}
function Ze(t) {
  const e = [], n = [];
  D.forEach((s) => t.indexOf(s) === -1 ? e.push(s) : n.push(s)), n.forEach((s) => s()), D = e;
}
const K = /* @__PURE__ */ new Set();
let M;
function J() {
  M = {
    r: 0,
    c: [],
    p: M
    // parent group
  };
}
function G() {
  M.r || P(M.c), M = M.p;
}
function w(t, e) {
  t && t.i && (K.delete(t), t.i(e));
}
function v(t, e, n, s) {
  if (t && t.o) {
    if (K.has(t)) return;
    K.add(t), M.c.push(() => {
      K.delete(t), s && (n && t.d(1), s());
    }), t.o(e);
  } else s && s();
}
function x(t) {
  return (t == null ? void 0 : t.length) !== void 0 ? t : Array.from(t);
}
function et(t, e) {
  t.d(1), e.delete(t.key);
}
function tt(t, e) {
  v(t, 1, 1, () => {
    e.delete(t.key);
  });
}
function We(t, e, n, s, i, c, l, r, o, u, h, a) {
  let _ = t.length, f = c.length, d = _;
  const g = {};
  for (; d--; ) g[t[d].key] = d;
  const S = [], X = /* @__PURE__ */ new Map(), Z = /* @__PURE__ */ new Map(), ye = [];
  for (d = f; d--; ) {
    const m = a(i, c, d), k = n(m);
    let E = l.get(k);
    E ? ye.push(() => E.p(m, e)) : (E = u(k, m), E.c()), X.set(k, S[d] = E), k in g && Z.set(k, Math.abs(d - g[k]));
  }
  const be = /* @__PURE__ */ new Set(), we = /* @__PURE__ */ new Set();
  function ee(m) {
    w(m, 1), m.m(r, h), l.set(m.key, m), h = m.first, f--;
  }
  for (; _ && f; ) {
    const m = S[f - 1], k = t[_ - 1], E = m.key, W = k.key;
    m === k ? (h = m.first, _--, f--) : X.has(W) ? !l.has(E) || be.has(E) ? ee(m) : we.has(W) ? _-- : Z.get(E) > Z.get(W) ? (we.add(E), ee(m)) : (be.add(W), _--) : (o(k, l), _--);
  }
  for (; _--; ) {
    const m = t[_];
    X.has(m.key) || o(m, l);
  }
  for (; f; ) ee(S[f - 1]);
  return P(ye), S;
}
function $e(t, e) {
  const n = {}, s = {}, i = { $$scope: 1 };
  let c = t.length;
  for (; c--; ) {
    const l = t[c], r = e[c];
    if (r) {
      for (const o in l)
        o in r || (s[o] = 1);
      for (const o in r)
        i[o] || (n[o] = r[o], i[o] = 1);
      t[c] = r;
    } else
      for (const o in l)
        i[o] = 1;
  }
  for (const l in s)
    l in n || (n[l] = void 0);
  return n;
}
function Le(t) {
  return typeof t == "object" && t !== null ? t : {};
}
function le(t) {
  t && t.c();
}
function B(t, e, n) {
  const { fragment: s, after_update: i } = t.$$;
  s && s.m(e, n), ce(() => {
    const c = t.$$.on_mount.map(Fe).filter(ue);
    t.$$.on_destroy ? t.$$.on_destroy.push(...c) : P(c), t.$$.on_mount = [];
  }), i.forEach(ce);
}
function z(t, e) {
  const n = t.$$;
  n.fragment !== null && (Ze(n.after_update), P(n.on_destroy), n.fragment && n.fragment.d(e), n.on_destroy = n.fragment = null, n.ctx = []);
}
function nt(t, e) {
  t.$$.dirty[0] === -1 && (A.push(t), Ve(), t.$$.dirty.fill(0)), t.$$.dirty[e / 31 | 0] |= 1 << e % 31;
}
function H(t, e, n, s, i, c, l = null, r = [-1]) {
  const o = pe;
  j(t);
  const u = t.$$ = {
    fragment: null,
    ctx: [],
    // state
    props: c,
    update: p,
    not_equal: i,
    bound: ve(),
    // lifecycle
    on_mount: [],
    on_destroy: [],
    on_disconnect: [],
    before_update: [],
    after_update: [],
    context: new Map(e.context || (o ? o.$$.context : [])),
    // everything else
    callbacks: ve(),
    dirty: r,
    skip_bound: !1,
    root: e.target || o.$$.root
  };
  l && l(u.root);
  let h = !1;
  if (u.ctx = n ? n(t, e.props || {}, (a, _, ...f) => {
    const d = f.length ? f[0] : _;
    return u.ctx && i(u.ctx[a], u.ctx[a] = d) && (!u.skip_bound && u.bound[a] && u.bound[a](d), h && nt(t, a)), _;
  }) : [], u.update(), h = !0, P(u.before_update), u.fragment = s ? s(u.ctx) : !1, e.target) {
    if (e.hydrate) {
      const a = Ge(e.target);
      u.fragment && u.fragment.l(a), a.forEach(y);
    } else
      u.fragment && u.fragment.c();
    e.intro && w(t.$$.fragment), B(t, e.target, e.anchor), qe();
  }
  j(o);
}
class V {
  constructor() {
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    te(this, "$$");
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    te(this, "$$set");
  }
  /** @returns {void} */
  $destroy() {
    z(this, 1), this.$destroy = p;
  }
  /**
   * @template {Extract<keyof Events, string>} K
   * @param {K} type
   * @param {((e: Events[K]) => void) | null | undefined} callback
   * @returns {() => void}
   */
  $on(e, n) {
    if (!ue(n))
      return p;
    const s = this.$$.callbacks[e] || (this.$$.callbacks[e] = []);
    return s.push(n), () => {
      const i = s.indexOf(n);
      i !== -1 && s.splice(i, 1);
    };
  }
  /**
   * @param {Partial<Props>} props
   * @returns {void}
   */
  $set(e) {
    this.$$set && !Je(e) && (this.$$.skip_bound = !0, this.$$set(e), this.$$.skip_bound = !1);
  }
}
const st = "4", C = [];
function it(t, e) {
  return {
    subscribe: R(t, e).subscribe
  };
}
function R(t, e = p) {
  let n;
  const s = /* @__PURE__ */ new Set();
  function i(r) {
    if (T(t, r) && (t = r, n)) {
      const o = !C.length;
      for (const u of s)
        u[1](), C.push(u, t);
      if (o) {
        for (let u = 0; u < C.length; u += 2)
          C[u][0](C[u + 1]);
        C.length = 0;
      }
    }
  }
  function c(r) {
    i(r(t));
  }
  function l(r, o = p) {
    const u = [r, o];
    return s.add(u), s.size === 1 && (n = e(i, c) || p), r(t), () => {
      s.delete(u), s.size === 0 && n && (n(), n = null);
    };
  }
  return { set: i, update: c, subscribe: l };
}
function O(t, e, n) {
  const s = !Array.isArray(t), i = s ? [t] : t;
  if (!i.every(Boolean))
    throw new Error("derived() expects stores as input, got a falsy value");
  const c = e.length < 2;
  return it(n, (l, r) => {
    let o = !1;
    const u = [];
    let h = 0, a = p;
    const _ = () => {
      if (h)
        return;
      a();
      const d = e(s ? u[0] : u, l, r);
      c ? l(d) : a = ue(d) ? d : p;
    }, f = i.map(
      (d, g) => Ie(
        d,
        (S) => {
          u[g] = S, h &= ~(1 << g), o && _();
        },
        () => {
          h |= 1 << g;
        }
      )
    );
    return o = !0, _(), function() {
      P(f), a(), o = !1;
    };
  });
}
const ie = /* @__PURE__ */ new Map(), Me = /* @__PURE__ */ new Map();
async function ot(t) {
  const e = await fetch(t);
  if (!e.ok)
    throw new Error(`Failed to fetch manifest: ${e.status} ${e.statusText}`);
  return await e.json();
}
async function rt(t) {
  if (!t.module)
    throw new Error(`Missing module specifier for atom ${t.role}`);
  const e = await import(
    /* @vite-ignore */
    t.module
  ), n = t.export ?? "default";
  if (!(n in e))
    throw new Error(`Export '${n}' not found in module ${t.module}`);
  return e[n];
}
function ct(t, e) {
  var s;
  if (e) return e;
  const n = (s = t.meta) != null && s.atoms && typeof t.meta.atoms == "object" ? t.meta.atoms.revision : void 0;
  return String(n ?? t.etag ?? t.version ?? "default");
}
async function lt(t, e = {}) {
  const n = e.fetcher ?? ot, s = e.importResolver ?? rt, i = await n(t), c = ct(i, e.cacheKey);
  if (ie.has(c)) {
    const o = ie.get(c), u = Me.get(c) ?? /* @__PURE__ */ new Map();
    return { manifest: o, components: u };
  }
  const l = /* @__PURE__ */ new Map(), r = i.tiles.map((o) => o.atom).filter((o) => !!(o && o.family === "swarmakit"));
  for (const o of r) {
    if (l.has(o.role)) continue;
    const u = await s(o);
    l.set(o.role, { component: u, atom: o });
  }
  return ie.set(c, i), Me.set(c, l), { manifest: i, components: l };
}
const ut = 1e3, ft = 1e4, at = 1.7;
class dt extends ze {
  constructor(e) {
    if (super(), this.socket = null, this.reconnectTimer = null, this.subscriptions = /* @__PURE__ */ new Map(), this.outboundQueue = [], this.handleOpen = () => {
      this.emit("open"), this.reconnectDelay = this.options.reconnectDelay, this.flushQueue();
      for (const n of this.subscriptions.keys())
        this.enqueue({ action: "subscribe", channel: n });
    }, this.handleMessage = (n) => {
      try {
        const s = JSON.parse(String(n.data));
        if (!s || typeof s != "object" || !("channel" in s)) {
          this.emit("raw", s);
          return;
        }
        const i = String(s.channel ?? "");
        if (!i) return;
        this.emit("message", s);
        const c = this.subscriptions.get(i);
        if (!c) return;
        const l = {
          channel: i,
          payload: s.payload,
          ...s
        };
        for (const r of c)
          r(l);
      } catch (s) {
        this.emit("error", s);
      }
    }, this.handleClose = () => {
      this.emit("close"), this.scheduleReconnect();
    }, this.handleError = (n) => {
      this.emit("error", n);
    }, !e.url)
      throw new Error("WSMuxClient requires a url");
    this.options = {
      protocols: e.protocols ?? [],
      reconnectDelay: e.reconnectDelay ?? ut,
      maxReconnectDelay: e.maxReconnectDelay ?? ft,
      backoffFactor: e.backoffFactor ?? at,
      url: e.url
    }, this.reconnectDelay = this.options.reconnectDelay;
  }
  connect() {
    this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) || (this.clearReconnect(), this.socket = new WebSocket(this.options.url, this.options.protocols), this.socket.addEventListener("open", this.handleOpen), this.socket.addEventListener("message", this.handleMessage), this.socket.addEventListener("close", this.handleClose), this.socket.addEventListener("error", this.handleError));
  }
  disconnect() {
    this.clearReconnect(), this.socket && (this.socket.removeEventListener("open", this.handleOpen), this.socket.removeEventListener("message", this.handleMessage), this.socket.removeEventListener("close", this.handleClose), this.socket.removeEventListener("error", this.handleError), this.socket.close(), this.socket = null);
  }
  subscribe(e, n) {
    return this.subscriptions.has(e) || (this.subscriptions.set(e, /* @__PURE__ */ new Set()), this.enqueue({ action: "subscribe", channel: e })), this.subscriptions.get(e).add(n), this.connect(), () => {
      const i = this.subscriptions.get(e);
      i && (i.delete(n), i.size === 0 && (this.subscriptions.delete(e), this.enqueue({ action: "unsubscribe", channel: e })));
    };
  }
  publish(e, n) {
    this.enqueue({ action: "publish", channel: e, payload: n });
  }
  enqueue(e) {
    this.socket && this.socket.readyState === WebSocket.OPEN ? this.socket.send(JSON.stringify(e)) : (this.outboundQueue.push(e), this.connect());
  }
  flushQueue() {
    var e;
    for (; this.outboundQueue.length; ) {
      const n = this.outboundQueue.shift();
      n && ((e = this.socket) == null || e.send(JSON.stringify(n)));
    }
  }
  scheduleReconnect() {
    this.clearReconnect(), this.reconnectTimer = setTimeout(() => {
      this.connect(), this.reconnectDelay = Math.min(
        this.reconnectDelay * this.options.backoffFactor,
        this.options.maxReconnectDelay
      );
    }, this.reconnectDelay);
  }
  clearReconnect() {
    this.reconnectTimer && (clearTimeout(this.reconnectTimer), this.reconnectTimer = null);
  }
}
function ht(t) {
  const e = new dt({ url: t.muxUrl, protocols: t.protocols });
  return e.connect(), {
    client: e,
    channels: t.manifest.channels ?? []
  };
}
function It(t, e, n) {
  const s = t.client.subscribe(e, n);
  return {
    publish: (i) => t.client.publish(e, i),
    unsubscribe: s
  };
}
async function jt(t) {
  const { manifest: e, components: n } = await lt(t.manifestUrl), s = t.muxUrl ? ht({
    manifest: e,
    muxUrl: t.muxUrl,
    protocols: t.muxProtocols
  }) : void 0, i = R(e), c = R(n), l = O(i, (r) => r.tiles ?? []);
  return {
    manifest: i,
    tiles: l,
    components: c,
    mux: s
  };
}
typeof window < "u" && (window.__svelte || (window.__svelte = { v: /* @__PURE__ */ new Set() })).v.add(st);
const Ke = Symbol("layout-engine:manifest"), Qe = Symbol("layout-engine:registry"), _t = Symbol("layout-engine:mux");
function mt(t) {
  ne(Ke, t.manifest), ne(Qe, t.registry), t.mux && ne(_t, t.mux);
}
function ge() {
  const t = Te(Ke);
  if (!t)
    throw new Error("Layout manifest store not found; wrap content in LayoutEngineProvider.");
  return t;
}
function pt() {
  const t = Te(Qe);
  if (!t)
    throw new Error("Atom registry store not found; wrap content in LayoutEngineProvider.");
  return t;
}
function gt(t) {
  let e;
  const n = (
    /*#slots*/
    t[4].default
  ), s = fe(
    n,
    t,
    /*$$scope*/
    t[3],
    null
  );
  return {
    c() {
      s && s.c();
    },
    m(i, c) {
      s && s.m(i, c), e = !0;
    },
    p(i, [c]) {
      s && s.p && (!e || c & /*$$scope*/
      8) && de(
        s,
        n,
        i,
        /*$$scope*/
        i[3],
        e ? ae(
          n,
          /*$$scope*/
          i[3],
          c,
          null
        ) : he(
          /*$$scope*/
          i[3]
        ),
        null
      );
    },
    i(i) {
      e || (w(s, i), e = !0);
    },
    o(i) {
      v(s, i), e = !1;
    },
    d(i) {
      s && s.d(i);
    }
  };
}
function yt(t, e, n) {
  let { $$slots: s = {}, $$scope: i } = e, { manifest: c } = e, { registry: l } = e, { mux: r = void 0 } = e;
  return mt({ manifest: c, registry: l, mux: r }), t.$$set = (o) => {
    "manifest" in o && n(0, c = o.manifest), "registry" in o && n(1, l = o.registry), "mux" in o && n(2, r = o.mux), "$$scope" in o && n(3, i = o.$$scope);
  }, [c, l, r, i, s];
}
class Ut extends V {
  constructor(e) {
    super(), H(this, e, yt, gt, T, { manifest: 0, registry: 1, mux: 2 });
  }
}
function Pe(t, e, n) {
  const s = t.slice();
  return s[10] = e[n], s;
}
function bt(t) {
  return {
    c: p,
    m: p,
    p,
    i: p,
    o: p,
    d: p
  };
}
function wt(t) {
  let e = (
    /*tile*/
    t[10].id
  ), n, s, i = Ne(t);
  return {
    c() {
      i.c(), n = U();
    },
    m(c, l) {
      i.m(c, l), b(c, n, l), s = !0;
    },
    p(c, l) {
      l & /*$tiles*/
      4 && T(e, e = /*tile*/
      c[10].id) ? (J(), v(i, 1, 1, p), G(), i = Ne(c), i.c(), w(i, 1), i.m(n.parentNode, n)) : i.p(c, l);
    },
    i(c) {
      s || (w(i), s = !0);
    },
    o(c) {
      v(i), s = !1;
    },
    d(c) {
      c && y(n), i.d(c);
    }
  };
}
function Ne(t) {
  var u;
  let e, n, s, i, c;
  const l = [
    /*tile*/
    t[10].props
  ];
  var r = (
    /*$registry*/
    (u = t[3].get(
      /*tile*/
      t[10].role
    )) == null ? void 0 : u.component
  );
  function o(h, a) {
    let _ = {};
    for (let f = 0; f < l.length; f += 1)
      _ = oe(_, l[f]);
    return a !== void 0 && a & /*$tiles*/
    4 && (_ = oe(_, $e(l, [Le(
      /*tile*/
      h[10].props
    )]))), { props: _ };
  }
  return r && (n = ke(r, o(t))), {
    c() {
      e = F("div"), n && le(n.$$.fragment), s = _e(), L(e, "class", "layout-engine-tile"), L(e, "style", i = /*frameStyle*/
      t[8](
        /*tile*/
        t[10].frame
      ));
    },
    m(h, a) {
      b(h, e, a), n && B(n, e, null), Q(e, s), c = !0;
    },
    p(h, a) {
      var _;
      if (a & /*$registry, $tiles*/
      12 && r !== (r = /*$registry*/
      (_ = h[3].get(
        /*tile*/
        h[10].role
      )) == null ? void 0 : _.component)) {
        if (n) {
          J();
          const f = n;
          v(f.$$.fragment, 1, 0, () => {
            z(f, 1);
          }), G();
        }
        r ? (n = ke(r, o(h, a)), le(n.$$.fragment), w(n.$$.fragment, 1), B(n, e, s)) : n = null;
      } else if (r) {
        const f = a & /*$tiles*/
        4 ? $e(l, [Le(
          /*tile*/
          h[10].props
        )]) : {};
        n.$set(f);
      }
      (!c || a & /*$tiles*/
      4 && i !== (i = /*frameStyle*/
      h[8](
        /*tile*/
        h[10].frame
      ))) && L(e, "style", i);
    },
    i(h) {
      c || (n && w(n.$$.fragment, h), c = !0);
    },
    o(h) {
      n && v(n.$$.fragment, h), c = !1;
    },
    d(h) {
      h && y(e), n && z(n);
    }
  };
}
function Ce(t, e) {
  let n, s, i, c, l, r;
  const o = [wt, bt], u = [];
  function h(a, _) {
    return _ & /*$registry, $tiles*/
    12 && (s = null), s == null && (s = !!/*$registry*/
    a[3].get(
      /*tile*/
      a[10].role
    )), s ? 0 : 1;
  }
  return i = h(e, -1), c = u[i] = o[i](e), {
    key: t,
    first: null,
    c() {
      n = U(), c.c(), l = U(), this.first = n;
    },
    m(a, _) {
      b(a, n, _), u[i].m(a, _), b(a, l, _), r = !0;
    },
    p(a, _) {
      e = a;
      let f = i;
      i = h(e, _), i === f ? u[i].p(e, _) : (J(), v(u[f], 1, 1, () => {
        u[f] = null;
      }), G(), c = u[i], c ? c.p(e, _) : (c = u[i] = o[i](e), c.c()), w(c, 1), c.m(l.parentNode, l));
    },
    i(a) {
      r || (w(c), r = !0);
    },
    o(a) {
      v(c), r = !1;
    },
    d(a) {
      a && (y(n), y(l)), u[i].d(a);
    }
  };
}
function vt(t) {
  let e, n = [], s = /* @__PURE__ */ new Map(), i, c = x(
    /*$tiles*/
    t[2]
  );
  const l = (r) => (
    /*tile*/
    r[10].id
  );
  for (let r = 0; r < c.length; r += 1) {
    let o = Pe(t, c, r), u = l(o);
    s.set(u, n[r] = Ce(u, o));
  }
  return {
    c() {
      e = F("div");
      for (let r = 0; r < n.length; r += 1)
        n[r].c();
      L(e, "class", "layout-engine-view"), I(e, "position", "relative"), I(
        e,
        "width",
        /*$viewportWidth*/
        t[0]
      ), I(
        e,
        "min-height",
        /*$viewportHeight*/
        t[1]
      );
    },
    m(r, o) {
      b(r, e, o);
      for (let u = 0; u < n.length; u += 1)
        n[u] && n[u].m(e, null);
      i = !0;
    },
    p(r, [o]) {
      o & /*$tiles, frameStyle, $registry*/
      268 && (c = x(
        /*$tiles*/
        r[2]
      ), J(), n = We(n, o, l, 1, r, c, s, e, tt, Ce, null, Pe), G()), (!i || o & /*$viewportWidth*/
      1) && I(
        e,
        "width",
        /*$viewportWidth*/
        r[0]
      ), (!i || o & /*$viewportHeight*/
      2) && I(
        e,
        "min-height",
        /*$viewportHeight*/
        r[1]
      );
    },
    i(r) {
      if (!i) {
        for (let o = 0; o < c.length; o += 1)
          w(n[o]);
        i = !0;
      }
    },
    o(r) {
      for (let o = 0; o < n.length; o += 1)
        v(n[o]);
      i = !1;
    },
    d(r) {
      r && y(e);
      for (let o = 0; o < n.length; o += 1)
        n[o].d();
    }
  };
}
function kt(t, e, n) {
  let s, i, c, l;
  const r = ge(), o = pt();
  $(t, o, (f) => n(3, l = f));
  const u = O(r, (f) => f.tiles ?? []);
  $(t, u, (f) => n(2, c = f));
  const h = O(r, (f) => {
    var d;
    return (d = f.viewport) != null && d.width ? `${f.viewport.width}px` : "100%";
  });
  $(t, h, (f) => n(0, s = f));
  const a = O(r, (f) => {
    var d;
    return (d = f.viewport) != null && d.height ? `${f.viewport.height}px` : "auto";
  });
  return $(t, a, (f) => n(1, i = f)), [
    s,
    i,
    c,
    l,
    o,
    u,
    h,
    a,
    (f) => f ? `
      position:absolute;
      left:${f.x}px;
      top:${f.y}px;
      width:${f.w}px;
      height:${f.h}px;
      box-sizing:border-box;
      padding:12px;
      display:flex;
    ` : ""
  ];
}
class Et extends V {
  constructor(e) {
    super(), H(this, e, kt, vt, T, {});
  }
}
function St(t) {
  const e = t.site;
  return e ? {
    pages: Array.isArray(e.pages) ? e.pages.map((s) => ({
      id: String((s == null ? void 0 : s.id) ?? ""),
      route: String((s == null ? void 0 : s.route) ?? "/"),
      title: s != null && s.title ? String(s.title) : void 0,
      slots: Array.isArray(s == null ? void 0 : s.slots) ? s == null ? void 0 : s.slots : void 0,
      meta: (s == null ? void 0 : s.meta) ?? void 0
    })) : [],
    activePageId: e.active_page ?? (e == null ? void 0 : e.activePage),
    basePath: e.navigation && typeof e.navigation == "object" ? e.navigation.base_path : void 0
  } : { pages: [], activePageId: null, basePath: void 0 };
}
function Ye(t) {
  const e = R([]), n = R(null), s = R(void 0);
  return t.subscribe((c) => {
    const l = St(c);
    e.set(l.pages), n.set(l.activePageId ?? null), s.set(l.basePath);
  }), {
    pages: e,
    activePageId: n,
    basePath: s,
    navigate: (c) => {
      let l = null;
      return e.update((r) => {
        const o = r.find((u) => u.id === c);
        return o && (l = o.route), r;
      }), l && n.set(c), l;
    }
  };
}
function Ae(t, e, n) {
  const s = t.slice();
  return s[11] = e[n], s;
}
const $t = (t) => ({}), De = (t) => ({
  navigation: (
    /*navigation*/
    t[3]
  ),
  manifest: (
    /*manifest*/
    t[2]
  )
});
function Re(t) {
  let e, n = [], s = /* @__PURE__ */ new Map(), i = x(
    /*$pages*/
    t[0]
  );
  const c = (l) => (
    /*page*/
    l[11].id
  );
  for (let l = 0; l < i.length; l += 1) {
    let r = Ae(t, i, l), o = c(r);
    s.set(o, n[l] = Oe(o, r));
  }
  return {
    c() {
      e = F("nav");
      for (let l = 0; l < n.length; l += 1)
        n[l].c();
      L(e, "class", "layout-engine-shell__nav svelte-14fdevm");
    },
    m(l, r) {
      b(l, e, r);
      for (let o = 0; o < n.length; o += 1)
        n[o] && n[o].m(e, null);
    },
    p(l, r) {
      r & /*$pages, $activePage, handleNavigate*/
      67 && (i = x(
        /*$pages*/
        l[0]
      ), n = We(n, r, c, 1, l, i, s, e, et, Oe, null, Ae));
    },
    d(l) {
      l && y(e);
      for (let r = 0; r < n.length; r += 1)
        n[r].d();
    }
  };
}
function Oe(t, e) {
  let n, s = (
    /*page*/
    (e[11].title ?? /*page*/
    e[11].id) + ""
  ), i, c, l, r;
  function o() {
    return (
      /*click_handler*/
      e[9](
        /*page*/
        e[11]
      )
    );
  }
  return {
    key: t,
    first: null,
    c() {
      var u;
      n = F("button"), i = q(s), c = _e(), L(n, "type", "button"), L(n, "class", "svelte-14fdevm"), Y(
        n,
        "selected",
        /*page*/
        e[11].id === /*$activePage*/
        ((u = e[1]) == null ? void 0 : u.id)
      ), this.first = n;
    },
    m(u, h) {
      b(u, n, h), Q(n, i), Q(n, c), l || (r = Ue(n, "click", o), l = !0);
    },
    p(u, h) {
      var a;
      e = u, h & /*$pages*/
      1 && s !== (s = /*page*/
      (e[11].title ?? /*page*/
      e[11].id) + "") && me(i, s), h & /*$pages, $activePage*/
      3 && Y(
        n,
        "selected",
        /*page*/
        e[11].id === /*$activePage*/
        ((a = e[1]) == null ? void 0 : a.id)
      );
    },
    d(u) {
      u && y(n), l = !1, r();
    }
  };
}
function Lt(t) {
  let e, n = (
    /*$pages*/
    t[0].length && Re(t)
  );
  return {
    c() {
      n && n.c(), e = U();
    },
    m(s, i) {
      n && n.m(s, i), b(s, e, i);
    },
    p(s, i) {
      /*$pages*/
      s[0].length ? n ? n.p(s, i) : (n = Re(s), n.c(), n.m(e.parentNode, e)) : n && (n.d(1), n = null);
    },
    d(s) {
      s && y(e), n && n.d(s);
    }
  };
}
function Mt(t) {
  let e, n, s, i;
  const c = (
    /*#slots*/
    t[8].default
  ), l = fe(
    c,
    t,
    /*$$scope*/
    t[7],
    De
  ), r = l || Lt(t);
  return s = new Et({}), {
    c() {
      e = F("div"), r && r.c(), n = _e(), le(s.$$.fragment), L(e, "class", "layout-engine-shell");
    },
    m(o, u) {
      b(o, e, u), r && r.m(e, null), Q(e, n), B(s, e, null), i = !0;
    },
    p(o, [u]) {
      l ? l.p && (!i || u & /*$$scope*/
      128) && de(
        l,
        c,
        o,
        /*$$scope*/
        o[7],
        i ? ae(
          c,
          /*$$scope*/
          o[7],
          u,
          $t
        ) : he(
          /*$$scope*/
          o[7]
        ),
        De
      ) : r && r.p && (!i || u & /*$pages, $activePage*/
      3) && r.p(o, i ? u : -1);
    },
    i(o) {
      i || (w(r, o), w(s.$$.fragment, o), i = !0);
    },
    o(o) {
      v(r, o), v(s.$$.fragment, o), i = !1;
    },
    d(o) {
      o && y(e), r && r.d(o), z(s);
    }
  };
}
function Pt(t, e, n) {
  let s, i, { $$slots: c = {}, $$scope: l } = e;
  const r = ge(), o = Ye(r), u = o.pages;
  $(t, u, (d) => n(0, s = d));
  const h = o.activePageId, a = O([u, h], ([d, g]) => d.find((S) => S.id === g) ?? null);
  $(t, a, (d) => n(1, i = d));
  const _ = (d) => {
    const g = o.navigate(d);
    g && typeof window < "u" && window.history.pushState({}, "", g), typeof window < "u" && window.dispatchEvent(new CustomEvent("layout-engine:navigate", { detail: { pageId: d } }));
  }, f = (d) => _(d.id);
  return t.$$set = (d) => {
    "$$scope" in d && n(7, l = d.$$scope);
  }, [
    s,
    i,
    r,
    o,
    u,
    a,
    _,
    l,
    c,
    f
  ];
}
class qt extends V {
  constructor(e) {
    super(), H(this, e, Pt, Mt, T, {});
  }
}
function Nt(t) {
  let e;
  return {
    c() {
      e = q(
        /*pageId*/
        t[0]
      );
    },
    m(n, s) {
      b(n, e, s);
    },
    p(n, s) {
      s & /*pageId*/
      1 && me(
        e,
        /*pageId*/
        n[0]
      );
    },
    d(n) {
      n && y(e);
    }
  };
}
function Ct(t) {
  let e = (
    /*$page*/
    (t[2].title ?? /*pageId*/
    t[0]) + ""
  ), n;
  return {
    c() {
      n = q(e);
    },
    m(s, i) {
      b(s, n, i);
    },
    p(s, i) {
      i & /*$page, pageId*/
      5 && e !== (e = /*$page*/
      (s[2].title ?? /*pageId*/
      s[0]) + "") && me(n, e);
    },
    d(s) {
      s && y(n);
    }
  };
}
function At(t) {
  let e;
  function n(c, l) {
    return (
      /*$page*/
      c[2] ? Ct : Nt
    );
  }
  let s = n(t), i = s(t);
  return {
    c() {
      i.c(), e = U();
    },
    m(c, l) {
      i.m(c, l), b(c, e, l);
    },
    p(c, l) {
      s === (s = n(c)) && i ? i.p(c, l) : (i.d(1), i = s(c), i && (i.c(), i.m(e.parentNode, e)));
    },
    d(c) {
      c && y(e), i.d(c);
    }
  };
}
function Dt(t) {
  let e, n, s, i;
  const c = (
    /*#slots*/
    t[7].default
  ), l = fe(
    c,
    t,
    /*$$scope*/
    t[6],
    null
  ), r = l || At(t);
  return {
    c() {
      e = F("button"), r && r.c(), Y(
        e,
        "selected",
        /*$activePageId*/
        t[1] === /*pageId*/
        t[0]
      );
    },
    m(o, u) {
      b(o, e, u), r && r.m(e, null), n = !0, s || (i = Ue(
        e,
        "click",
        /*onClick*/
        t[5]
      ), s = !0);
    },
    p(o, [u]) {
      l ? l.p && (!n || u & /*$$scope*/
      64) && de(
        l,
        c,
        o,
        /*$$scope*/
        o[6],
        n ? ae(
          c,
          /*$$scope*/
          o[6],
          u,
          null
        ) : he(
          /*$$scope*/
          o[6]
        ),
        null
      ) : r && r.p && (!n || u & /*$page, pageId*/
      5) && r.p(o, n ? u : -1), (!n || u & /*$activePageId, pageId*/
      3) && Y(
        e,
        "selected",
        /*$activePageId*/
        o[1] === /*pageId*/
        o[0]
      );
    },
    i(o) {
      n || (w(r, o), n = !0);
    },
    o(o) {
      v(r, o), n = !1;
    },
    d(o) {
      o && y(e), r && r.d(o), s = !1, i();
    }
  };
}
function Rt(t, e, n) {
  let s, i, { $$slots: c = {}, $$scope: l } = e, { pageId: r } = e;
  const o = ge(), u = Ye(o), h = u.pages, a = u.activePageId;
  $(t, a, (d) => n(1, s = d));
  const _ = O([h], ([d]) => d.find((g) => g.id === r));
  $(t, _, (d) => n(2, i = d));
  const f = () => {
    u.navigate(r);
  };
  return t.$$set = (d) => {
    "pageId" in d && n(0, r = d.pageId), "$$scope" in d && n(6, l = d.$$scope);
  }, [r, s, i, a, _, f, l, c];
}
class Wt extends V {
  constructor(e) {
    super(), H(this, e, Rt, Dt, T, { pageId: 0 });
  }
}
export {
  Wt as LayoutEngineNavLink,
  Ut as LayoutEngineProvider,
  qt as LayoutEngineShell,
  Et as LayoutEngineView,
  dt as WSMuxClient,
  jt as createLayoutEngineApp,
  ht as createMuxContext,
  lt as loadManifest,
  It as useMux
};
