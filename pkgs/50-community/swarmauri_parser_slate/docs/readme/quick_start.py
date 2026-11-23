from swarmauri_parser_slate import SlateParser

parser = SlateParser()
documents = parser.parse("pdfs/handbook.pdf")

for document in documents:
    print(document.metadata["page_number"], document.content[:120])
