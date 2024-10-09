import pytest
from swarmauri.tools.concrete import AutomatedReadabilityIndexTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "AutomatedReadabilityIndexTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_text, expected_score",
    [
        ("The quick brown fox jumps over the lazy dog.", 1.91),
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            11.41,  # Replace with the expected ARI score for this input
        ),
        (
            "A short sentence.",
            3.62,  # Replace with the expected ARI score for this input
        ),
        (
            "",
            0.00,  # Replace with the expected ARI score for this input
        ),
        (
            "Some longer text to test the algorithm with more complexity and variability in sentence length and word choice.",
            12.16,  # Replace with the expected ARI score for this input
        ),
    ],
)
def test_call(input_text, expected_score):
    tool = Tool()

    result = tool(input_text)

    expected_keys = {"ari_score"}

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(
        result.keys()
    ), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(
        result.get("ari_score"), float
    ), f"Expected float, but got {type(result.get('ari_score')).__name__}"

    assert (
        result.get("ari_score") == pytest.approx(expected_score, rel=1e-2)
    ), f"Expected ARI score 22. {expected_score} ± {1e-2 * expected_score}, but got {result.get('ari_score')}"
