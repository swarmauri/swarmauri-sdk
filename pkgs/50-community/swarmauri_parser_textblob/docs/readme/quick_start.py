from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
documents = parser.parse(
    "One more large chapula please. It should be extra spicy!"
)

for document in documents:
    print(document.content)
