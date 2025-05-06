from typing import Optional, Literal, List, Union, Dict
from pydantic import Field, field_validator
from typing_extensions import TypedDict

from swarmauri_standard.utils.base64_encoder import is_url, encode_file
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.ComponentBase import ComponentBase


# Define specific content types
class TextContent(TypedDict):
    type: str
    text: str


class ImageUrlContent(TypedDict):
    type: str
    image_url: Union[str, Dict]


contentItem = Union[TextContent, ImageUrlContent]


@ComponentBase.register_type(MessageBase, "HumanMessage")
class HumanMessage(MessageBase):
    content: Optional[Union[str, List[contentItem]]]
    role: str = Field(default="user")
    name: Optional[str] = None
    type: Literal["HumanMessage"] = "HumanMessage"

    @field_validator("content", mode="before")
    def validate_content(
        cls, content: Optional[Union[str, List[contentItem]]]
    ) -> Optional[Union[str, List[contentItem]]]:
        if isinstance(content, list):
            for item in content:
                image_data = item.get("image_url", {})
                url = image_data.get("url")
                if url and not is_url(url):
                    image_data["url"] = f"data:image/jpeg;base64,{encode_file(url)}"
        return content
