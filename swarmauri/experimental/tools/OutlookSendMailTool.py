import requests
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class OutlookSendMailTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="recipient",
                type="string",
                description="The email address of the recipient",
                required=True
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True
            ),
            Parameter(
                name="body",
                type="string",
                description="The HTML body of the email",
                required=True
            )
        ]
        
        super().__init__(name="OutlookSendMailTool", 
                         description="Sends an email using the Outlook service.",
                         parameters=parameters)

        # Add your Microsoft Graph API credentials and endpoint URL here
        self.tenant_id = "YOUR_TENANT_ID"
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def get_access_token(self):
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.scope),
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json().get("access_token")

    def __call__(self, recipient, subject, body):
        access_token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient
                        }
                    }
                ]
            }
        }

        send_mail_endpoint = f"{self.graph_endpoint}/users/{self.client_id}/sendMail"
        response = requests.post(send_mail_endpoint, json=email_data, headers=headers)
        if response.status_code == 202:
            return "Email sent successfully"
        else:
            return f"Failed to send email, status code {response.status_code}"