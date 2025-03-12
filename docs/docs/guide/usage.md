# Usage Guide

Welcome to the Swarmauri SDK usage guide. This document will help you understand the basic usage patterns, common workflows, and best practices for using Swarmauri SDK.

## Basic Usage Patterns

### Initializing the SDK

To get started with Swarmauri SDK, you need to import the necessary modules and initialize the components you plan to use.

```python
from swarmauri import Conversation, HumanMessage, OpenAIToolModel

# Create a conversation
conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello, how can I help you today?"))

# Initialize an LLM with tool capabilities
llm = OpenAIToolModel(model="gpt-4-turbo")

# Generate a response
response = llm.predict(conversation=conversation)
print(response.get_last().content)
```

!!! info "API Key Requirements"
    Remember that you'll need to set up your API key for OpenAI or any other LLM provider before initializing the models. This can be done through environment variables or configuration files.

### Using Tools

Swarmauri SDK allows you to integrate various tools to enhance the capabilities of your AI models.

```python
from swarmauri import CalculatorTool, RequestsTool

# Initialize tools
calculator = CalculatorTool()
web_request = RequestsTool()

# Use the calculator tool
calc_result = calculator(operation="add", x=2, y=2)
print(f"Calculator Result: {calc_result['calculated_result']}")

# Use the web request tool for a simple API call
request_result = web_request(
    method="GET",
    url="https://jsonplaceholder.typicode.com/todos/1"
)
print(f"Request Result: {request_result}")
```

!!! warning "Security Considerations"
    When using the `RequestsTool`, be careful with the URLs you allow it to access. Consider implementing URL validation or allowlists to prevent potential security risks.

## Common Workflows

### Building a Simple Chatbot

Create a basic chatbot that can respond to user queries.

```python
from swarmauri import Conversation, HumanMessage, SystemMessage, OpenAIModel

# Create a conversation with a system message
conversation = Conversation()
conversation.add_message(SystemMessage(content="You are a helpful assistant."))

# Initialize an LLM
llm = OpenAIModel(model="gpt-3.5-turbo")

# Function to handle user input
def chat_with_bot(user_input):
    # Add the user's message to the conversation
    conversation.add_message(HumanMessage(content=user_input))

    # Generate a response
    llm.predict(conversation=conversation)

    # Return the latest response
    return conversation.get_last().content

# Example usage
response = chat_with_bot("What is machine learning?")
print(response)
```

!!! tip "Conversation Management"
    For longer conversations, consider implementing a mechanism to trim the conversation history to avoid hitting token limits. You can either summarize previous exchanges or remove older messages.
    
    ```python
    # Example of trimming conversation history
    if len(conversation.messages) > 10:
        # Keep only the last 5 messages
        conversation.messages = conversation.messages[-5:]
    ```

### Using Tools with an LLM

Create an assistant that can use tools to answer questions.

```python
from swarmauri import Conversation, HumanMessage, SystemMessage, OpenAIToolModel, CalculatorTool, Toolkit

# Create a conversation
conversation = Conversation()
conversation.add_message(SystemMessage(content="You are a helpful assistant with access to tools."))

# Create a toolkit with a calculator
toolkit = Toolkit(
    tools=[CalculatorTool()]
)

# Initialize an LLM with tool capabilities
llm = OpenAIToolModel(model="gpt-4-turbo")

# Function to handle user input
def ask_with_tools(user_input):
    # Add the user's message to the conversation
    conversation.add_message(HumanMessage(content=user_input))

    # Generate a response using the toolkit
    llm.predict(conversation=conversation, toolkit=toolkit)

    # Return the latest response
    return conversation.get_last().content

# Example usage
response = ask_with_tools("What is 25 * 16?")
print(response)
```

## Code Examples

### Example 1: Question Answering

```python
from swarmauri import QAAgent, OpenAIModel, Conversation

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
from swarmauri import (
    RagAgent,
    OpenAIModel,
    OpenAIEmbedding,
    SqliteVectorStore,
    Document,
    Conversation
)

# Create documents
documents = [
    Document(content="Paris is the capital of France."),
    Document(content="Berlin is the capital of Germany."),
    Document(content="Rome is the capital of Italy.")
]

# Create a vector store and add documents
embedding_model = OpenAIEmbedding()
vector_store = SqliteVectorStore(embedding=embedding_model, db_path=":memory:")
vector_store.add_documents(documents)

# Create a conversation
conversation = Conversation()

# Create a RAG agent
agent = RagAgent(
    llm=OpenAIModel(model="gpt-3.5-turbo"),
    vector_store=vector_store,
    conversation=conversation
)

# Ask a question
answer = agent.exec("What is the capital of France?")
print(answer)
```

!!! note "In-Memory vs. Persistent Storage"
    The example above uses an in-memory SQLite database (`:memory:`) which is suitable for testing but not for production. For production applications, specify a file path to create a persistent vector store:
    
    ```python
    vector_store = SqliteVectorStore(
        embedding=embedding_model, 
        db_path="./data/vector_store.db"
    )
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

!!! tip "Requirements File"
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

!!! warning "Rate Limits"
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