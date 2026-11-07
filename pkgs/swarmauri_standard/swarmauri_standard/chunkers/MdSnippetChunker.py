import re
from typing import Any, List, Literal, Optional

from swarmauri_base.chunkers.ChunkerBase import ChunkerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ChunkerBase, "MdSnippetChunker")
class MdSnippetChunker(ChunkerBase):
    version: str = "0.1.0.dev1"
    language: Optional[str] = None
    type: Literal["MdSnippetChunker"] = "MdSnippetChunker"

    def chunk_text(self, text: str | Any, *args, **kwargs) -> List[tuple]:
        """
        Extracts paired comments and code blocks from Markdown content based on
        the
        specified programming language.
        """
        if self.language:
            pattern = rf"```{self.language}\s*(.*?)```"
            snippets = []
            previous_end = 0
            for match in re.finditer(pattern, text, re.DOTALL):
                comment = text[previous_end : match.start()].strip()
                snippets.append(
                    (comment, self.language, match.group(1).strip())
                )
                previous_end = match.end()
            return snippets

        # Extract blocks and languages dynamically if no specific language
        # is provided
        scripts = []
        languages = []
        for match in re.finditer(r"```(\w+)?\s*(.*?)```", text, re.DOTALL):
            languages.append(match.group(1) or "")
            scripts.append(match.group(2))
        comments_temp = re.split(r"```.*?```", text, flags=re.DOTALL)

        comments = [comment.strip() for comment in comments_temp]

        if text.strip().startswith("```"):
            comments = [""] + comments
        if text.strip().endswith("```"):
            comments.append("")

        return [
            (comments[i], languages[i], script.strip())
            for i, script in enumerate(scripts)
        ]
