from typing import Optional, Any, Literal, List, Union, Dict
from pydantic import BaseModel, Field
from swarmauri.messages.base.MessageBase import MessageBase

class TextContent(BaseModel):
    type: Literal['text']
    text: str

class ImageURLContent(BaseModel):
    type: Literal['image_url']
    image_url: Dict[str, Any]

ContentItem = Union[TextContent, ImageURLContent]
class HumanMessage(MessageBase):
    content: Union[str, List[ContentItem]]
    role: str = Field(default='user')
    name: Optional[str] = None
    type: Literal['HumanMessage'] = 'HumanMessage'

