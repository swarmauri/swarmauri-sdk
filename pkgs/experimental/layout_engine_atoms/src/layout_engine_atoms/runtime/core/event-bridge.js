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

export function deriveEventsUrl({ manifestUrl, explicitUrl, windowRef } = {}) {
  const win =
    windowRef !== undefined
      ? windowRef
      : typeof window !== "undefined"
        ? window
        : null;

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
      // ignore
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

    ws.onopen = () => {
      attempts = 0;
      emit(handlers, "open", { url: targetUrl });
      emit(handlers, "status", { type: "open", url: targetUrl });
    };

    ws.onerror = (event) => {
      emit(handlers, "error", event instanceof Event ? new Error("WebSocket error") : event);
    };

    ws.onclose = (event) => {
      emit(handlers, "close", event);
      emit(handlers, "status", { type: "closed", url: targetUrl, event });
      socket = null;
      scheduleReconnect();
    };

    ws.onmessage = (event) => {
      emit(handlers, "message", event.data);
    };
  }

  function disconnect() {
    cleanupSocket();
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  }

  function setUrl(url) {
    currentUrl = url ?? null;
  }

  function dispose() {
    disposed = true;
    disconnect();
    handlers.clear();
  }

  function send(data) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return false;
    }
    try {
      socket.send(data);
      return true;
    } catch (error) {
      emit(handlers, "error", error);
      return false;
    }
  }

  function on(event, handler) {
    return addHandler(handlers, event, handler);
  }

  if (autoConnect && options.url) {
    setUrl(options.url);
    connect();
  }

  return {
    connect() {
      if (!currentUrl) {
        currentUrl = options.url ?? null;
      }
      if (!currentUrl) {
        emit(handlers, "error", new Error("WebSocket URL is not set"));
        return;
      }
      connect();
    },
    disconnect,
    dispose,
    reconnect() {
      disconnect();
      connect();
    },
    setUrl,
    setProtocols(nextProtocols) {
      options.protocols = nextProtocols;
    },
    on,
    off(event, handler) {
      handlers.get(event)?.delete(handler);
    },
    send,
    get url() {
      return currentUrl;
    },
    get connected() {
      return socket?.readyState === WebSocket.OPEN;
    },
  };
}
