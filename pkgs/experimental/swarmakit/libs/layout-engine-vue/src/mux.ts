import EventEmitter from "eventemitter3";

export type MuxMessage = {
  channel: string;
  payload?: unknown;
  [key: string]: unknown;
};

export type SubscribeHandler = (message: MuxMessage) => void;

export type MuxClientOptions = {
  url: string;
  protocols?: string | string[];
  reconnectDelay?: number;
  maxReconnectDelay?: number;
  backoffFactor?: number;
};

const DEFAULT_RECONNECT_DELAY = 1000;
const DEFAULT_MAX_DELAY = 10000;
const DEFAULT_BACKOFF = 1.7;

export class WSMuxClient extends EventEmitter {
  private socket: WebSocket | null = null;
  private readonly options: Required<MuxClientOptions>;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly subscriptions = new Map<string, Set<SubscribeHandler>>();
  private readonly pendingSubscribes = new Set<string>();
  private readonly outboundQueue: Array<Record<string, unknown>> = [];
  private reconnectDelay: number;

  constructor(options: MuxClientOptions) {
    super();
    if (!options.url) {
      throw new Error("WSMuxClient requires a url");
    }
    this.options = {
      protocols: options.protocols ?? [],
      reconnectDelay: options.reconnectDelay ?? DEFAULT_RECONNECT_DELAY,
      maxReconnectDelay: options.maxReconnectDelay ?? DEFAULT_MAX_DELAY,
      backoffFactor: options.backoffFactor ?? DEFAULT_BACKOFF,
      url: options.url,
    };
    this.reconnectDelay = this.options.reconnectDelay;
  }

  connect(): void {
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

  disconnect(): void {
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

  subscribe(channelId: string, handler: SubscribeHandler): () => void {
    if (!this.subscriptions.has(channelId)) {
      this.subscriptions.set(channelId, new Set());
      this.enqueueSubscribe(channelId);
    }
    const set = this.subscriptions.get(channelId)!;
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

  publish(channelId: string, payload: unknown): void {
    this.send({ action: "publish", channel: channelId, payload });
  }

  private enqueueSubscribe(channelId: string) {
    this.pendingSubscribes.add(channelId);
    this.send({ action: "subscribe", channel: channelId });
  }

  private enqueueUnsubscribe(channelId: string) {
    this.send({ action: "unsubscribe", channel: channelId });
  }

  private flushSubscribes() {
    for (const channelId of this.subscriptions.keys()) {
      this.send({ action: "subscribe", channel: channelId });
    }
    this.pendingSubscribes.clear();
  }

  private send(message: Record<string, unknown>) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      this.outboundQueue.push(message);
      this.connect();
    }
  }

  private handleOpen = () => {
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

  private handleMessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(String(event.data));
      if (!data || typeof data !== "object" || !("channel" in data)) {
        this.emit("raw", data);
        return;
      }
      const channelId = String((data as Record<string, unknown>)["channel"] ?? "");
      if (!channelId) return;
      this.emit("message", data);
      const handlers = this.subscriptions.get(channelId);
      if (!handlers) return;
      const message: MuxMessage = {
        channel: channelId,
        payload: (data as Record<string, unknown>)["payload"],
        ...data,
      };
      for (const handler of handlers) {
        handler(message);
      }
    } catch (err) {
      this.emit("error", err);
    }
  };

  private handleClose = () => {
    this.emit("close");
    this.scheduleReconnect();
  };

  private handleError = (event: Event) => {
    this.emit("error", event);
  };

  private scheduleReconnect() {
    this.clearReconnect();
    this.reconnectTimer = setTimeout(() => {
      this.connect();
      this.reconnectDelay = Math.min(
        this.reconnectDelay * this.options.backoffFactor,
        this.options.maxReconnectDelay
      );
    }, this.reconnectDelay);
  }

  private clearReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}
