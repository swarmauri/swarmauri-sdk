import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
from typing import List, Literal, Dict, Optional
from pydantic import Field


class GmailReadTool(ToolBase):
    SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.readonly"]
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="query",
                type="string",
                description="""The query to filter emails. For example, "is:unread" or "from:example@gmail.com".""",
                required=True,
            ),
            Parameter(
                name="max_results",
                type="integer",
                description="""The maximum number of emails to return. Defaults to 10.""",
            ),
        ]
    )

    name: str = "GmailReadTool"
    description: str = "Read emails from a Gmail account."
    type: Literal["GmailReadTool"] = "GmailReadTool"
    credentials_path: str
    sender_email: str
    service: Optional[object] = None

    def authenticate(self):
        """
        Authenticates the user and creates a Gmail API service.
        """
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.SCOPES
        )

        delegated_credentials = credentials.with_subject(self.sender_email)
        self.service = build("gmail", "v1", credentials=delegated_credentials)

    def __call__(self, query: str = "", max_results: int = 10) -> Dict[str, str]:
        """
        Fetches emails from the authenticated Gmail account based on the given query.

        Parameters:
        query (str): The query to filter emails. For example, "is:unread".
        max_results (int): The maximum number of email messages to fetch.

        Returns:
            Dict[str, str]: A dictionary containing the email messages.
        """
        try:
            self.authenticate()
            # Call the Gmail API
            gmail_messages = self.service.users().messages()
            results = gmail_messages.list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            messages = results.get("messages", [])
            message_data = ""
            for message in messages:
                msg = gmail_messages.get(
                    userId="me", id=message["id"], format="full"
                ).execute()
                headers = msg["payload"]["headers"]

                sender = next(
                    header["value"] for header in headers if header["name"] == "From"
                )
                subject = next(
                    header["value"] for header in headers if header["name"] == "Subject"
                )
                reply_to = next(
                    (
                        header["value"]
                        for header in headers
                        if header["name"] == "Reply-To"
                    ),
                    subject,
                )
                date_time = next(
                    header["value"] for header in headers if header["name"] == "Date"
                )

                formatted_msg = f"\nSender: {sender}\nReply-To: {reply_to}\nSubject: {subject}\nDate: {date_time}\n"
                message_data += formatted_msg

            return {"gmail_messages": message_data}
        except Exception as e:
            return f"An error occurred: {str(e)}"
        finally:
            del self.service
