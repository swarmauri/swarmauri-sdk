// Event Handling System Module
// Extracted from index.js for better modularity

// Event listener aliases mapping
const EVENT_LISTENER_ALIASES = {
  click: "onClick",
  primary: "onClick",
  secondary: "onClick",
  submit: "onSubmit",
  change: "onChange",
  input: "onInput",
  action: "onAction",
  select: "onSelect",
  broadcast: "onBroadcast",
  increment: "onIncrement",
  primaryaction: "onPrimaryAction",
  secondaryaction: "onSecondaryAction"
};

const DEFAULT_EVENT_METHOD = "POST";

/**
 * Ensures tile has a props object
 */
function ensureTileProps(tile) {
  if (!tile.props || typeof tile.props !== "object") {
    tile.props = {};
  }
  return tile.props;
}

/**
 * Resolves slot content from tile or props
 */
function resolveSlotContent(tile, props) {
  const label =
    (typeof props.label === "string" && props.label) ||
    (typeof tile?.props?.label === "string" && tile.props.label);
  const text =
    (typeof props.text === "string" && props.text) ||
    (typeof tile?.props?.text === "string" && tile.props.text);
  const children =
    (typeof props.children === "string" && props.children) ||
    (typeof tile?.props?.children === "string" && tile.props.children);
  return label || text || children || null;
}

/**
 * Resolves event trigger to Vue listener prop name
 */
function resolveListenerProp(trigger) {
  if (!trigger) {
    return null;
  }
  if (trigger.startsWith("on")) {
    return trigger;
  }
  const normalized = trigger.toLowerCase();
  if (EVENT_LISTENER_ALIASES[normalized]) {
    return EVENT_LISTENER_ALIASES[normalized];
  }
  const fallback = `on${normalized.charAt(0).toUpperCase()}${normalized.slice(1)}`;
  return fallback || "onClick";
}

/**
 * Ensures tile event entry exists and returns it
 */
function ensureTileEventEntry(tile, key, eventId) {
  if (!tile?.props || typeof tile.props !== "object") {
    return null;
  }
  const events = tile.props.events;
  if (!events || typeof events !== "object") {
    tile.props.events = {};
  }
  const store = tile.props.events;
  let current = store[key];
  if (!current || typeof current !== "object") {
    current = { id: eventId };
    store[key] = current;
  }
  if (!current.state) {
    current.state = {};
  }
  return current;
}

/**
 * Sets pending state for an event
 */
function setEventPendingState(tile, binding, isPending) {
  const entry = ensureTileEventEntry(tile, binding.key, binding.id);
  if (entry) {
    entry.state.pending = isPending;
    if (isPending) {
      entry.state.error = null;
    }
  }
  if (binding.loadingProp && tile?.props) {
    tile.props[binding.loadingProp] = isPending;
  }
  if (binding.disabledProp && tile?.props) {
    tile.props[binding.disabledProp] = isPending;
  }
}

/**
 * Records successful event result
 */
function recordEventResult(tile, binding, result) {
  const entry = ensureTileEventEntry(tile, binding.key, binding.id);
  if (entry) {
    entry.state.lastResult = result;
    entry.state.error = null;
  }
}

/**
 * Records event error
 */
function recordEventError(tile, binding, error) {
  const entry = ensureTileEventEntry(tile, binding.key, binding.id);
  if (entry) {
    entry.state.error = error;
  }
}

/**
 * Normalizes tile event binding
 */
function normalizeTileEventBinding(tile, key, raw, eventsContext) {
  if (!raw) return null;
  const spec = typeof raw === "string" ? { id: raw } : { ...raw };
  const eventId = spec.id ?? spec.event ?? spec.eventId ?? null;
  if (!eventId) {
    return null;
  }
  ensureTileEventEntry(tile, key, eventId);
  const descriptor = eventsContext?.describe ? eventsContext.describe(eventId) : null;
  const trigger = spec.trigger ?? spec.listener ?? key;
  const listener = resolveListenerProp(trigger);
  if (!listener) return null;
  const method = (spec.method ?? descriptor?.method ?? DEFAULT_EVENT_METHOD).toUpperCase();
  return {
    key,
    id: eventId,
    trigger,
    listener,
    method,
    payload: spec.payload ?? {},
    context: spec.context ?? {},
    stateProp: spec.stateProp ?? spec.prop ?? descriptor?.stateProp,
    loadingProp: spec.loadingProp ?? descriptor?.loadingProp,
    disabledProp: spec.disabledProp ?? descriptor?.disabledProp,
    preventDefault: spec.preventDefault ?? trigger === "submit",
    stopPropagation: spec.stopPropagation ?? false
  };
}

/**
 * Creates event handler for a tile binding
 */
function createTileEventHandler(tile, binding, eventsContext, componentProps) {
  if (!eventsContext?.invoke) {
    return null;
  }
  return async (domEvent) => {
    if (binding.preventDefault && domEvent?.preventDefault) {
      domEvent.preventDefault();
    }
    if (binding.stopPropagation && domEvent?.stopPropagation) {
      domEvent.stopPropagation();
    }
    setEventPendingState(tile, binding, true);
    try {
      const payload = { ...(binding.payload ?? {}) };
      const eventValue =
        domEvent && typeof domEvent === "object" && "detail" in domEvent
          ? domEvent.detail
          : domEvent;
      if (typeof eventValue === "boolean") {
        payload.checked = eventValue;
        if (binding.stateProp) {
          if (tile?.props) {
            tile.props[binding.stateProp] = eventValue;
          }
          if (componentProps && typeof componentProps === "object") {
            componentProps[binding.stateProp] = eventValue;
          }
        }
      } else if (
        eventValue &&
        typeof eventValue === "object" &&
        !Array.isArray(eventValue)
      ) {
        Object.assign(payload, eventValue);
        if (binding.stateProp && binding.stateProp in eventValue) {
          if (tile?.props) {
            tile.props[binding.stateProp] = eventValue[binding.stateProp];
          }
          if (componentProps && typeof componentProps === "object") {
            componentProps[binding.stateProp] = eventValue[binding.stateProp];
          }
        }
      }
      const context = {
        tileId: tile.id,
        role: tile.role,
        ...binding.context
      };
      const result = await eventsContext.invoke(binding.id, {
        method: binding.method,
        payload,
        context
      });
      recordEventResult(tile, binding, result?.body ?? result);
      return result;
    } catch (error) {
      recordEventError(tile, binding, error?.body ?? { message: error?.message ?? "Event failed" });
      throw error;
    } finally {
      setEventPendingState(tile, binding, false);
    }
  };
}

/**
 * Attaches event handlers to tile props
 */
function attachTileEventHandlers(tile, props, eventsContext) {
  if (!eventsContext || !props || typeof props !== "object") {
    return props;
  }
  const eventDefs = tile?.props?.events;
  if (!eventDefs || typeof eventDefs !== "object") {
    return props;
  }
  const handlers = {};
  for (const [key, raw] of Object.entries(eventDefs)) {
    const binding = normalizeTileEventBinding(tile, key, raw, eventsContext);
    if (!binding) continue;
    const handler = createTileEventHandler(tile, binding, eventsContext, props);
    if (handler && binding.listener) {
      handlers[binding.listener] = handler;
    }
  }
  if (Object.keys(handlers).length) {
    Object.assign(props, handlers);
    delete props.events;
  }
  return props;
}

/**
 * Special handling for card action events
 */
function attachCardActionHandlers(tile, props, eventsContext) {
  if (!eventsContext || !props || typeof props !== "object") {
    return props;
  }
  if (tile?.role !== "swarmakit:vue:card-actions") {
    return props;
  }
  const actions = props.actions;
  if (!Array.isArray(actions)) {
    return props;
  }
  actions.forEach((action, actionIndex) => {
    if (!action || typeof action !== "object") {
      return;
    }
    const rawEvents = action.events;
    if (!rawEvents) {
      return;
    }
    const candidates = Array.isArray(rawEvents) ? rawEvents : [rawEvents];
    const handlers = [];
    candidates.forEach((raw, eventIndex) => {
      const binding = normalizeTileEventBinding(
        tile,
        `card-action:${actionIndex}:${eventIndex}`,
        raw,
        eventsContext
      );
      if (!binding) {
        return;
      }
      const handler = createTileEventHandler(tile, binding, eventsContext, props);
      if (handler) {
        handlers.push(handler);
      }
    });
    if (!handlers.length) {
      return;
    }
    action.onClick = async (event) => {
      for (const handler of handlers) {
        await handler(event);
      }
    };
    delete action.events;
  });
  return props;
}

// Exports
export {
  EVENT_LISTENER_ALIASES,
  DEFAULT_EVENT_METHOD,
  ensureTileProps,
  resolveSlotContent,
  attachTileEventHandlers,
  attachCardActionHandlers
};
