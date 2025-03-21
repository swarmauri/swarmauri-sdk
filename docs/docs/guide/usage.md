# Usage Guide

Welcome to the Swarmauri SDK usage guide. This document will help you understand the basic usage patterns, common workflows, and best practices for using Swarmauri SDK.

## Basic Usage Patterns

### Initializing the SDK

To get started with Swarmauri SDK, you need to import the necessary modules and initialize the components you plan to use.

```python
from swarmauri.conversations.Conversation import Conversation
from swarmauri.messages.HumanMessage import HumanMessage
from swarmauri.tool_llms.OpenAIToolModel import OpenAIToolModel

# Create a conversation
conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello, how can I help you today?"))

# Initialize an LLM with tool capabilities
llm = OpenAIModel(model="gpt-4-turbo")

# Generate a response
response = llm.predict(conversation=conversation)
print(response.get_last().content)
```

!!! info "API Key Requirements"
    Remember that you'll need to set up your API key for OpenAI or any other LLM provider before initializing the models. This can be done through environment variables or configuration files.

### Using Tools

### Using Tools

Swarmauri SDK allows you to integrate various tools to enhance the capabilities of your AI models.

```python
from swarmauri.tools.CalculatorTool import CalculatorTool
from swarmauri.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri.toolkit.Toolkit import Toolkit
from swarmauri.conversations.Conversation import Conversation
from swarmauri.messages.HumanMessage import HumanMessage
import os

# Create a toolkit to hold our tools
toolkit = Toolkit()

# Initialize the calculator tool and add it to our toolkit
calculator_tool = CalculatorTool()
toolkit.add_tool(calculator_tool)

# Create a conversation object to manage the message history
conversation = Conversation()

# Prepare the user's input as a human message
input_data = "Add 512+671"
human_message = HumanMessage(content=input_data)

# Add the message to our conversation
conversation.add_message(human_message)

# Initialize the OpenAI Tool Model
openai_tool_model = OpenAIToolModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4-turbo"
)

# Generate a response using the model and toolkit
conversation = openai_tool_model.predict(conversation=conversation, toolkit=toolkit)

# Print the model's response
print(f"Response: {conversation.get_last().content}")
```

!!! warning "Security Considerations"
    When using the `RequestsTool`, be careful with the URLs you allow it to access. Consider implementing URL validation or allowlists to prevent potential security risks.

## Common Workflows

### Building a Simple Chatbot

Create a basic chatbot that can respond to user queries.

```python
from swarmauri.agents.SimpleConversationAgent import SimpleConversationAgent
from swarmauri.conversation.Conversation import Conversation
from swarmauri.messages.SystemMessage import SystemMessage
from swarmauri.llms.OpenAIModel import OpenAIModel

# Create a conversation with a system message
conversation = Conversation()
conversation.add_message(SystemMessage(content="You are a helpful assistant."))

# Initialize an LLM
llm = OpenAIModel(model="gpt-3.5-turbo")

# Create a simple conversation agent
agent = SimpleConversationAgent(conversation=conversation, llm=llm)

# Example usage
response = agent.exec("What is machine learning?")
print(response)

# Continue the conversation
response = agent.exec("Can you explain it in simpler terms?")
print(response)
```

### Using Tools with an LLM

Create an assistant that can use tools to answer questions.

### How do I use tools in Swarmauri SDK?

Swarmauri SDK allows you to integrate various tools to enhance the capabilities of your AI models.

```python
from swarmauri.agents.ToolAgent import ToolAgent
from swarmauri.conversations.Conversation import Conversation
from swarmauri.messages.SystemMessage import SystemMessage
from swarmauri.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri.tools.CalculatorTool import CalculatorTool
from swarmauri.toolkits.Toolkit import Toolkit

# Create a conversation with a system message
conversation = Conversation()
conversation.add_message(SystemMessage(content="You are a helpful assistant with access to tools."))

# Create a toolkit with a calculator
toolkit = Toolkit()
toolkit.add_tool(CalculatorTool())

# Initialize an LLM with tool capabilities
openai_tool_model = OpenAIToolModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4-turbo"
)
# Create a tool agent
agent = ToolAgent(conversation=conversation, llm=llm, toolkit=toolkit)

# Example usage
response = agent.exec("What is 25 * 16?")
print(response)

# Continue the conversation with another tool-based query
response = agent.exec("What is the square root of 144?")
print(response)
```

## Code Examples

### Example 1: Question Answering

```python
from swarmauri.agents.QAAgent import QAAgent
from swarmauri.llms.OpenAIModel import OpenAIModel
from swarrmauri.conversation.Conversation import Conversation

# Create a conversation
conversation = Conversation()

# Create a QA agent
agent = QAAgent(
    llm=OpenAIModel(model="gpt-3.5-turbo"),
    conversation=conversation
)

# Ask a question
answer = agent.exec("What is the capital of France?")
print(answer)
```

### Example 2: RAG (Retrieval-Augmented Generation)

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

??? note "TfidfVectorStore vs. Other Vector Stores"
    The `TfidfVectorStore` is a simple in-memory vector store that:

    - Doesn't require external services or API keys
    - Uses TF-IDF for document embeddings
    - Performs well for small to medium document collections
    - Doesn't persist data between application restarts

    For production applications with large document collections, consider other storage like:

    ```python
    # Pinecone for cloud-based storage
    from swarmauri_vectorstore_pinecone import PineconeVectorStore

    vector_store = PineconeVectorStore(
        api_key=os.getenv("PINECONE_API_KEY"),
        collection_name="my-collection",
        vector_size=1536
    )
    vector_store.connect()
    ```

## Best Practices

### Use Virtual Environments

Always use virtual environments to manage dependencies and avoid conflicts.

```bash
# Create a virtual environment
python -m venv swarmauri_env

# Activate the environment
# On macOS/Linux:
source swarmauri_env/bin/activate

# On Windows:
.\swarmauri_env\Scripts\activate

# Install Swarmauri SDK
pip install swarmauri
```

??? tip "Requirements File"
For team projects or deployments, consider creating a `requirements.txt` file to ensure consistent environments:

    ```bash
    # Generate requirements.txt
    pip freeze > requirements.txt

    # Install from requirements.txt
    pip install -r requirements.txt
    ```

### Error Handling

Implement robust error handling to ensure your application can gracefully handle unexpected situations.

```python
try:
    response = llm.predict(conversation=conversation)
    print(response.get_last().content)
except Exception as e:
    print(f"An error occurred: {e}")
```

??? warning "Rate Limits"
    When working with external API services like OpenAI, be aware of rate limits. Implement exponential backoff strategies for retries:

    ```python
    import time

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.predict(conversation=conversation)
            break  # Success, exit the retry loop
        except Exception as e:
            if attempt < max_retries - 1:
                # Wait with exponential backoff (1s, 2s, 4s, etc.)
                time.sleep(2 ** attempt)
                continue
            else:
                print(f"Failed after {max_retries} attempts: {e}")
    ```

### Logging

Use logging to track the behavior of your application and debug issues.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting the AI assistant")
```

!!! info "Structured Logging"
    For production applications, consider using structured logging for better searchability:

    ```python
    logger.info(
        "LLM response generated",
        extra={
            "tokens_used": response.usage.total_tokens,
            "response_time_ms": response_time,
            "model": "gpt-4-turbo"
        }
    )
    ```

## Next Steps

After familiarizing yourself with the basic usage patterns and workflows, you can:

1. Explore more advanced features in our API Documentation
2. Check out our Examples for more use cases
3. Join our Community for support and collaboration

Need help? Visit our FAQ or reach out to our community resources.
