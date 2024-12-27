import re
from typing import List, Tuple, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase


class Md2HtmlParser(ParserBase):
    """
    A concrete implementation of the IParser interface that parses Markdown text.
    
    This parser takes Markdown formatted text, converts it to HTML using Python's
    markdown library, and then uses BeautifulSoup to extract plain text content. The
    resulting plain text is then wrapped into Document instances.
    """
    rules: List[Tuple[str, str]] = [
            (r'###### (.*)', r'<h6>\1</h6>'),
            (r'##### (.*)', r'<h5>\1</h5>'),
            (r'#### (.*)', r'<h4>\1</h4>'),
            (r'### (.*)', r'<h3>\1</h3>'),
            (r'## (.*)', r'<h2>\1</h2>'),
            (r'# (.*)', r'<h1>\1</h1>'),
            (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
            (r'\*(.*?)\*', r'<em>\1</em>'),
            (r'!\[(.*?)\]\((.*?)\)', r'<img alt="\1" src="\2" />'),
            (r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>'),
            (r'\n\n', r'<p>'),
            (r'\n', r'<br>'),
        ]
    type: Literal['Md2HtmlParser'] = 'Md2HtmlParser'

    def parse(self, data: str) -> List[Document]:
        documents = []
        for pattern, repl in self.rules:
            data = re.sub(pattern, repl, data)
        documents.append( Document(content=data, metadata={} ))
        
        return documents