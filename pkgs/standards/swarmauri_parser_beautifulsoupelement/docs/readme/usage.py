from swarmauri_parser_beautifulsoupelement import BeautifulSoupElementParser

# Create a parser instance to extract paragraphs
parser = BeautifulSoupElementParser(element="p")

# HTML content to parse
html_content = "<div><p>First paragraph</p><p>Second paragraph</p></div>"

# Parse the content (input must be a string)
documents = parser.parse(html_content)

# Access the extracted elements and metadata
for doc in documents:
    print(
        doc.content
    )  # Prints each paragraph element, including the surrounding <p> tag
    print(
        doc.metadata
    )  # {'element': 'p', 'index': 0}, {'element': 'p', 'index': 1}, ...
