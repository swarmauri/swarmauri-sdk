import pytest
from swarmauri.standard.parsers.concrete.PythonParser import PythonParser

@pytest.mark.unit
def test_ubc_resource():
    def test():
        parser = PythonParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def test_parse():
    def test():
        python_code = """
class ExampleClass:
    \"\"\"
    This is an example class.
    \"\"\"
    
    def example_method(self):
        \"\"\"
        This is an example method.
        \"\"\"
        pass

def example_function():
    \"\"\"
    This is an example function.
    \"\"\"
    pass
        """
        assert PythonParser().parse(python_code)[0].content == 'This is an example class.'
        assert PythonParser().parse(python_code)[1].content == 'This is an example function.'
        assert PythonParser().parse(python_code)[2].content == 'This is an example method.'
    test()

@pytest.mark.unit
def test_parse_2():
    def test():
        python_code = """
class ExampleClass:
    \"\"\"
    This is an example class.
    \"\"\"
    
    def example_method(self):
        \"\"\"
        This is an example method.
        \"\"\"
        print('example method')

def example_function():
    \"\"\"
    This is an example function.
    \"\"\"
    pass
        """

        result_1 = """
class ExampleClass:
    \"\"\"
    This is an example class.
    \"\"\"
    
    def example_method(self):
        \"\"\"
        This is an example method.
        \"\"\"
        print('example method')
                """

        result_2 = """
def example_function():
    \"\"\"
    This is an example function.
    \"\"\"
    pass
            """
        assert PythonParser().parse(python_code)[0].metadata['source_code'] == result_1
        assert PythonParser().parse(python_code)[1].metadata['source_code'] == result_2
        assert PythonParser().parse(python_code)[1].resource == 'Document'
    test()