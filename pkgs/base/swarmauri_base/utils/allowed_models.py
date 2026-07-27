"""Provide exact and glob-based model allowlist matching."""

from fnmatch import fnmatchcase


def is_model_allowed(name: str, allowed_models: list[str]) -> bool:
    """Return whether a model name matches an allowlist pattern.

    Evaluate ``name`` against each entry in ``allowed_models`` using
    case-sensitive, shell-style matching. Entries may be exact model IDs or
    glob patterns. The supported pattern operators are ``*`` for any sequence,
    ``?`` for one character, ``[seq]`` for one listed character, and
    ``[!seq]`` for one character outside a set.

    Model-name separators are ordinary characters: ``*`` matches across
    ``/`` boundaries. Consequently, ``anthropic/*`` also matches nested names
    such as ``anthropic/team/model``. ``**`` has no special recursive meaning
    and behaves like ``*``. Matching is case-sensitive, so ``OpenAI/*`` does
    not match ``openai/gpt-4o``. Wrap metacharacters in brackets to match them
    literally, for example ``[*]``, ``[?]``, or ``[[]``.

    Policy semantics are explicit and deny by default. An empty list denies
    every model, while ``["*"]`` permits every model name. When multiple
    patterns are supplied, a match against any one pattern permits the model.
    This function does not mutate the policy.

    Args:
        name: Model identifier to evaluate, such as
            ``"anthropic/claude-sonnet-4"``.
        allowed_models: Exact identifiers and glob patterns that define the
            allowlist policy.

    Returns:
        ``True`` when at least one pattern matches ``name``; otherwise
        ``False``.

    Examples:
        >>> is_model_allowed("openai/gpt-4o", [])
        False
        >>> is_model_allowed("openai/gpt-4o", ["openai/gpt-4o"])
        True
        >>> is_model_allowed("anthropic/claude-sonnet-4", ["anthropic/*"])
        True
        >>> is_model_allowed("openai/gpt-4o", ["anthropic/*"])
        False
    """
    return any(fnmatchcase(name, pattern) for pattern in allowed_models)
