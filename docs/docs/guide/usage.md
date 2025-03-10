# Usage Guide

Welcome to the Swarmauri SDK usage guide. This document will help you understand the basic usage patterns, common workflows, and best practices for using Swarmauri SDK.

## Basic Usage Patterns

### Initializing the SDK

To get started with Swarmauri SDK, you need to import the necessary modules and initialize the components you plan to use.

```python
from swarmauri_standard.conversations import Conversation
from swarmauri_standard.messages import HumanMessage
from swarmauri_standard.tool_llms import OpenAIToolModel

# Create a conversation
conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello, how can I help you today?"))

# Initialize an LLM with tool capabilities
llm = OpenAIToolModel(model="gpt-4-turbo")

# Generate a response
response = llm.predict(conversation=conversation)
print(response.get_last().content)
```

### Using Tools

Swarmauri SDK allows you to integrate various tools to enhance the capabilities of your AI models.

```python
from swarmauri_standard.tools import CalculatorTool, RequestsTool

# Initialize tools
calculator = CalculatorTool()
web_request = RequestsTool()

# Use the calculator tool
calc_result = calculator(operation="add", x=2, y=2)
print(f"Calculator Result: {calc_result['calculated_result']}")

# Use the web request tool
request_result = web_request(
    method="GET",
    url="https://api.example.com/data",
    headers={"Content-Type": "application/json"}
)
print(f"Request Result: {request_result}")
```

## Common Workflows

### Building an AI Assistant

Create a simple AI assistant that can handle multiple tasks using different tools.

```python
from swarmauri_standard.conversations import Conversation
from swarmauri_standard.messages import HumanMessage
from swarmauri_standard.agents import ToolAgent
from swarmauri_standard.tool_llms import OpenAIToolModel
from swarmauri_standard.toolkits import Toolkit
from swarmauri_standard.tools import CalculatorTool, RequestsTool, CodeInterpreterTool

# Create a conversation
conversation = Conversation()
conversation.add_message(HumanMessage(content="Can you help me analyze this dataset?"))

# Create a toolkit with various tools
toolkit = Toolkit(
    tools=[
        CalculatorTool(),
        RequestsTool(),
        CodeInterpreterTool()
    ]
)

# Create an agent with tools
agent = ToolAgent(
    llm=OpenAIToolModel(model="gpt-4-turbo"),
    toolkit=toolkit,
    conversation=conversation
)

# Generate a response
response = agent.exec("Can you calculate 25 * 4 and then fetch the weather for New York?")
print(response)
```

### Document Processing Pipeline

Set up a pipeline to process and analyze documents.

```python
from swarmauri_standard.pipelines import Pipeline
from swarmauri_standard.parsers import CSVParser
from swarmauri_standard.chunkers import TextSplitter
from swarmauri_standard.embeddings import OpenAIEmbedding
from swarmauri_standard.vector_stores import SqliteVectorStore

# Create a pipeline for document processing
pipeline = Pipeline([
    CSVParser(),
    TextSplitter(chunk_size=1000),
    OpenAIEmbedding(),
    SqliteVectorStore(db_path="documents.db")
])

# Process documents
result = pipeline.run("data.csv")
```

## Code Examples

### Example 1: Simple Chatbot

```python
from swarmauri_standard.conversations import Conversation
from swarmauri_standard.messages import HumanMessage, SystemMessage
from swarmauri_standard.tool_llms import OpenAIToolModel

# Create a conversation with a system message
conversation = Conversation()
conversation.add_message(SystemMessage(content="You are a helpful assistant."))
conversation.add_message(HumanMessage(content="What's the weather in New York?"))

# Create an LLM with tool capabilities
llm = OpenAIToolModel(model="gpt-4-turbo")

# Generate a response
response = llm.predict(conversation=conversation)
print(response.get_last().content)
```

### Example 2: Research Assistant

```python
from swarmauri_standard.agents import ToolAgent
from swarmauri_standard.conversations import Conversation
from swarmauri_standard.messages import SystemMessage
from swarmauri_standard.tool_llms import OpenAIToolModel
from swarmauri_standard.toolkits import Toolkit
from swarmauri_standard.tools import RequestsTool, CodeInterpreterTool

# Create a conversation with a system message for a research assistant
conversation = Conversation()
conversation.add_message(SystemMessage(content="You are a research assistant specialized in gathering and analyzing information."))

# Create a toolkit with research tools
toolkit = Toolkit(
    tools=[
        RequestsTool(),
        CodeInterpreterTool()
    ]
)

# Create a research agent
agent = ToolAgent(
    llm=OpenAIToolModel(model="gpt-4-turbo"),
    toolkit=toolkit,
    conversation=conversation
)

# Conduct research
research_result = agent.exec("What are the latest advancements in fusion energy?")
print(research_result)
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

### Modular Design

Leverage Swarmauri's modular architecture to build scalable and maintainable applications. Use only the components you need and extend them as required.

### Error Handling

Implement robust error handling to ensure your application can gracefully handle unexpected situations.

```python
try:
    response = llm.predict(conversation=conversation)
    print(response.get_last().content)
except Exception as e:
    print(f"An error occurred: {e}")
```

### Logging

Use logging to track the behavior of your application and debug issues.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting the AI assistant")
```

## Next Steps

After familiarizing yourself with the basic usage patterns and workflows, you can:

1. Explore more advanced features in our API Documentation
2. Check out our Examples for more use cases
3. Join our Community for support and collaboration

Need help? Visit our FAQ or reach out to our community resources.
