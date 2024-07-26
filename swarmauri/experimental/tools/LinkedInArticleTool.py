import requests
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class LinkedInArticleTool(ToolBase):
    """
    A tool to post articles on LinkedIn using the LinkedIn API.
    """
    def __init__(self, access_token):
        """
        Initializes the LinkedInArticleTool with the necessary access token.
        
        Args:
            access_token (str): The OAuth access token for authenticating with the LinkedIn API.
        """
        super().__init__(name="LinkedInArticleTool",
                         description="A tool for posting articles on LinkedIn.",
                         parameters=[
                             Parameter(name="title", type="string", description="The title of the article", required=True),
                             Parameter(name="text", type="string", description="The body text of the article", required=True),
                             Parameter(name="visibility", type="string", description="The visibility of the article", required=True, enum=["anyone", "connectionsOnly"])
                         ])
        self.access_token = access_token
        
    def __call__(self, title: str, text: str, visibility: str = "anyone") -> str:
        """
        Posts an article on LinkedIn.

        Args:
            title (str): The title of the article.
            text (str): The body text of the article.
            visibility (str): The visibility of the article, either "anyone" or "connectionsOnly".

        Returns:
            str: A message indicating the success or failure of the post operation.
        """
        # Construct the request URL and payload according to LinkedIn API documentation
        url = 'https://api.linkedin.com/v2/ugcPosts'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "author": "urn:li:person:YOUR_PERSON_ID_HERE",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": title
                            },
                            "originalUrl": "URL_OF_THE_ARTICLE_OR_IMAGE",
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
            }
        }
     
        # Make the POST request to LinkedIn's API
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return f"Article posted successfully: {response.json().get('id')}"
        else:
            return f"Failed to post the article. Status Code: {response.status_code} - {response.text}"