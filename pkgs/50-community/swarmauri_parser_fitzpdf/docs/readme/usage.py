from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
documents = parser.parse("reports/quarterly.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content[:500])
