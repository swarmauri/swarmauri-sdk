from swarmauri.standard.prompts.concrete.JaccardIndexDistance import JaccardIndexDistance

@pytest.mark.unit
def test_1():
    def test():
        assert JaccardIndexDistance().distance(
            Vector(value=[1,2]), 
            Vector(value=[1,2])
            ) == 0.0
    test()



