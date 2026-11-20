from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
documents = parser.parse("forms/enrollment.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content)
