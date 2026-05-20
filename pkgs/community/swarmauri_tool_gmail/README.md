![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_gmail/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_gmail/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_gmail/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_gmail.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_gmail/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_gmail/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_gmail" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_gmail/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_gmail?label=swarmauri_tool_gmail&color=green" alt="PyPI - swarmauri_tool_gmail"/></a>
</p>
---

# Swarmauri Tool Gmail

Tools for sending and reading Gmail messages via Google Workspace service-account delegation. Provides `GmailSendTool` and `GmailReadTool` wrappers around the Gmail REST API.

## Features

- `GmailSendTool` sends HTML emails to one or more recipients.
- `GmailReadTool` fetches messages matching a Gmail search query and formats key headers.
- Both tools authenticate with `googleapiclient` using a service account JSON file and delegated user email.

## Prerequisites

- Python 3.10 or newer.
- Google Cloud service account with Gmail API enabled and domain-wide delegation to the target user.
- Credentials JSON file with the `https://www.googleapis.com/auth/gmail.send` and/or `https://www.googleapis.com/auth/gmail.readonly` scopes.
- Install `google-api-python-client` and `google-auth` (pulled in automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_gmail

# poetry
poetry add swarmauri_tool_gmail

# uv (pyproject-based projects)
uv add swarmauri_tool_gmail
```

## Sending Email

```python
from swarmauri_tool_gmail import GmailSendTool

send_tool = GmailSendTool(
    credentials_path="service-account.json",
    sender_email="user@yourdomain.com",
)

result = send_tool(
    recipients="recipient@example.com",
    subject="Test Email",
    htmlMsg="<p>Hello, this is a test email!</p>",
)

print(result)
```

## Reading Email

```python
from swarmauri_tool_gmail import GmailReadTool

read_tool = GmailReadTool(
    credentials_path="service-account.json",
    sender_email="user@yourdomain.com",
)

result = read_tool(query="is:unread", max_results=5)
print(result["gmail_messages"])
```

## Tips

- Ensure the service account has been granted domain-wide delegation and that the Gmail API is enabled in Google Cloud console.
- Store credentials securely (Secrets Manager, Vault) and inject the file path via environment variables.
- When sending to multiple recipients, supply a comma-separated string (Gmail handles the formatting).
- For message bodies beyond simple HTML, extend the tool to add attachments or alternative MIME parts.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
