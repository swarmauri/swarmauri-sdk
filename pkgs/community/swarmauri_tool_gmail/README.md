![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_gmail)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_gmail)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_gmail)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_gmail?label=swarmauri_tool_gmail&color=green)

</div>

---

# Gmail Tool Package

A Swarmauri tool package for interacting with Gmail API, providing functionality to send and read emails.

## Installation

```bash
pip install swarmauri_tool_gmail
```

## Usage

### Sending Emails
```python
from swarmauri.tools.GmailSendTool import GmailSendTool

# Initialize the tool
send_tool = GmailSendTool(
    credentials_path="path/to/credentials.json",
    sender_email="your-email@example.com",
    service={"serviceName": "gmail", "version": "v1"}
)

# Send an email
result = send_tool(
    recipients="recipient@example.com",
    subject="Test Email",
    htmlMsg="<p>Hello, this is a test email!</p>"
)
```

### Reading Emails
```python
from swarmauri.tools.GmailReadTool import GmailReadTool

# Initialize the tool
read_tool = GmailReadTool(
    credentials_path="path/to/credentials.json",
    sender_email="your-email@example.com"
)

# Read unread emails
result = read_tool(query="is:unread", max_results=10)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

