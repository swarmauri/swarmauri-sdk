![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_gmail/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_gmail" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_gmail/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_gmail.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_gmail/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_gmail" alt="PyPI - Python Version"/></a>
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
