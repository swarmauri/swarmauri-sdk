# Welcome to Swarmauri

![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/dm/swarmauri" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg"/></a>
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

---

## Introduction

Swarmauri SDK is a powerful toolkit for building AI-powered applications with a focus on modularity, extensibility, and ease of use.

!!! abstract "Key Features"
    - **📦 Modular Design**: Mix and match components to build custom AI solutions
    - **🔧 Extensive Tool Support**: Pre-built tools for common AI tasks
    - **🚀 High Performance**: Optimized for speed and efficiency
    - **🛡️ Type Safety**: Better development experience with Python's type system
    - **🌐 Cross-Platform**: Works on macOS, Windows, and Linux

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

??? info "Package Structure"
    === "Core"
        The `swarmauri_core` package contains the foundation classes and interfaces that define the SDK's architecture. These include:
        
        - Base interfaces for models, tools, and agents
        - Core data structures
        - Type definitions
        - Utility functions
        
        This package has minimal dependencies and establishes the contract for all other packages.
    
    === "Base"
        The `swarmauri_base` package provides abstract implementations of the core interfaces, including:
        
        - Abstract base classes for common components
        - Default implementations of interfaces
        - Common patterns and utilities
        
        This package depends only on `swarmauri_core`.
    
    === "Standard"
        The `swarmauri_standard` package includes concrete implementations ready for use:
        
        - Model integrations (OpenAI, Anthropic, etc.)
        - Tool implementations (Calculator, Web Search, etc.)
        - Agent implementations (Chat, Task, etc.)
        
        This package depends on both `swarmauri_core` and `swarmauri_base`.
    
    === "Swarmauri"
        The main `swarmauri` package brings everything together and provides:
        
        - Convenient imports from all packages
        - High-level abstractions
        - Ready-to-use components
        
        This is the package most users will interact with directly.

## Getting Started

Getting started with Swarmauri SDK is simple:

```console
pip install swarmauri
```

??? tip "Installation Options"    
    === "Installation with all dependencies"
        ```sh
        pip install "swarmauri[all]"
        ```
    
    === "Plugin Installation"
        ```sh
        pip install "swarmauri_<[resource kind]>_<name of package>"

        #Example
        pip install swarmauri_tool_gmail
        ```
    
    === "Development setup"
        ```sh
        pip install "swarmauri[dev]"
        ```

### Setting Up Environment Variables

Before using Swarmauri SDK, you need to set up your environment variables for API keys. You can do this by adding the following lines to your `.env` file or exporting them directly in your terminal:

```sh
export GROQ_API_KEY=your_api_key_here
```

Or, if you are using a `.env` file, add:

```env
GROQ_API_KEY=your_api_key_here
```

Make sure to replace `your_api_key_here` with your actual API key.

??? warning "API Key Security"
    Never commit your API keys to version control or share them publicly. Consider using environment variables or a secure secrets management solution in production environments.
    
    ```python
    # Recommended approach for loading API keys
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Access API key safely
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable")
    ```

### Example Usage

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

??? example "More Examples"
    === "RAG (Retrieval Augmented Generation)"
        ```python
        from swarmauri.agents.RagAgent import RagAgent
        from swarmauri.llms.OpenAIModel import OpenAIModel
        from swarmauri.documents.Document import Document
        from swarmauri.conversations.Conversation import Conversation
        from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
        import os

        # Create documents
        documents = [
            Document(content="Paris is the capital of France."),
            Document(content="Berlin is the capital of Germany."),
            Document(content="Rome is the capital of Italy.")
        ]

        # Initialize TfidfVectorStore
        vector_store = TfidfVectorStore()

        # Add documents to the vector store
        vector_store.add_documents(documents)

        # Create a conversation
        conversation = Conversation()

        # Create a RAG agent
        agent = RagAgent(
            llm=OpenAIModel(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY")),
            vector_store=vector_store,
            conversation=conversation
        )

        # Ask a question
        answer = agent.exec("What is the capital of France?")
        print(answer)
        ```
    
    === "Tool-augmented Agent"
        ```python
        import os
        from swarmauri_standard.llms.AnthropicModel import AnthropicModel
        from swarmauri_standard.tools.CalculatorTool import CalculatorTool
        from swarmauri_standard.tools.WeatherTool import WeatherTool
        from swarmauri_standard.toolkits.Toolkit import Toolkit
        from swarmauri_standard.agents.ToolAgent import ToolAgent
        from swarmauri_standard.conversations.Conversation import Conversation
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        # Initialize components
        llm = AnthropicModel(api_key=os.getenv("ANTHROPIC_API_KEY"))
        conversation = Conversation()
        toolkit = Toolkit()

        # Add tools to the toolkit
        calculator_tool = CalculatorTool()
        weather_tool = WeatherTool(api_key=os.getenv("WEATHER_API_KEY"))
        toolkit.add_tool(calculator_tool)
        toolkit.add_tool(weather_tool)

        # Create a tool-augmented agent
        agent = ToolAgent(llm=llm, conversation=conversation, toolkit=toolkit)

        # Ask the agent to perform calculations and check the weather
        response = agent.exec("What is 28 * 15? Also, what's the weather in New York?")
        print(response)  # Agent should use the calculator and weather tools to respond
        ```

## Community
### Join the Community

Need help? Have a feature suggestion? Join the Swarmauri community:

- [Join our Discord](https://discord.gg/swarmauri)
- [Connect on LinkedIn](https://linkedin.com/company/swarmauri)
- [Follow us on Twitter](https://twitter.com/swarmauri)

!!! success "Get Involved"
    We welcome contributions from developers of all experience levels! Here's how you can get involved:
    
    1. **Star the repository**: Show your support by starring the [GitHub repo](https://github.com/swarmauri/swarmauri-sdk)
    2. **Report issues**: Found a bug? Open an issue on GitHub
    3. **Submit PRs**: Contribute code improvements or new features
    4. **Share your projects**: Built something cool with Swarmauri? Share it with the community!
    5. **Help others**: Answer questions in our Discord server

### Get the Library

- **Swarmauri SDK Python**
    - [GitHub Repository](https://github.com/swarmauri/swarmauri-sdk)
    - [Documentation](https://docs.swarmauri.com)
    - [PyPI Package](https://pypi.org/project/swarmauri)

## Next Steps

Here are some recommended next steps to continue your journey with Swarmauri SDK:

1. **Explore the Courses**: Check out our [step-by-step courses](./guide/courses.md)
2. **Read the API Documentation**: Dive into our [detailed API reference](./api/concepts.md)
3. **Join the Community**: Connect with other developers in our [Discord server](https://discord.gg/swarmauri)
4. **Contribute**: Learn how to [contribute to the project](./home/contribute.md)
5. **Stay Updated**: Follow our [blog](./blog/index.md) for the latest updates

---

Need help? Join our [community forums](https://community.swarmauri.com) or [open an issue](https://github.com/swarmauri/swarmauri-sdk/issues) on GitHub.