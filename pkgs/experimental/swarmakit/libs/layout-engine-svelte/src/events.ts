import type { LayoutManifest, ManifestChannel } from "./types";
import { WSMuxClient, type SubscribeHandler } from "./mux";

export type MuxContext = {
  client: WSMuxClient;
  channels: ManifestChannel[];
};

export function createMuxContext(options: {
  manifest: LayoutManifest;
  muxUrl: string;
  protocols?: string | string[];
}): MuxContext {
  const client = new WSMuxClient({ url: options.muxUrl, protocols: options.protocols });
  client.connect();
  return {
    client,
    channels: options.manifest.channels ?? [],
  };
}

export function useMux(mux: MuxContext, channelId: string, handler: SubscribeHandler) {
  const unsubscribe = mux.client.subscribe(channelId, handler);
  return {
    publish: (payload: unknown) => mux.client.publish(channelId, payload),
    unsubscribe,
  };
}
