from typing import Optional, Any, Literal, List
from pydantic import Field
from swarmauri.messages.base.MessageBase import MessageBase
from typing import Union, Dict
from typing_extensions import TypedDict
# Define specific content types
class TextContent(TypedDict):
    type: str
    text: str

class ImageUrlContent(TypedDict):
    type: str
    image_url: Union[str, Dict]
    
contentItem = Union[TextContent, ImageUrlContent]

class HumanMessage(MessageBase):
    content: Optional[Union[str, List[contentItem]]]
    role: str = Field(default='user')
    name: Optional[str] = None
    type: Literal['HumanMessage'] = 'HumanMessage'    