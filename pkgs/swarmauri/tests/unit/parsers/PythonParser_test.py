import pytest
import logging
from swarmauri.parsers.concrete.PythonParser import PythonParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == 'PythonParser'

@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id

@pytest.mark.unit
def test_parse():
    python_code = """class ExampleClass:
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
    pass"""
    assert Parser().parse(python_code)[0].content == 'This is an example class.'
    assert Parser().parse(python_code)[1].content == 'This is an example function.'
    assert Parser().parse(python_code)[2].content == 'This is an example method.'

@pytest.mark.unit
def test_parse_class_into_metadata():
    python_code = """class ExampleClass:
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
    pass"""

    result_1 = """class ExampleClass:
    \"\"\"
    This is an example class.
    \"\"\"
    
    def example_method(self):
        \"\"\"
        This is an example method.
        \"\"\"
        print('example method')"""


    logging.info(Parser().parse(python_code)[0].metadata)
    assert Parser().parse(python_code)[0].metadata['source_code'] == result_1

@pytest.mark.unit
def test_parse_function_into_metadata():
    python_code = """class ExampleClass:
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
    pass"""


    result_2 = """def example_function():
    \"\"\"
    This is an example function.
    \"\"\"
    pass"""
    logging.info(Parser().parse(python_code)[0].metadata)
    assert Parser().parse(python_code)[1].metadata['source_code'] == result_2

@pytest.mark.unit
def test_parse_function_into_document_resource():
    python_code = """class ExampleClass:
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
    pass"""

    logging.info(Parser().parse(python_code)[0].metadata)
    assert Parser().parse(python_code)[1].resource == 'Document'