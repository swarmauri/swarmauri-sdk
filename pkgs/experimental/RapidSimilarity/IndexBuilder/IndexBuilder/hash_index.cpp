#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <functional>
#include <vector>
#include <unordered_map>
#include <random>
#include <cmath>
#include <stdexcept>

class LSHIndex {
public:
    LSHIndex(int num_hashes, int bucket_size) : num_hashes(num_hashes), bucket_size(bucket_size) {
        if (bucket_size <= 0) {
            throw std::invalid_argument("Bucket size must be greater than 0.");
        }
        // Initialize hash functions
        for (int i = 0; i < num_hashes; ++i) {
            hash_functions.emplace_back(generate_random_hash_function());
        }
    }

    void insert(const std::vector<float>& data_point) {
        std::vector<int> hashes(num_hashes);
        for (int i = 0; i < num_hashes; ++i) {
            hashes[i] = hash_functions[i](data_point);
        }
        for (int i = 0; i < num_hashes; ++i) {
            buckets[hashes[i]].push_back(data_point);
            if (buckets[hashes[i]].size() > bucket_size) {
                buckets[hashes[i]].pop_back(); // Maintain bucket size
            }
        }
    }

    std::vector<std::vector<float>> query(const std::vector<float>& data_point) {
        std::unordered_map<int, std::vector<std::vector<float>>> result;
        for (int i = 0; i < num_hashes; ++i) {
            int hash_value = hash_functions[i](data_point);
            result[hash_value] = buckets[hash_value];
        }
        std::vector<std::vector<float>> output;
        for (const auto& entry : result) {
            output.insert(output.end(), entry.second.begin(), entry.second.end());
        }
        return output;
    }

private:
    int num_hashes;
    int bucket_size;
    std::unordered_map<int, std::vector<std::vector<float>>> buckets;
    std::vector<std::function<int(const std::vector<float>&)>> hash_functions;

    std::function<int(const std::vector<float>&)> generate_random_hash_function() {
        std::default_random_engine generator;
        std::uniform_real_distribution<float> distribution(-1.0, 1.0);
        std::vector<float> random_vector(2);
        for (int i = 0; i < 2; ++i) {
            random_vector[i] = distribution(generator);
        }
        return [random_vector](const std::vector<float>& point) {
            float dot_product = random_vector[0] * point[0] + random_vector[1] * point[1];
            return static_cast<int>(std::floor(dot_product));
        };
    }
};


static std::vector<float> point_from_array(const py::array& input) {
    auto values = py::array_t<float, py::array::c_style | py::array::forcecast>::ensure(input);
    if (!values || values.ndim() != 1 || values.size() < 2)
        throw py::value_error("Expected a vector with at least two coordinates");
    return {values.data(), values.data() + values.size()};
}
PYBIND11_MODULE(hash_index, module) {
    py::class_<LSHIndex>(module, "LSHIndex")
        .def(py::init<int, int>())
        .def("insert", [](LSHIndex& index, const py::array& point) {
            index.insert(point_from_array(point));
        })
        .def("query", [](LSHIndex& index, const py::array& point) {
            return index.query(point_from_array(point));
        });
}
