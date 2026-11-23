from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
documents = parser.parse("manuals/device.pdf")

for document in documents:
    print(document.metadata["page_number"])
    print(document.content[:160])
