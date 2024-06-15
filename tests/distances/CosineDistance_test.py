from swarmauri.standard.prompts.concrete.CosineDistance import CosineDistance

@pytest.mark.unit
def test_1():
	def test():
		# Floating-Point Precision Epsilon
		assert CosineDistance().distance(
			Vector(value=[1,2]), 
			Vector(value=[1,2])
			) == 2.220446049250313e-16
	test()

