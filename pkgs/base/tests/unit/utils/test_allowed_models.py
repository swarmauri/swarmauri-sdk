"""Test shared exact and glob model allowlist behavior."""

import pytest

from swarmauri_base.utils.allowed_models import is_model_allowed


@pytest.mark.parametrize(
    ("name", "allowed_models"),
    [
        ("openai/gpt-4o", ["openai/gpt-4o"]),
        ("", [""]),
        ("anthropic/claude-sonnet-4", ["*"]),
        ("anthropic/claude-sonnet-4", ["anthropic/*"]),
        ("anthropic/team/claude", ["anthropic/*"]),
        ("anthropic/team/claude", ["anthropic/**"]),
        ("openai/gpt-4o", ["openai/gpt-4?"]),
        ("openai/gpt-4.1", ["openai/gpt-4.?"]),
        ("provider/model-a", ["provider/model-[abc]"]),
        ("provider/model-7", ["provider/model-[0-9]"]),
        ("provider/model-z", ["provider/model-[!abc]"]),
        ("provider/model-*", ["provider/model-[*]"]),
        ("provider/model-?", ["provider/model-[?]"]),
        ("provider/model-[", ["provider/model-[[]"]),
        ("openai/gpt-4o-mini", ["anthropic/*", "openai/gpt-4o*"]),
        ("vendor/model", ["does-not-match", "vendor/model"]),
    ],
)
def test_positive_patterns(name, allowed_models):
    assert is_model_allowed(name, allowed_models)


@pytest.mark.parametrize(
    ("name", "allowed_models"),
    [
        ("anthropic/claude", []),
        ("", []),
        ("openai/gpt-4o-mini", ["openai/gpt-4o"]),
        ("OpenAI/gpt-4o", ["openai/gpt-4o"]),
        ("openai/GPT-4o", ["openai/gpt-4o"]),
        ("openai/gpt-4o", ["anthropic/*"]),
        ("anthropic", ["anthropic/*"]),
        ("openai/gpt-4", ["openai/gpt-4?"]),
        ("openai/gpt-4oo", ["openai/gpt-4?"]),
        ("provider/model-d", ["provider/model-[abc]"]),
        ("provider/model-x", ["provider/model-[0-9]"]),
        ("provider/model-a", ["provider/model-[!abc]"]),
        ("provider/model-x", ["provider/model-[*]"]),
        ("provider/model-x", ["provider/model-[?]"]),
        ("other/model", ["anthropic/*", "openai/*"]),
        ("anthropic/claude", [""]),
    ],
)
def test_negative_patterns(name, allowed_models):
    assert not is_model_allowed(name, allowed_models)


def test_star_matches_empty_name_too():
    assert is_model_allowed("", ["*"])


def test_double_star_has_no_special_recursive_semantics():
    names = ["anthropic/claude", "anthropic/team/claude", "anthropic/"]
    for name in names:
        assert is_model_allowed(name, ["anthropic/*"]) == is_model_allowed(
            name, ["anthropic/**"]
        )


def test_matching_does_not_mutate_policy():
    policy = ["anthropic/*", "openai/gpt-4o"]
    original = policy.copy()
    is_model_allowed("anthropic/claude", policy)
    assert policy == original
