# Welcome to Swarmauri

![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/dm/swarmauri" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk">
        <img src="https://img.shields.io/github/repo-size/swarmauri/swarmauri-sdk" alt="GitHub Repo Size"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/l/swarmauri" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri_core&color=green" alt="PyPI - swarmauri_core"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green" alt="PyPI - swarmauri"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri_community&color=yellow" alt="PyPI - swarmauri_community"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri_experimental&color=yellow" alt="PyPI - swarmauri_experimental"/></a>
</p>

## Introduction

Swarmauri SDK is a powerful toolkit for building AI-powered applications with a focus on modularity, extensibility, and ease of use.

## Why Use Swarmauri SDK?

Our SDK offers several compelling advantages:

- **Modular Architecture**: Build your AI applications using our plug-and-play components
- **Extensive Tool Support**: Access a wide range of pre-built tools for common AI tasks
- **Type Safety**: Built with Python's type system for better development experience
- **Enterprise Ready**: Production-tested components with robust error handling
- **Flexible Integration**: Works seamlessly with popular AI services and frameworks

## Overview

Swarmauri SDK consists of four main packages:

1. **Core** (`swarmauri_core`): Foundation classes and interfaces
2. **Base** (`swarmauri_base`): Abstract implementations and base classes
3. **Standard** (`swarmauri_standard`): Ready-to-use components and tools
4. **Swarmauri** (`swarmauri`): High-level package that brings everything together

## Getting Started

Getting started with Swarmauri SDK is simple:

```console

pip install swarmauri
```

## Usage

Here's a quick example of using Swarmauri SDK with a conversational agent:

```py
from swarmauri.llms import GroqModel
from swarmauri.conversations import Conversation
from swarmauri.agents import SimpleConversationAgent
import os

# Initialize the model
model = GroqModel(
    api_key=os.getenv("GROQ_API_KEY")
)
# Create a conversation
conversation = Conversation()
# Initialize the agent
agent = SimpleConversationAgent(
    conversation=conversation,
    llm=model
)
response = agent.exec("Tell me a joke about programming.")
print(response)

# Continue the conversation
follow_up = agent.exec("Explain that joke.")
print(follow_up)
```

This example demonstrates:
- Setting up a conversational agent
- Managing conversation state
- Generating contextual responses
- Using environment variables for API keys

## Community
### Join the Community

Need help? Have a feature suggestion? Join the Swarmauri community:

- [Join our Discord](https://discord.gg/swarmauri)
- [Connect on LinkedIn](https://linkedin.com/company/swarmauri)
- [Follow us on Twitter](https://twitter.com/swarmauri)

### Get the Library

- **Swarmauri SDK Python**
    - [GitHub Repository](https://github.com/swarmauri/swarmauri-sdk)
    - [Documentation](https://docs.swarmauri.com)
    - [PyPI Package](https://pypi.org/project/swarmauri)

## Next Steps

Here are some recommended next steps to continue your journey with Swarmauri SDK:

1. **Explore the Tutorials**: Check out our [step-by-step tutorials](../tutorials/index.md)
2. **Read the API Documentation**: Dive into our [detailed API reference](../api/index.md)
3. **Join the Community**: Connect with other developers in our [Discord server](https://discord.gg/swarmauri)
4. **Contribute**: Learn how to [contribute to the project](../contributing.md)
5. **Stay Updated**: Follow our [blog](../blog/index.md) for the latest updates

For more detailed information, visit our [comprehensive documentation](https://docs.swarmauri.com).

---

Need help? Join our [community forums](https://community.swarmauri.com) or [open an issue](https://github.com/swarmauri/swarmauri-sdk/issues) on GitHub.