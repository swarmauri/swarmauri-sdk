# Metric Distances and Similarity

Metric theory-based distances quantify how far apart two vectors are within a metric space. They satisfy non-negativity, identity of indiscernibles, symmetry, and the triangle inequality. The SDK exposes these metrics through distance classes that also provide convenience methods to convert a distance into a similarity score.

## Available Distance Classes

Common implementations include:

- `CosineDistance`
- `EuclideanDistance`
- `SquaredEuclideanDistance`
- `ManhattanDistance`
- `MinkowskiDistance`
- `ChebyshevDistance`
- `CanberraDistance`
- `HaversineDistance`
- `JaccardIndexDistance`
- `SorensenDiceDistance`
- `ChiSquaredDistance`
- `LevenshteinDistance`

These classes live under the `swarmauri.distances` namespace and implement both `distance()` and `similarity()` methods.

## Similarity Measures

Similarity measures compute how alike two vectors are without guaranteeing the properties of a metric. They implement the `ISimilarity` interface and often return a value in the range `[0, 1]`. Examples include the experimental `SSASimilarity` and `SSIVSimilarity` classes.

## Deprecation Notice

The distance classes are **deprecated** and scheduled for removal in `v0.10.0`. Future releases will focus on dedicated similarity implementations that conform to `ISimilarity`. Migrate your code to these similarity classes to remain compatible with upcoming versions.
