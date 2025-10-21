export function isPlainObject(value) {
  if (Object.prototype.toString.call(value) !== "[object Object]") {
    return false;
  }
  const proto = Object.getPrototypeOf(value);
  return proto === null || proto === Object.prototype;
}

function clone(value) {
  if (Array.isArray(value)) {
    return value.map(clone);
  }
  if (isPlainObject(value)) {
    const result = {};
    for (const [key, nested] of Object.entries(value)) {
      result[key] = clone(nested);
    }
    return result;
  }
  return value;
}

export function deepMerge(target, patch) {
  if (!isPlainObject(target)) {
    return clone(patch);
  }
  if (!isPlainObject(patch)) {
    return clone(patch);
  }
  const result = { ...target };
  for (const [key, value] of Object.entries(patch)) {
    const existing = result[key];
    if (Array.isArray(value)) {
      result[key] = value.map((item) => clone(item));
    } else if (isPlainObject(value) && isPlainObject(existing)) {
      result[key] = deepMerge(existing, value);
    } else {
      result[key] = clone(value);
    }
  }
  return result;
}
