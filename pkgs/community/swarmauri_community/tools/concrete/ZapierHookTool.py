import json
import requests
from typing import Dict, List, Literal
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
from pydantic import Field


"""
- Zapier's webhooks do not require authentication for basic usage,
    as they are designed to be secure via their unique URLs.
- The webhook URL (https://hooks.zapier.com/hooks/catch/{zap_id}/) includes
    a randomly generated identifier that is private to you,
    ensuring that only those with the specific URL can trigger the Zap.

Reference
---------------
- https://www.switchlabs.dev/resources/locating-your-webhook-url-in-zapier
- https://zapier.com/apps/webhook/integrations
- https://zapier.com/engineering/webhook-design/

"""


class ZapierHookTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="payload",
                type="string",
                description="A Payload to send when triggering the Zapier webhook",
                required=True,
            )
        ]
    )

    name: str = "ZapierTool"
    description: str = "Tool to authenticate with Zapier and execute zaps."
    type: Literal["ZapierHookTool"] = "ZapierHookTool"

    content_type: str = "application/json"
    zap_url: str

    def execute_zap(self, payload: str) -> str:
        """Execute a zap with given payload.

        Args:
            payload (str): The data payload to send to the Zap.

        Returns:
            str: The response from Zapier API.
        """
        headers = {"Content-Type": self.content_type}

        response = requests.post(
            self.zap_url,
            json={"data": payload},
            headers=headers,
        )
        # Checking the HTTP response status for success or failure
        if response.status_code == 200:
            return json.dumps(response.json())
        else:
            response.raise_for_status()  # This will raise an error for non-200 responses

    def __call__(self, payload: str) -> Dict[str, str]:
        """
        Enable the tool to be called directly with the given payload and return the zap response.

        Parameters:
        payload (str): The input string to be processed by the tool.

        Returns:
        Dict[str, str]: A dictionary with a single key "zap_response", containing the result of executing the zap.

        Example:
        >>> tool = YourToolClass()
        >>> result = tool("some payload")
        >>> print(result)
        {'zap_response': 'processed result'}
        """
        return {"zap_response": self.execute_zap(payload)}
