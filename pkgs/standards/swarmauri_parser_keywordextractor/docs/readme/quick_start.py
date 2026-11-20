from swarmauri_parser_keywordextractor import KeywordExtractorParser

# Initialize the parser for three keywords in English
parser = KeywordExtractorParser(num_keywords=3, lang="en")

text = (
    "Artificial intelligence and machine learning are transforming technology"
)
documents = parser.parse(text)

for document in documents:
    score = document.metadata["score"]
    print(f"Keyword: {document.content}, Score: {score:.4f}")
