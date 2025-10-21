function matchesPageId(page, identifier) {
  if (identifier === undefined || identifier === null) {
    return false;
  }
  const id = page?.id ?? page?.slug ?? page?.name;
  return id !== undefined && String(id) === String(identifier);
}

export function resolveManifestPage(manifest, requestedId, resolver) {
  const pages = Array.isArray(manifest?.pages) ? manifest.pages : [];
  if (!pages.length) {
    return null;
  }

  const attempt = (candidate) => {
    if (candidate === undefined || candidate === null) {
      return null;
    }
    if (typeof candidate === "string" || typeof candidate === "number") {
      return pages.find((page) => matchesPageId(page, candidate)) ?? null;
    }
    if (typeof candidate === "object") {
      if (candidate.id !== undefined || candidate.slug !== undefined) {
        return attempt(candidate.id ?? candidate.slug);
      }
      return candidate;
    }
    return null;
  };

  const fromResolver = resolver ? attempt(resolver(manifest, requestedId)) : null;
  if (fromResolver) {
    return fromResolver;
  }

  const fromRequested = attempt(requestedId);
  if (fromRequested) {
    return fromRequested;
  }

  return pages[0] ?? null;
}
