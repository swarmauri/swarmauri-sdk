#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <vector>
#include <algorithm>
#include <memory>
#include <cmath>

// Class representing a node in the kd-tree
class KDTreeNode {
public:
    std::vector<double> point; // Point in the kd-tree
    std::unique_ptr<KDTreeNode> left; // Left child
    std::unique_ptr<KDTreeNode> right; // Right child

    KDTreeNode(std::vector<double> pt) : point(std::move(pt)), left(nullptr), right(nullptr) {}
};

// Class for constructing the kd-tree
class KDTree {
public:
    KDTree(std::vector<std::vector<double>> points) : root(buildTree(points, 0)) {}

    // Function to find the nearest neighbor
    std::vector<double> nearestNeighbor(const std::vector<double>& target) {
        return nearestNeighborHelper(root.get(), target, 0);
    }

private:
    std::unique_ptr<KDTreeNode> root;

    // Recursive function to build the kd-tree
    std::unique_ptr<KDTreeNode> buildTree(std::vector<std::vector<double>>& points, int depth) {
        if (points.empty()) return nullptr;

        // Select axis based on depth so that we cycle through all dimensions
        size_t axis = depth % points[0].size();

        // Sort points by the selected axis
        std::sort(points.begin(), points.end(), [axis](const std::vector<double>& a, const std::vector<double>& b) {
            return a[axis] < b[axis];
        });

        // Choose median as root
        size_t median = points.size() / 2;
        auto node = std::make_unique<KDTreeNode>(points[median]);

        // Recursively build the left and right subtrees
        std::vector<std::vector<double>> leftPoints(points.begin(), points.begin() + median);
        std::vector<std::vector<double>> rightPoints(points.begin() + median + 1, points.end());
        node->left = buildTree(leftPoints, depth + 1);
        node->right = buildTree(rightPoints, depth + 1);

        return node;
    }

    // Recursive function to find the nearest neighbor
    std::vector<double> nearestNeighborHelper(KDTreeNode* node, const std::vector<double>& target, int depth) {
        if (node == nullptr) return {};

        size_t axis = depth % target.size();
        std::vector<double> bestPoint = node->point;
        double bestDist = distance(bestPoint, target);

        // Search the corresponding subtree
        KDTreeNode* nextNode = (target[axis] < node->point[axis]) ? node->left.get() : node->right.get();
        std::vector<double> candidate = nearestNeighborHelper(nextNode, target, depth + 1);
        if (!candidate.empty()) {
            double candidateDist = distance(candidate, target);
            if (candidateDist < bestDist || (candidateDist == bestDist && candidate < bestPoint)) {
                bestPoint = candidate;
                bestDist = candidateDist;
            }
        }

        // Check if we need to search the other subtree
        KDTreeNode* otherNode = (nextNode == node->left.get()) ? node->right.get() : node->left.get();
        if (otherNode != nullptr) {
            double axisDist = std::abs(target[axis] - node->point[axis]);
            if (axisDist < bestDist) {
                candidate = nearestNeighborHelper(otherNode, target, depth + 1);
                if (!candidate.empty()) {
                    double candidateDist = distance(candidate, target);
                    if (candidateDist < bestDist || (candidateDist == bestDist && candidate < bestPoint)) {
                        bestPoint = candidate;
                    }
                }
            }
        }

        return bestPoint;
    }

    // Utility function to calculate Euclidean distance
    double distance(const std::vector<double>& a, const std::vector<double>& b) {
        double dist = 0.0;
        for (size_t i = 0; i < a.size(); ++i) {
            dist += (a[i] - b[i]) * (a[i] - b[i]);
        }
        return std::sqrt(dist);
    }
};


PYBIND11_MODULE(tree_index, module) {
    module.def("nearestNeighbor", [](std::vector<std::vector<double>> points, const std::vector<double>& target) {
        for (const auto& point : points)
            if (point.size() != target.size()) throw py::value_error("Vector dimensions must match");
        if (target.empty() && !points.empty()) throw py::value_error("Target cannot be empty");
        KDTree tree(points);
        return tree.nearestNeighbor(target);
    });
}
