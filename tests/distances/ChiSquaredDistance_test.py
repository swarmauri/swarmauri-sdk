from swarmauri.standard.prompts.concrete.ChiSquaredDistance import ChiSquaredDistance

@pytest.mark.unit
def test_1():
	def test():
		assert ChiSquaredDistance().distance(
		    Vector(value=[1,2]), 
		    Vector(value=[1,2])
		    ) == 0.0
	test()

