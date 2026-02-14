#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

using namespace std;

// A simple Point structure. Here we use a vector to hold the coordinates.
struct Point {
    vector<double> coords;
    Point(double x, double y) : coords({x, y}) {}
};

// A node in the k-d tree.
struct Node {
    Point point;
    int axis;     // splitting dimension (0 for x, 1 for y, etc.)
    Node* left;
    Node* right;
    
    Node(const Point &pt, int ax) : point(pt), axis(ax), left(nullptr), right(nullptr) {}
};

class KDTree {
private:
    Node* root;
    int k; // number of dimensions

public:
    // Build the kd-tree from a vector of points.
    KDTree(const vector<Point>& points, int dimensions) : root(nullptr), k(dimensions) {
        // Make a copy of points since we'll be modifying the vector.
        vector<Point> pts = points;
        root = build(pts, 0);
    }

    ~KDTree() {
        destroy(root);
    }

    // Find the nearest neighbor to the target point.
    Point nearestNeighbor(const Point& target) {
        double bestDist = numeric_limits<double>::max();
        Node* best = nullptr;
        nearest(root, target, best, bestDist);
        if (best)
            return best->point;
        else
            throw runtime_error("No nearest neighbor found");
    }

private:
    // Recursively builds the kd-tree.
    Node* build(vector<Point>& points, int depth) {
        if (points.empty())
            return nullptr;

        // Determine the axis on which to split.
        int axis = depth % k;
        
        // Find the median on this axis.
        size_t medianIndex = points.size() / 2;
        auto comparator = [axis](const Point &a, const Point &b) {
            return a.coords[axis] < b.coords[axis];
        };
        nth_element(points.begin(), points.begin() + medianIndex, points.end(), comparator);
        
        // The point at the median becomes the root of this subtree.
        Point medianPoint = points[medianIndex];
        
        // Prepare left and right subsets (note: these copies are for simplicity).
        vector<Point> leftPoints(points.begin(), points.begin() + medianIndex);
        vector<Point> rightPoints(points.begin() + medianIndex + 1, points.end());
        
        // Create the node and build subtrees.
        Node* node = new Node(medianPoint, axis);
        node->left = build(leftPoints, depth + 1);
        node->right = build(rightPoints, depth + 1);
        return node;
    }
    
    // Recursively deallocates nodes.
    void destroy(Node* node) {
        if (!node)
            return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

    // Helper: computes squared Euclidean distance between two points.
    double distanceSquared(const Point& a, const Point& b) {
        double dist = 0.0;
        for (int i = 0; i < k; i++) {
            double diff = a.coords[i] - b.coords[i];
            dist += diff * diff;
        }
        return dist;
    }
    
    // Recursive nearest neighbor search.
    void nearest(Node* node, const Point& target, Node*& best, double& bestDist) {
        if (!node)
            return;
        
        // Compute distance between the target and the current node.
        double d = distanceSquared(node->point, target);
        if (d < bestDist) {
            bestDist = d;
            best = node;
        }
        
        // Determine which side of the node to search first.
        int axis = node->axis;
        double diff = target.coords[axis] - node->point.coords[axis];
        Node* first = (diff < 0) ? node->left : node->right;
        Node* second = (diff < 0) ? node->right : node->left;
        
        // Search the half that is more likely to contain the target.
        nearest(first, target, best, bestDist);
        
        // If the hypersphere crosses the splitting plane, search the other side.
        if (diff * diff < bestDist)
            nearest(second, target, best, bestDist);
    }
};

int main() {
    // Create some 2D points.
    vector<Point> points = {
        Point(2.0, 3.0),
        Point(5.0, 4.0),
        Point(9.0, 6.0),
        Point(4.0, 7.0),
        Point(8.0, 1.0),
        Point(7.0, 2.0)
    };

    // Build the kd-tree for 2D points.
    KDTree tree(points, 2);

    // Define a target point.
    Point target(9.0, 2.0);

    // Find the nearest neighbor to the target.
    Point nearest = tree.nearestNeighbor(target);

    cout << "Nearest neighbor to (" 
         << target.coords[0] << ", " << target.coords[1] << ") is ("
         << nearest.coords[0] << ", " << nearest.coords[1] << ")." << endl;

    return 0;
}
