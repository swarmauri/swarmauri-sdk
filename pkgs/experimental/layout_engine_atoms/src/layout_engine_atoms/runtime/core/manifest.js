export function manifestFromPayload(payload) {
  if (!payload || typeof payload !== "object") {
    return null;
  }
  if (payload.manifest && typeof payload.manifest === "object") {
    return payload.manifest;
  }
  if (payload.kind === "layout_manifest") {
    return payload;
  }
  if (
    payload.payload &&
    typeof payload.payload === "object" &&
    payload.payload.kind === "layout_manifest"
  ) {
    return payload.payload;
  }
  return null;
}
