from typing import Dict
from tweepy import Client

from swarmauri.tools.concrete.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class TwitterPostTool(ToolBase):
    def __init__(self, bearer_token):
        # Initialize parameters necessary for posting a tweet
        parameters = [
            Parameter(
                name="status",
                type="string",
                description="The status message to post on Twitter",
                required=True,
            )
        ]

        super().__init__(
            name="TwitterPostTool",
            description="Post a status update on Twitter",
            parameters=parameters,
        )

        # Initialize Twitter API Client
        self.client = Client(bearer_token=bearer_token)

    def __call__(self, status: str) -> Dict[str, str]:
        """
        Posts a status on Twitter.

        Args:
            status (str): The status message to post.

        Returns:
            Dict[str, str]: A dictionary containing the response from the Twitter API.
        """
        try:
            # Using Tweepy to send a tweet
            response = self.client.create_tweet(text=status)
            tweet_id = response.data["id"]
            # Constructing URL to the tweet - Adjust the URL to match Twitter API v2 structure if needed
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            return {"message": "Tweet posted successfully!", "tweet_url": tweet_url}
        except Exception as e:
            return {"message": f"Failed to post tweet: {e}"}
