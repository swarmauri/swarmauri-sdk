export function normalizeTheme(input = {}) {
  if (!input) {
    return { className: "", style: {}, tokens: {} };
  }
  return {
    className: input.className ?? "",
    style: { ...(input.style ?? {}) },
    tokens: { ...(input.tokens ?? {}) },
  };
}

export function mergeTheme(base, patch) {
  const output = normalizeTheme(base);
  if (!patch) {
    return output;
  }
  const addition = normalizeTheme(patch);
  if (addition.className) {
    output.className = [output.className, addition.className]
      .filter(Boolean)
      .join(" ");
  }
  Object.assign(output.style, addition.style);
  Object.assign(output.tokens, addition.tokens);
  return output;
}

function cloneTheme(theme) {
  return {
    className: theme.className,
    style: { ...theme.style },
    tokens: { ...theme.tokens },
  };
}

export function createThemeController(initialTheme) {
  let base = normalizeTheme(initialTheme);
  const state = cloneTheme(base);

  function reset(nextBase = base) {
    base = normalizeTheme(nextBase);
    state.className = base.className;

    for (const key of Object.keys(state.style)) {
      delete state.style[key];
    }
    Object.assign(state.style, base.style);

    for (const key of Object.keys(state.tokens)) {
      delete state.tokens[key];
    }
    Object.assign(state.tokens, base.tokens);
    return state;
  }

  function apply(patch, { replace = false } = {}) {
    if (replace || patch?.reset) {
      reset();
    }
    if (!patch) {
      return state;
    }
    const normalized = normalizeTheme(patch);
    if (normalized.className !== undefined) {
      state.className = normalized.className ?? "";
    }
    Object.assign(state.style, normalized.style);
    Object.assign(state.tokens, normalized.tokens);
    return state;
  }

  function setBase(nextBase) {
    base = normalizeTheme(nextBase);
    reset(base);
    return state;
  }

  reset(base);

  return {
    state,
    apply,
    reset,
    setBase,
  };
}
