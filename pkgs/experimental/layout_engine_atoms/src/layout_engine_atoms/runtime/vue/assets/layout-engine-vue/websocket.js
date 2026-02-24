// WebSocket Multiplexer Module
// Extracted from index.js for better modularity

import EventEmitter from "eventemitter3";
import { onBeforeUnmount } from "vue";

// Constants
const DEFAULT_RECONNECT_DELAY = 1e3;
const DEFAULT_MAX_DELAY = 1e4;
const DEFAULT_BACKOFF = 1.7;

/**
 * WebSocket Multiplexer Client
 * Manages WebSocket connections with auto-reconnection and pub/sub channels
 */
class WSMuxClient extends EventEmitter {
  constructor(options) {
    super();
    this.socket = null;
    this.reconnectTimer = null;
    this.subscriptions = /* @__PURE__ */ new Map();
    this.pendingSubscribes = /* @__PURE__ */ new Set();
    this.outboundQueue = [];
    this.handleOpen = () => {
      this.emit("open");
      this.reconnectDelay = this.options.reconnectDelay;
      while (this.outboundQueue.length) {
        const message = this.outboundQueue.shift();
        if (message) {
          this.socket?.send(JSON.stringify(message));
        }
      }
      this.flushSubscribes();
    };
    this.handleMessage = (event) => {
      try {
        const data = JSON.parse(String(event.data));
        if (!data || typeof data !== "object" || !("channel" in data)) {
          this.emit("raw", data);
          return;
        }
        const channelId = String(data["channel"] ?? "");
        if (!channelId) return;
        this.emit("message", data);
        const handlers = this.subscriptions.get(channelId);
        if (!handlers) return;
        const message = {
          channel: channelId,
          payload: data["payload"],
          ...data
        };
        for (const handler of handlers) {
          handler(message);
        }
      } catch (err) {
        this.emit("error", err);
      }
    };
    this.handleClose = () => {
      this.emit("close");
      this.scheduleReconnect();
    };
    this.handleError = (event) => {
      this.emit("error", event);
    };
    if (!options.url) {
      throw new Error("WSMuxClient requires a url");
    }
    this.options = {
      protocols: options.protocols ?? [],
      reconnectDelay: options.reconnectDelay ?? DEFAULT_RECONNECT_DELAY,
      maxReconnectDelay: options.maxReconnectDelay ?? DEFAULT_MAX_DELAY,
      backoffFactor: options.backoffFactor ?? DEFAULT_BACKOFF,
      url: options.url
    };
    this.reconnectDelay = this.options.reconnectDelay;
  }
  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }
    this.clearReconnect();
    this.socket = new WebSocket(this.options.url, this.options.protocols);
    this.socket.addEventListener("open", this.handleOpen);
    this.socket.addEventListener("message", this.handleMessage);
    this.socket.addEventListener("close", this.handleClose);
    this.socket.addEventListener("error", this.handleError);
  }
  disconnect() {
    this.clearReconnect();
    if (this.socket) {
      this.socket.removeEventListener("open", this.handleOpen);
      this.socket.removeEventListener("message", this.handleMessage);
      this.socket.removeEventListener("close", this.handleClose);
      this.socket.removeEventListener("error", this.handleError);
      this.socket.close();
      this.socket = null;
    }
  }
  subscribe(channelId, handler) {
    if (!this.subscriptions.has(channelId)) {
      this.subscriptions.set(channelId, /* @__PURE__ */ new Set());
      this.enqueueSubscribe(channelId);
    }
    const set = this.subscriptions.get(channelId);
    set.add(handler);
    this.connect();
    return () => {
      const group = this.subscriptions.get(channelId);
      if (!group) return;
      group.delete(handler);
      if (group.size === 0) {
        this.subscriptions.delete(channelId);
        this.enqueueUnsubscribe(channelId);
      }
    };
  }
  publish(channelId, payload) {
    this.send({ action: "publish", channel: channelId, payload });
  }
  enqueueSubscribe(channelId) {
    this.pendingSubscribes.add(channelId);
    this.send({ action: "subscribe", channel: channelId });
  }
  enqueueUnsubscribe(channelId) {
    this.send({ action: "unsubscribe", channel: channelId });
  }
  flushSubscribes() {
    for (const channelId of this.subscriptions.keys()) {
      this.send({ action: "subscribe", channel: channelId });
    }
    this.pendingSubscribes.clear();
  }
  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      this.outboundQueue.push(message);
      this.connect();
    }
  }
  scheduleReconnect() {
    this.clearReconnect();
    this.reconnectTimer = setTimeout(() => {
      this.connect();
      this.reconnectDelay = Math.min(
        this.reconnectDelay * this.options.backoffFactor,
        this.options.maxReconnectDelay
      );
    }, this.reconnectDelay);
  }
  clearReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

// Mux context and composables
const muxKey = Symbol("layout-engine:mux");

function createMuxContext(options) {
  const client = new WSMuxClient({ url: options.muxUrl, protocols: options.protocols });
  client.connect();
  return {
    client,
    channels: options.manifest.channels ?? []
  };
}

function useMux(mux, channelId, handler) {
  const unsubscribe = mux.client.subscribe(channelId, handler);
  onBeforeUnmount(() => unsubscribe());
  return {
    publish: (payload) => mux.client.publish(channelId, payload)
  };
}

// Exports
export { WSMuxClient, createMuxContext, useMux, muxKey };
