import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
from typing import List, Dict, Literal
from pydantic import Field


class GmailSendTool(ToolBase):
    SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.send"]

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="recipients",
                type="string",
                description="The email addresses of the recipients, separated by commas",
                required=True,
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True,
            ),
            Parameter(
                name="htmlMsg",
                type="string",
                description="The HTML message to be sent as the email body",
                required=True,
            ),
        ]
    )

    name: str = "GmailSendTool"
    description: str = "Sends an email using the Gmail API."
    type: Literal["GmailSendTool"] = "GmailSendTool"

    credentials_path: str
    sender_email: str

    def authenticate(self) -> Resource:
        """
        Authenticates the user and creates a Gmail API service for sending emails.
        This method returns the service instance, without saving it as an attribute.
        """
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.SCOPES
        )
        delegated_credentials = credentials.with_subject(self.sender_email)
        return build("gmail", "v1", credentials=delegated_credentials)

    def create_message(
        self, to: str, subject: str, message_text: str
    ) -> Dict[str, str]:
        """
        Create a MIMEText message for sending an email.

        Parameters:
        to (str): The email address of the recipient.
        subject (str): The subject of the email.
        message_text (str): The HTML body of the email.

        Returns:
        Dict[str, str]: The created MIMEText message in a format suitable for Gmail API.
        """
        message = MIMEMultipart("alternative")
        message["from"] = self.sender_email
        message["to"] = to
        message["subject"] = subject
        mime_text = MIMEText(message_text, "html")
        message.attach(mime_text)
        raw_message = base64.urlsafe_b64encode(
            message.as_string().encode("utf-8")
        ).decode("utf-8")
        return {"raw": raw_message}

    def __call__(self, recipients: str, subject: str, htmlMsg: str) -> Dict[str, str]:
        """
        Sends an email to the specified recipients with the given subject and HTML message.

        Parameters:
            recipients (str): The email address of the recipients, separated by commas.
            subject (str): The subject of the email.
            htmlMsg (str): The HTML content of the email body.

        Returns:
            Dict[str, str]: A message indicating the status of the email sending process.
        """
        service = (
            self.authenticate()
        )  # Authenticate within this function and do not store in the object state
        try:
            message = self.create_message(recipients, subject, htmlMsg)
            service.users().messages().send(userId="me", body=message).execute()
            return {"success": f"Email sent successfully to {recipients}"}
        except Exception as e:
            return {"error": f"An error occurred in sending the email: {str(e)}"}
