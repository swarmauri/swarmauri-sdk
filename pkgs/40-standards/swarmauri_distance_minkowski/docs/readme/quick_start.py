from swarmauri_standard.metrics.LpMetric import LpMetric

metric = LpMetric(p=2)
distance = metric.distance([1.0, 2.0], [1.0, 2.0])
similarity = 1.0 if distance == 0.0 else 1.0 / (1.0 + distance)
