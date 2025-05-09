import pytest
from swarmauri_standard.swarmauri_standard.similarities.BrayCurtisSimilarity import BrayCurtisSimilarity

@pytest.mark.unit
class TestBrayCurtisSimilarity:
    """Unit tests for BrayCurtisSimilarity class."""

    @pytest.fixture
    def braycurtis_instance(self):
        """Fixture to provide a BrayCurtisSimilarity instance."""
        return BrayCurtisSimilarity()

    def test_type_attribute(self):
        """Test that the type attribute is correctly set."""
        assert BrayCurtisSimilarity.type == "BrayCurtisSimilarity"

    def test_resource_attribute(self, braycurtis_instance):
        """Test that the resource attribute is correctly set."""
        assert braycurtis_instance.resource == "SIMILARITY"

    @pytest.mark.parametrize(
        "a,b,expected_similarity",
        [
            ([1, 2, 3], [1, 2, 3], 1.0),  # Identical vectors
            ([0, 0, 0], [0, 0, 0], 0.0),  # Zero vectors
            ([1, 2, 3], [4, 5, 6], 0.0),  # Completely different vectors
            ([1, 1, 1], [2, 2, 2], 0.0),  # Different magnitudes
        ],
    )
    def test_similarity(
        self, braycurtis_instance, a, b, expected_similarity
    ):
        """Test Bray-Curtis similarity calculation."""
        similarity = braycurtis_instance.similarity(a, b)
        assert pytest.approx(similarity, expected_similarity)

    def test_similarity_raises_value_error_for_none(self, braycurtis_instance):
        """Test that similarity raises ValueError for None inputs."""
        with pytest.raises(ValueError):
            braycurtis_instance.similarity(None, [1, 2, 3])

    @pytest.mark.parametrize(
        "a,b_list,expected_similarities",
        [
            ([1, 2, 3], [[1, 2, 3], [4, 5, 6]], (1.0, 0.0)),
        ],
    )
    def test_similarities(
        self, braycurtis_instance, a, b_list, expected_similarities
    ):
        """Test multiple Bray-Curtis similarity calculations."""
        similarities = braycurtis_instance.similarities(a, b_list)
        assert similarities == expected_similarities

    def test_check_boundedness(self, braycurtis_instance):
        """Test that check_boundedness returns True."""
        assert braycurtis_instance.check_boundedness([1, 2, 3], [4, 5, 6])

    @pytest.mark.parametrize(
        "a,expected_reflexive",
        [
            ([1, 2, 3], True),  # Typical vector
            ([0, 0, 0], True),  # Zero vector
            (None, False),  # None input
        ],
    )
    def test_check_reflexivity(
        self, braycurtis_instance, a, expected_reflexive
    ):
        """Test reflexivity check."""
        assert (
            braycurtis_instance.check_reflexivity(a) == expected_reflexive
        )

    def test_dissimilarity(self, braycurtis_instance):
        """Test Bray-Curtis dissimilarity calculation."""
        a = [1, 2, 3]
        b = [4, 5, 6]
        dissimilarity = braycurtis_instance.dissimilarity(a, b)
        assert pytest.approx(dissimilarity, 1.0)

    def test_serialization(self, braycurtis_instance):
        """Test serialization/deserialization consistency."""
        dumped = braycurtis_instance.model_dump_json()
        loaded = BrayCurtisSimilarity.model_validate_json(dumped)
        assert braycurtis_instance.model_dump_json() == loaded