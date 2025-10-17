function normalizeUrl(urlLike, windowRef) {
  const base =
    windowRef && windowRef.location ? windowRef.location.href : "http://localhost";
  try {
    return new URL(urlLike, base).toString();
  } catch {
    return null;
  }
}

function upgradeToWebSocket(urlLike, windowRef) {
  const normalized = normalizeUrl(urlLike, windowRef);
  if (!normalized) {
    return null;
  }
  try {
    const url = new URL(normalized);
    if (url.protocol === "http:") {
      url.protocol = "ws:";
    } else if (url.protocol === "https:") {
      url.protocol = "wss:";
    }
    return url.toString();
  } catch {
    return null;
  }
}

export function deriveEventsUrl({
  manifestUrl,
  explicitUrl,
  windowRef,
} = {}) {
  const win =
    windowRef !== undefined
      ? windowRef
      : typeof window !== "undefined"
        ? window
        : null;

  // Highest precedence: explicit override then global override.
  const preferred = explicitUrl ?? win?.__LE_EVENTS_URL__ ?? null;
  if (preferred) {
    return upgradeToWebSocket(preferred, win);
  }

  const manifestSource =
    manifestUrl ??
    win?.__LE_MANIFEST_URL__ ??
    (win ? new URL("manifest.json", win.location.href).toString() : null);
  if (!manifestSource) {
    return null;
  }
  const absoluteManifest = normalizeUrl(manifestSource, win);
  if (!absoluteManifest) {
    return null;
  }

  try {
    const url = new URL(absoluteManifest);
    let path = url.pathname ?? "/";
    if (path.endsWith("manifest.json")) {
      path = path.slice(0, -"manifest.json".length);
    }
    if (!path.endsWith("/")) {
      path += "/";
    }
    path += "events";
    url.pathname = path;
    url.search = "";
    url.hash = "";
    if (url.protocol === "http:") {
      url.protocol = "ws:";
    } else if (url.protocol === "https:") {
      url.protocol = "wss:";
    }
    return url.toString();
  } catch {
    return null;
  }
}

function createHandlerRegistry() {
  return new Map();
}

function emit(registry, event, detail) {
  const bucket = registry.get(event);
  if (!bucket) {
    return;
  }
  for (const handler of bucket) {
    try {
      handler(detail);
    } catch (error) {
      console.error("[event-bridge] handler error", error);
    }
  }
}

function addHandler(registry, event, handler) {
  if (!registry.has(event)) {
    registry.set(event, new Set());
  }
  registry.get(event).add(handler);
  return () => {
    const bucket = registry.get(event);
    if (!bucket) {
      return;
    }
    bucket.delete(handler);
    if (!bucket.size) {
      registry.delete(event);
    }
  };
}

export function createEventBridge(options = {}) {
  const {
    protocols,
    autoReconnect = true,
    reconnectDelay = 2000,
    autoConnect = true,
    windowRef,
  } = options;

  const handlers = createHandlerRegistry();
  let currentUrl = options.url ?? null;
  let socket = null;
  let reconnectTimer = null;
  let disposed = false;
  let attempts = 0;

  function cleanupSocket() {
    if (!socket) {
      return;
    }
    try {
      socket.close(1000, "reconnect");
    } catch {
      // swallow errors from browsers that disallow closing here
    }
    socket = null;
  }

  function scheduleReconnect() {
    if (disposed || !autoReconnect) {
      return;
    }
    if (reconnectTimer) {
      return;
    }
    const delay =
      typeof reconnectDelay === "function"
        ? reconnectDelay(attempts)
        : reconnectDelay;
    const duration = Number.isFinite(delay) ? Math.max(0, delay) : 0;
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, duration);
  }

  function connect() {
    if (disposed || !currentUrl) {
      return;
    }
    if (typeof WebSocket === "undefined") {
      emit(handlers, "error", new Error("WebSocket is not available in this environment"));
      return;
    }
    if (socket) {
      const ready = socket.readyState;
      if (ready === WebSocket.OPEN || ready === WebSocket.CONNECTING) {
        return;
      }
    }
    cleanupSocket();

    const targetUrl = currentUrl;
    let ws;
    try {
      if (protocols !== undefined) {
        ws = new WebSocket(targetUrl, protocols);
      } else {
        ws = new WebSocket(targetUrl);
      }
    } catch (error) {
      emit(handlers, "error", error);
      scheduleReconnect();
      return;
    }

    socket = ws;
    attempts += 1;
    emit(handlers, "status", {
      type: "connecting",
      url: targetUrl,
      attempts,
    });

    ws.addEventListener("open", () => {
      attempts = 0;
      emit(handlers, "open", { url: targetUrl });
      emit(handlers, "status", { type: "open", url: targetUrl });
    });

    ws.addEventListener("message", (event) => {
      emit(handlers, "message", event);
    });

    ws.addEventListener("error", (event) => {
      emit(handlers, "error", event);
    });

    ws.addEventListener("close", (event) => {
      socket = null;
      emit(handlers, "close", event);
      emit(handlers, "status", {
        type: "closed",
        url: targetUrl,
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
      });
      scheduleReconnect();
    });
  }

  function close(code = 1000, reason = "client close") {
    disposed = true;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (socket) {
      try {
        socket.close(code, reason);
      } catch {
        // ignore close errors
      }
      socket = null;
    }
  }

  function send(payload) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return false;
    }
    socket.send(payload);
    return true;
  }

  function setUrl(url, { reconnect = true } = {}) {
    currentUrl = url ? upgradeToWebSocket(url, windowRef) ?? url : null;
    emit(handlers, "status", { type: "url", url: currentUrl });
    cleanupSocket();
    if (reconnect && currentUrl) {
      connect();
    }
  }

  function on(event, handler) {
    return addHandler(handlers, event, handler);
  }

  if (currentUrl) {
    currentUrl = upgradeToWebSocket(currentUrl, windowRef) ?? currentUrl;
  }
  if (autoConnect && currentUrl) {
    setTimeout(connect, 0);
  }

  return {
    connect,
    close,
    send,
    on,
    setUrl,
    getUrl() {
      return currentUrl;
    },
  };
}

export default createEventBridge;
