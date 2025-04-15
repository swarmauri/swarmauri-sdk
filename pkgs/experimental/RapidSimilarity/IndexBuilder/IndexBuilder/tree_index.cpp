#include <Python.h>
#include <numpy/arrayobject.h>
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
            if (candidateDist < bestDist) {
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
                    if (candidateDist < bestDist) {
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

// Python wrapper for KDTree
static PyObject* py_nearestNeighbor(PyObject* self, PyObject* args) {
    PyObject* pointsObj;
    PyObject* targetObj;

    // Parse input
    if (!PyArg_ParseTuple(args, "OO", &pointsObj, &targetObj)) {
        return nullptr;
    }

    // Convert Python list to std::vector<std::vector<double>>
    std::vector<std::vector<double>> points;
    Py_ssize_t numPoints = PyList_Size(pointsObj);
    for (Py_ssize_t i = 0; i < numPoints; ++i) {
        PyObject* pointObj = PyList_GetItem(pointsObj, i);
        std::vector<double> point;
        Py_ssize_t numDims = PyList_Size(pointObj);
        for (Py_ssize_t j = 0; j < numDims; ++j) {
            point.push_back(PyFloat_AsDouble(PyList_GetItem(pointObj, j)));
        }
        points.push_back(point);
    }

    // Convert target to std::vector<double>
    std::vector<double> target;
    Py_ssize_t targetDims = PyList_Size(targetObj);
    for (Py_ssize_t i = 0; i < targetDims; ++i) {
        target.push_back(PyFloat_AsDouble(PyList_GetItem(targetObj, i)));
    }

    // Build the KDTree and find the nearest neighbor
    KDTree tree(points);
    std::vector<double> nearest = tree.nearestNeighbor(target);

    // Convert result back to Python list
    PyObject* result = PyList_New(nearest.size());
    for (size_t i = 0; i < nearest.size(); ++i) {
        PyList_SetItem(result, i, PyFloat_FromDouble(nearest[i]));
    }

    return result;
}

// Module method definitions
static PyMethodDef KDTreeMethods[] = {
    {"nearestNeighbor", py_nearestNeighbor, METH_VARARGS, "Find the nearest neighbor."},
    {nullptr, nullptr, 0, nullptr}
};

// Module definition
static struct PyModuleDef kdtree_module = {
    PyModuleDef_HEAD_INIT,
    "kdtree",
    nullptr,
    -1,
    KDTreeMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_kdtree(void) {
    import_array(); // Initialize NumPy API
    return PyModule_Create(&kdtree_module);
}