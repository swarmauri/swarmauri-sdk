from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
codeword = [1, 0, 1, 1, 0, 0, 1]
received = [1, 1, 1, 1, 0, 0, 1]

print(metric.distance(codeword, received))
