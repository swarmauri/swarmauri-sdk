A metric, in the context of mathematics and computer science, is a function that defines a distance between elements of a set. This distance function must satisfy four specific axioms, also known as the properties of a metric, to be considered a true metric. These properties ensure that the concept of distance behaves in a mathematically consistent and intuitive manner.

Here are the four properties that a metric (ie: a distance component) must satisfy:

1.  **Non-Negativity (Positivity)**: The distance between any two points must be always non-negative. If the distance is zero, it implies that the two points are identical.

2.  **Identity of Indiscernibles**: If the distance between two points is zero, it means that the two points are identical. This property is related to non-negativity and ensures that a distance of zero implies a perfect match between the elements.

3.  **Symmetry**: The distance from point A to point B must be the same as the distance from point B to point A. This means that the order of points does not affect the distance calculation.

4.  **Triangle Inequality**: The direct distance between two points must be less than or equal to the sum of the distances between each point and a third point. This ensures consistency with the concept of distance.

If a function does not satisfy all these properties, it cannot be considered a metric. 

Now, considering the definition of a distance:

- A distance is a numerical value that describes the dissimilarity or similarity between two points or elements in a set.

However, the term "distance" is often used interchangeably with "metric," which has these four properties. In many contexts, people treat a distance as a metric, assuming it satisfies these properties.

The question that arises is: Can a distance be a metric?

The answer is that not all distances are metrics. A distance can fail to satisfy one or more axioms, making it not a true metric.

For instance, cosine similarity is often treated as a distance, but it doesn't satisfy the triangle inequality property, so it's not a metric.

However, in many situations, people use the term "distance" synonymously with "metric," not strictly adhering to the mathematical definition. Thus, the distinction between a distance and a metric can sometimes be blurred.

In summary, a distance object's internal implementations must satisfy the four properties of non-negativity, identity of indiscernibles, symmetry, and triangle inequality to be considered a true metric.
