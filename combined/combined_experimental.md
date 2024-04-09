```swarmauri/experimental/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/tools/LinkedInArticleTool.py

import requests
from ...standard.tools.base.ToolBase import ToolBase
from ...standard.tools.concrete.Parameter import Parameter

class LinkedInArticleTool(ToolBase):
    """
    A tool to post articles on LinkedIn using the LinkedIn API.
    """
    def __init__(self, access_token):
        """
        Initializes the LinkedInArticleTool with the necessary access token.
        
        Args:
            access_token (str): The OAuth access token for authenticating with the LinkedIn API.
        """
        super().__init__(name="LinkedInArticleTool",
                         description="A tool for posting articles on LinkedIn.",
                         parameters=[
                             Parameter(name="title", type="string", description="The title of the article", required=True),
                             Parameter(name="text", type="string", description="The body text of the article", required=True),
                             Parameter(name="visibility", type="string", description="The visibility of the article", required=True, enum=["anyone", "connectionsOnly"])
                         ])
        self.access_token = access_token
        
    def __call__(self, title: str, text: str, visibility: str = "anyone") -> str:
        """
        Posts an article on LinkedIn.

        Args:
            title (str): The title of the article.
            text (str): The body text of the article.
            visibility (str): The visibility of the article, either "anyone" or "connectionsOnly".

        Returns:
            str: A message indicating the success or failure of the post operation.
        """
        # Construct the request URL and payload according to LinkedIn API documentation
        url = 'https://api.linkedin.com/v2/ugcPosts'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "author": "urn:li:person:YOUR_PERSON_ID_HERE",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": title
                            },
                            "originalUrl": "URL_OF_THE_ARTICLE_OR_IMAGE",
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
            }
        }
     
        # Make the POST request to LinkedIn's API
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return f"Article posted successfully: {response.json().get('id')}"
        else:
            return f"Failed to post the article. Status Code: {response.status_code} - {response.text}"

```

```swarmauri/experimental/tools/TwitterPostTool.py

from tweepy import Client

from ...standard.tools.base.ToolBase import ToolBase
from ...standard.tools.concrete.Parameter import Parameter

class TwitterPostTool(ToolBase):
    def __init__(self, bearer_token):
        # Initialize parameters necessary for posting a tweet
        parameters = [
            Parameter(
                name="status",
                type="string",
                description="The status message to post on Twitter",
                required=True
            )
        ]
        
        super().__init__(name="TwitterPostTool", description="Post a status update on Twitter", parameters=parameters)
        
        # Initialize Twitter API Client
        self.client = Client(bearer_token=bearer_token)

    def __call__(self, status: str) -> str:
        """
        Posts a status on Twitter.

        Args:
            status (str): The status message to post.

        Returns:
            str: A confirmation message including the tweet's URL if successful.
        """
        try:
            # Using Tweepy to send a tweet
            response = self.client.create_tweet(text=status)
            tweet_id = response.data['id']
            # Constructing URL to the tweet - Adjust the URL to match Twitter API v2 structure if needed
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            return f"Tweet successful: {tweet_url}"
        except Exception as e:
            return f"An error occurred: {e}"

```

```swarmauri/experimental/tools/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/tools/OutlookSendMailTool.py

import requests
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter


class OutlookSendMailTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="recipient",
                type="string",
                description="The email address of the recipient",
                required=True
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True
            ),
            Parameter(
                name="body",
                type="string",
                description="The HTML body of the email",
                required=True
            )
        ]
        
        super().__init__(name="OutlookSendMailTool", 
                         description="Sends an email using the Outlook service.",
                         parameters=parameters)

        # Add your Microsoft Graph API credentials and endpoint URL here
        self.tenant_id = "YOUR_TENANT_ID"
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def get_access_token(self):
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.scope),
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json().get("access_token")

    def __call__(self, recipient, subject, body):
        access_token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient
                        }
                    }
                ]
            }
        }

        send_mail_endpoint = f"{self.graph_endpoint}/users/{self.client_id}/sendMail"
        response = requests.post(send_mail_endpoint, json=email_data, headers=headers)
        if response.status_code == 202:
            return "Email sent successfully"
        else:
            return f"Failed to send email, status code {response.status_code}"

```

```swarmauri/experimental/tools/CypherQueryTool.py

from ..base.ToolBase import ToolBase
from .Parameter import Parameter
from neo4j import GraphDatabase
import json

class CypherQueryTool(ToolBase):
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        
        # Define only the 'query' parameter since uri, user, and password are set at initialization
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="The Cypher query to execute.",
                required=True
            )
        ]
        
        super().__init__(name="CypherQueryTool",
                         description="Executes a Cypher query against a Neo4j database.",
                         parameters=parameters)

    def _get_connection(self):
        return GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def __call__(self, query) -> str:
        # Establish connection to the database
        driver = self._get_connection()
        session = driver.session()

        # Execute the query
        result = session.run(query)
        records = result.data()

        # Close the connection
        session.close()
        driver.close()

        # Convert records to JSON string, assuming it's JSON serializable
        return json.dumps(records)

```

```swarmauri/experimental/tools/FileDownloaderTool.py

import requests
from ....core.tools.ToolBase import ToolBase
from ....core.tools.Parameter import Parameter


class FileDownloaderTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the file to download",
                required=True
            )
        ]
        
        super().__init__(name="FileDownloaderTool",
                         description="Downloads a file from a specified URL into memory.",
                         parameters=parameters)
    
    def __call__(self, url: str) -> bytes:
        """
        Downloads a file from the given URL into memory.
        
        Parameters:
        - url (str): The URL of the file to download.
        
        Returns:
        - bytes: The content of the downloaded file.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the request resulted in an error
            return response.content
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download file from '{url}'. Error: {e}")

```

```swarmauri/experimental/tools/SQLite3QueryTool.py

import sqlite3
from ...base.ToolBase import ToolBase
from ...concrete.Parameter import Parameter

class SQLite3QueryTool(ToolBase):
    def __init__(self, db_name: str):
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="SQL query to execute",
                required=True
            )
        ]
        super().__init__(name="SQLQueryTool", 
                         description="Executes an SQL query and returns the results.", 
                         parameters=parameters)
        self.db_name = db_name

    def __call__(self, query) -> str:
        """
        Execute the provided SQL query.

        Parameters:
        - query (str): The SQL query to execute.

        Returns:
        - str: The results of the SQL query as a string.
        """
        try:
            connection = sqlite3.connect(self.db_name)  # Connect to the specific database file
            cursor = connection.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            result = "\n".join(str(row) for row in rows)
        except Exception as e:
            result = f"Error executing query: {e}"
        finally:
            connection.close()
        
        return f"Query Result:\n{result}"

```

```swarmauri/experimental/conversations/__init__.py



```

```swarmauri/experimental/conversations/SemanticConversation.py

from abc import ABC, abstractmethod
from typing import Callable, Dict, Union
from ...core.messages.IMessage import IMessage
from ...core.conversations.IConversation import IConversation

class SemanticConversation(IConversation, ABC):
    """
    A concrete implementation of the Conversation class that includes semantic routing.
    Semantic routing involves analyzing the content of messages to understand their intent
    or category and then routing them to appropriate handlers based on that analysis.

    This class requires subclasses to implement the _analyze_message method for semantic analysis.
    """


    @abstractmethod
    def register_handler(self, category: str, handler: Callable[[IMessage], None]):
        """
        Registers a message handler for a specific semantic category.

        Args:
            category (str): The category of messages this handler should process.
            handler (Callable[[Message], None]): The function to call for messages of the specified category.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and routes it to the appropriate handler based on its semantic category.

        Args:
            message (Message): The message to be added and processed.
        """
        pass

    @abstractmethod
    def _analyze_message(self, message: IMessage) -> Union[str, None]:
        """
        Analyzes the content of a message to determine its semantic category.

        This method must be implemented by subclasses to provide specific logic for semantic analysis.

        Args:
            message (Message): The message to analyze.

        Returns:
            Union[str, None]: The semantic category of the message, if determined; otherwise, None.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the _analyze_message method to provide semantic analysis.")

    # Additional methods as needed for message retrieval, history management, etc., inherited from Conversation

```

```swarmauri/experimental/conversations/ConsensusBuildingConversation.py

from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages.IMessage import IMessage


class ConsensusBuildingMessage(IMessage):
    def __init__(self, sender_id: str, content: str, message_type: str):
        self._sender_id = sender_id
        self._content = content
        self._role = 'consensus_message'
        self._message_type = message_type

    @property
    def role(self) -> str:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    def as_dict(self) -> dict:
        return {
            "sender_id": self._sender_id,
            "content": self._content,
            "message_type": self._message_type
        }


class ConsensusBuildingConversation(IConversation):
    def __init__(self, topic: str, participants: list):
        self.topic = topic
        self.participants = participants  # List of agent IDs
        self._history = []  # Stores all messages exchanged in the conversation
        self.proposal_votes = {}  # Tracks votes for each proposal

    @property
    def history(self) -> list:
        return self._history

    def add_message(self, message: IMessage):
        if not isinstance(message, ConsensusBuildingMessage):
            raise ValueError("Only instances of ConsensusBuildingMessage are accepted")
        self._history.append(message)

    def get_last(self) -> IMessage:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self) -> None:
        self._history.clear()

    def as_dict(self) -> list:
        return [message.as_dict() for message in self._history]

    def initiate_consensus(self, initiator_id: str, proposal=None):
        """Starts the conversation with an initial proposal, if any."""
        initiate_message = ConsensusBuildingMessage(initiator_id, proposal, "InitiateConsensusMessage")
        self.add_message(initiate_message)

    def add_proposal(self, sender_id: str, proposal: str):
        """Adds a proposal to the conversation."""
        proposal_message = ConsensusBuildingMessage(sender_id, proposal, "ProposalMessage")
        self.add_message(proposal_message)

    def add_comment(self, sender_id: str, comment: str):
        """Adds a comment or feedback regarding a proposal."""
        comment_message = ConsensusBuildingMessage(sender_id, comment, "CommentMessage")
        self.add_message(comment_message)

    def vote(self, sender_id: str, vote: str):
        """Registers a vote for a given proposal."""
        vote_message = ConsensusBuildingMessage(sender_id, vote, "VoteMessage")
        self.add_message(vote_message)
        # Count the vote
        self.proposal_votes[vote] = self.proposal_votes.get(vote, 0) + 1

    def check_agreement(self):
        """
        Checks if there is a consensus on any proposal.
        A simple majority (>50% of the participants) is required for consensus.
        """
        consensus_threshold = len(self.participants) / 2  # Define consensus as a simple majority

        for proposal, votes in self.proposal_votes.items():
            if votes > consensus_threshold:
                # A consensus has been reached
                return True, f"Consensus reached on proposal: {proposal} with {votes} votes."

        # If no consensus is reached
        return False, "No consensus reached."

```

```swarmauri/experimental/conversations/ConsensusBuildingConversation.md

show an example implementation with a ConsensusBuildingConversation, 3 swarm agents with openaimodels that use gpt-4-0125-preview, and a prompttemplate that is used to start their consensus. the prompttemplate should trigger the first agent to make a proposal to solve a task.
To create a ConsensusBuildingConversation scenario with 3 Swarm Agents utilizing OpenAI models based on GPT-4 and initiating the conversation with a PromptTemplate to solve a task, let's structure it step-by-step. We'll start by defining the necessary components:

1. **ConsensusBuildingConversation** - Manages the flow of messages and consensus building among agents.
2. **Swarm Agents** - Three agents equipped with GPT-4-based models, OpenAIToolModel, to generate proposals and participate in consensus.
3. **PromptTemplate** - Used to kickstart the conversation with a specific task.

Here's an example implementation in Python:

```python
# File: OpenAIToolModel.py
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict
from openai import OpenAI

class OpenAIToolModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "gpt-4-0125-preview"):
        super().__init__(model_name)
        self.client = OpenAI(api_key=api_key)

    def predict(self, prompt: str) -> str:
        response = self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].text.strip()

# File: swarmauri/standard/prompts/concrete/PromptTemplate.py (already provided in the defined implementation)
from ..base.PromptBase import PromptBase

class PromptTemplate(PromptBase):
    def __init__(self, template: str = "", variables: Dict[str, str] = {}):
        super().__init__(template, variables)

    def __call__(self, variables: Dict[str, str] = {}):
        formatted_prompt = self.template.format(**variables)
        return formatted_prompt

# File: ConsensusBuildingConversation.py (provided in the example)
# Implementation of `ConsensusBuildingConversation` with method `initiate_consensus` to start the conversation

# Define Swarm Agents with OpenAIToolModel
class SwarmAgent:
    def __init__(self, model):
        self.model = model

    def contribute_to_conversation(self, prompt):
        proposal = self.model.predict(prompt)
        return proposal

# Set up PromptTemplate for initiating the consensus
task_description = "Solve the problem of efficiently distributing vaccines in a fair manner."
prompt_template = PromptTemplate(template="How should we approach: {task}?", variables={"task": task_description})

# Initialize OpenAI Models for each Agent (fake API key for demonstration)
api_key = "your_openai_api_key"
agent1 = SwarmAgent(OpenAIToolModel(api_key))
agent2 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant1"))
agent3 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant2"))

# Start the conversation with a task
initiating_prompt = prompt_template()
print(f"Initiating Prompt: {initiating_prompt}")

# Agent 1 makes the first proposal
first_proposal = agent1.contribute_to_conversation(initiating_prompt)
print(f"Agent 1 proposes: {first_proposal}")

# From here, you could continue the flow where Agent 2 and 3 provide feedback, additional proposals,
# and the conversation is steered towards building consensus as per `ConsensusBuildingConversation` logic.

```

In this example:
- We initialize three agents with the `OpenAIToolModel`, configured to use a GPT-4 model (assuming the `gpt-4-0125-preview` identifier and variants are placeholders for actual GPT-4 model identifiers).
- A `PromptTemplate` is defined and used to kickstart the conversation by generating an initiating prompt.
- Agent 1 reads the initiating prompt and makes the first proposal towards solving the task.
- Next steps (not fully implemented) involve other agents reacting to the proposal, contributing their ideas, and the group collectively moving towards a consensus.

This example provides a starting point. The actual consensus logic, including how proposals are voted on and a consensus is reached, would need to be implemented within the `ConsensusBuildingConversation` logic using methods such as `add_proposal`, `add_comment`, and `check_agreement`.

?  show the rest of the consensusbuildingconversation
Building upon the initial setup, we'll now flesh out the rest of the `ConsensusBuildingConversation` to demonstrate how agents might engage in a consensus-driven discussion, leveraging their unique capabilities or viewpoints generated by their respective GPT-4 models. This extension will include methods for agents to add proposals, comments, and votes, along with the mechanism to check for and reach consensus.

### Step 1: Expansion of ConsensusBuildingMessage and Conversation Classes

We'll start with expanding the `ConsensusBuildingMessage` type for various message kinds, and then work on the conversation logic to incorporate consensus mechanisms.

```python
# Considering ConsensusBuildingMessage and SharedConversation classes are defined,
# let's elaborate on different message types: Proposal and Comment.

class ConsensusBuildingMessage:
    def __init__(self, sender_id: str, content: str, message_type: str = "proposal"):
        self.sender_id = sender_id
        self.content = content
        self.type = message_type  # can be 'proposal', 'comment', or 'vote'
    
    def __str__(self):
        return f"[{self.type.upper()} by {self.sender_id}]: {self.content}"
```

### Step 2: Adding Proposals, Comments, and Votes

Now, let's implement functionalities for agents to add proposals, comments, and how the conversation tracks votes to reach a consensus.

```python
class ConsensusBuildingConversation:
    def __init__(self):
        self.messages = []
        self.votes = {}

    def add_message(self, message: ConsensusBuildingMessage):
        print(str(message))
        self.messages.append(message)
        if message.type == "vote":
            self.votes[message.content] = self.votes.get(message.content, 0) + 1

    def initiate_consensus(self, task_description):
        initiate_message = ConsensusBuildingMessage("admin", task_description, "task")
        self.add_message(initiate_message)

    def add_proposal(self, agent_id, proposal):
        proposal_message = ConsensusBuildingMessage(agent_id, proposal, "proposal")
        self.add_message(proposal_message)

    def add_comment(self, agent_id, comment):
        comment_message = ConsensusBuildingMessage(agent_id, comment, "comment")
        self.add_message(comment_message)

    def vote(self, agent_id, proposal):
        vote_message = ConsensusBuildingMessage(agent_id, proposal, "vote")
        self.add_message(vote_message)

    def check_agreement(self):
        consensus_threshold = 2  # For simplicity, consensus is reached if at least two votes match
        for proposal, count in self.votes.items():
            if count >= consensus_threshold:
                return True, proposal
        return False, ""
```

### Step 3: Running the Consensus-Building Process

Finally, you can simulate agents engaging in the conversation, proposing ideas, commenting, and eventually voting on proposals.

```python
# Initialize the conversation process
conversation = ConsensusBuildingConversation()
task = "Enhancing the efficiency of urban transportation systems."
conversation.initiate_consensus(task)

# Simulate agents contributing to the conversation
conversation.add_proposal("Agent1", "Proposal 1: Implement a dynamic routing system for public transportation.")
conversation.add_comment("Agent2", "Comment: Support Proposal 1 with smart traffic management.")
conversation.add_proposal("Agent3", "Proposal 2: Increase investment in bike-sharing infrastructure.")

# Voting on the proposals
conversation.vote("Agent1", "Proposal 1")
conversation.vote("Agent2", "Proposal 1")
conversation.vote("Agent3", "Proposal 2")

# Check and declare consensus
consensus_reached, consensus_proposal = conversation.check_agreement()
if consensus_reached:
    print(f"Consensus Reached on: {consensus_proposal}")
else:
    print("No Consensus Reached.")
```

This code simulates the process where three agents discuss a task, propose strategies, comment on proposals, and vote to decide on the best approach. A consensus is reported if at least two agents agree on a specific proposal.

This illustrative example focuses on the mechanics of the conversation and consensus process among agents using pre-defined roles and behaviors. In a real-world application, the agents’ contributions would be dynamically generated responses from the GPT-4 AI model based on the prompt provided, accounting for more complex interactions and decision-making processes.

?  show an example implementation with a ConsensusBuildingConversation, 3 swarm agents with openaimodels that use gpt-4-0125-preview, and a prompttemplate that is used to start their consensus. the prompttemplate should trigger the first agent to make a proposal to solve a task. show the complete conversation flow from first proposal to voting to reaching consensus.
To illustrate a complete flow from proposal generation to consensus within a simulated environment using 3 swarm agents, each equipped with an OpenAI GPT-4 model, and a PromptTemplate to kick-start their conversation, we'll set up a structured example. This example will encompass initiating discussions, generating proposals based on the first prompt, allowing agents to respond, and finally voting to reach consensus on how to proceed. 

Let's begin:

### 1. Defining the Base Setup

First, we define our setup, assuming the `OpenAIToolModel`, `PromptTemplate`, `ConsensusBuildingConversation`, and `ConsensusBuildingMessage` are implemented as previously described.

### 2. Initializing the Environment

```python
api_key = "your_openai_api_key"

# Defining three agents with their respective OpenAI models focused on a "gpt-4-0125-preview" and its variants
agent1 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview"))
agent2 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant1"))
agent3 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant2"))

# The task to be solved, initiating the conversation
task_description = "Devise an innovative strategy to improve global literacy rates."
prompt_template = PromptTemplate(template="Initial approach to address: {task}?", variables={"task": task_description})

# Creating the conversation object
conversation = ConsensusBuildingConversation(topic="Global Literacy Strategy", participants=["agent1", "agent2", "agent3"])
```

### 3. Conducting the Conversation

Agent 1 kicks off the conversation:

```python
initiating_prompt = prompt_template()
print(f"Agent 1 Initiating: {initiating_prompt}")

# Agent 1 makes the first proposal based on received prompt
first_proposal = agent1.contribute_to_conversation(initiating_prompt)
conversation.initiate_consensus(initiating_prompt)
conversation.add_proposal("agent1", first_proposal)

# Assume Agent 2 and 3 generate their responses based on the initial proposal
response_agent2 = agent2.contribute_to_conversation("Commenting on the first proposal: " + first_proposal)
conversation.add_comment("agent2", response_agent2)

response_agent3 = agent3.contribute_to_conversation("Suggest an alternative strategy to " + first_proposal)
conversation.add_proposal("agent3", response_agent3)
```

### 4. Voting Phase and Checking for Consensus

After discussion, it's time to vote on the proposed strategies. For simplicity, let's simulate the voting:

```python
# Voting - let's say Agent 2 supports Agent 1's initial proposal, and Agent 3 remains with its own.
conversation.vote("agent2", "Proposal from agent1")
conversation.vote("agent3", "Proposal from agent3")

# Agent 1 votes for its own proposal to push the example towards consensus
conversation.vote("agent1", "Proposal from agent1")
```

### 5. Reaching Consensus

We check whether the consensus has been reached following the votes.

```python
is_agreement, agreement_message = conversation.check_agreement()

if is_agreement:
    print(f"Consensus Reached: {agreement_message}")
else:
    print("The agents could not reach a consensus.")
```

### Notes:

- The actual text for proposals and comments generated will be based on GPT-4 responses to prompts crafted from the conversation context, which can include the initial task and responses from other agents.
- To fully implement this scenario, you'd need access to the OpenAI API with the specified GPT-4 model versions or adjust the model identifiers according to available versions.
- Voting logic in this example is simplified for clarity. In practice, each agent's decision-making process to vote could also be informed by additional GPT-4 generated insights or predefined logic.

This example outlines how swarm intelligence could function in a collaborative task-solving context, demonstrating the concept of consensus-building in multi-agent systems using AI-driven decision-making.

?  we need a mechanism for talking to the agent's exec function so that we can get the agent's vote. additionally we need a function so that we can parse the agent's vote and determine which proposal the agent is voting for
To facilitate the agents' ability to vote and parse these votes effectively, we will enhance our agent setup with a mechanism to communicate votes and a function to parse these votes to understand which proposal an agent is voting for. This involves two key enhancements:

1. **Adding Voting Capability to the Agent's `exec` Function**: The `exec` function will be extended to process input for making a proposal, commenting, or voting. Based on the context or the content of the input, the agent will decide whether to propose a new solution, comment on existing proposals, or vote for the best proposal.

2. **Vote Parsing Function**: A function to parse the agent's response to extract the vote. This function will analyze the agent's text response to determine which proposal the agent supports.

Here's how these enhancements can be implemented:

### Updating the Swarm Agent

The `SwarmAgent` class is extended to include a decision-making capability for voting. This example does not directly integrate OpenAI's GPT-4 because of the complexity and access requirements. However, it demonstrates how you might structure these capabilities.

```python
class SwarmAgent:
    def __init__(self, model, agent_id):
        self.model = model
        self.agent_id = agent_id

    def exec(self, context):
        """
        Process the given context and decide on making a proposal, comment, or casting a vote.
        """
        # Example: Decide based on context (This should be replaced with actual model invocation)
        if "proposal" in context:
            response = self.model.predict(context)
            return response
        elif "vote" in context:
            # Simulate decision making for voting
            vote = self.decide_vote(context)
            return vote
        else:
            return "I need more information."

    def decide_vote(self, context):
        """
        Simulate an analysis to decide on voting - in practice, this could involve analyzing proposals with the model.
        """
        # Dummy logic for demonstration - replace with genuine analysis based on model prediction or explicit logic
        if "Proposal from agent1" in context:
            return "Proposal from agent1"
        else:
            return "Undecided"

    def contribute_to_conversation(self, prompt):
        proposal = self.exec(prompt)
        return proposal
```

### Implementing Vote Parsing

A function is created to parse the explicit vote from an agent's response. This function identifies which proposal the agent supports based on its text response.

```python
def parse_agent_vote(agent_response):
    """
    Parses the agent's text response to extract the vote.

    Parameters:
    agent_response (str): The agent's response text from which to extract the vote.

    Returns:
    str: The extracted vote indicating the supported proposal.
    """
    # Example parsing logic
    if "Proposal from agent1" in agent_response:
        return "Proposal from agent1"
    elif "Proposal from agent2" in agent_response:
        return "Proposal from agent2"
    elif "Proposal from agent3" in agent_response:
        return "Proposal from agent3"
    return "Undecided"
```

### Example Usage

Assuming the conversation and proposals have been initiated and it’s time to vote:

```python
# Assuming the context for voting includes all proposals
voting_context = "Please vote on the proposals: Proposal from agent1, Proposal from agent2, Proposal from agent3"

# Each agent votes
for agent in [agent1, agent2, agent3]:
    agent_vote = agent.exec(voting_context)
    parsed_vote = parse_agent_vote(agent_vote)
    # Add the parsed vote to the conversation
    conversation.vote(agent.agent_id, parsed_vote)

# Check for consensus
is_agreement, agreement_message = conversation.check_agreement()
print(f"Consensus Reached: {is_agreement}, with agreement on: {agreement_message}" if is_agreement else "No consensus reached.")
```

This structure and mechanisms allow agents to make informed decisions based on the context provided, such as proposals made by other agents, and provide a manageable way to parse these decisions to understand voting preferences better. In a real-world scenario, the decision-making process (`decide_vote`) and vote parsing should be enhanced to intelligently analyze the conversation context and proposals to determine the agent's stance accurately.

```

```swarmauri/experimental/models/__init__.py



```

```swarmauri/experimental/models/SageMaker.py

import json
import boto3
from ...core.models.IModel import IModel


class AWSSageMakerModel(IModel):
    def __init__(self, access_key: str, secret_access_key: str, region_name: str, model_name: str):
        """
        Initialize the AWS SageMaker model with AWS credentials, region, and the model name.

        Parameters:
        - access_key (str): AWS access key ID.
        - secret_access_key (str): AWS secret access key.
        - region_name (str): The region where the SageMaker model is deployed.
        - model_name (str): The name of the SageMaker model.
        """
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.client = boto3.client('sagemaker-runtime',
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_access_key,
                                   region_name=region_name)
        super().__init__(model_name)

    def predict(self, payload: str, content_type: str='application/json') -> dict:
        """
        Generate predictions using the AWS SageMaker model.

        Parameters:
        - payload (str): Input data in JSON format.
        - content_type (str): The MIME type of the input data (default: 'application/json').
        
        Returns:
        - dict: The predictions returned by the model.
        """
        endpoint_name = self.model_name  # Assuming the model name is also the endpoint name
        response = self.client.invoke_endpoint(EndpointName=endpoint_name,
                                               Body=payload,
                                               ContentType=content_type)
        result = json.loads(response['Body'].read().decode())
        return result

```

```swarmauri/experimental/models/HierarchicalAttentionModel.py

import tensorflow as tf
from swarmauri.core.models.IModel import IModel
from typing import Any

class HierarchicalAttentionModel(IModel):
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None  # This will hold the TensorFlow model with attention

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str) -> None:
        self._model_name = value

    def load_model(self) -> None:
        """
        Here, we define and compile the TensorFlow model described earlier.
        """
        # The following code is adapted from the attention model example provided earlier
        vocab_size = 10000  # Size of the vocabulary
        embedding_dim = 256  # Dimension of the embedding layer
        sentence_length = 100  # Max length of a sentence
        num_sentences = 10  # Number of sentences in a document
        units = 128  # Dimensionality of the output space of GRU
        
        # Word-level attention layer
        word_input = tf.keras.layers.Input(shape=(sentence_length,), dtype='int32')
        embedded_word = tf.keras.layers.Embedding(vocab_size, embedding_dim)(word_input)
        word_gru = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(units, return_sequences=True))(embedded_word)
        word_attention_layer = tf.keras.layers.Attention(use_scale=True, return_attention_scores=True)
        word_attention_output, word_attention_weights = word_attention_layer([word_gru, word_gru], return_attention_scores=True)
        word_encoder_with_attention = tf.keras.Model(inputs=word_input, outputs=[word_attention_output, word_attention_weights])
        
        # Sentence-level attention layer
        sentence_input = tf.keras.layers.Input(shape=(num_sentences, sentence_length), dtype='int32')
        sentence_encoder_with_attention = tf.keras.layers.TimeDistributed(word_encoder_with_attention)(sentence_input)
        sentence_gru = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(units, return_sequences=True))(sentence_encoder_with_attention[0])
        sentence_attention_layer = tf.keras.layers.Attention(use_scale=True, return_attention_scores=True)
        sentence_attention_output, sentence_attention_weights = sentence_attention_layer([sentence_gru, sentence_gru], return_attention_scores=True)
        doc_representation = tf.keras.layers.Dense(units, activation='tanh')(sentence_attention_output)
        
        # Classifier
        classifier = tf.keras.layers.Dense(1, activation='sigmoid')(doc_representation)
        
        # The model
        self._model = tf.keras.Model(inputs=sentence_input, outputs=[classifier, sentence_attention_weights])
        self._model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def predict(self, input_data: Any) -> Any:
        """
        Predict method to use the loaded model for making predictions.

        This example assumes `input_data` is preprocessed appropriately for the model's expected input.
        """
        if self._model is None:
            raise ValueError("Model is not loaded. Call `load_model` before prediction.")
            
        # Predicting with the model
        predictions, attention_weights = self._model.predict(input_data)
        
        # Additional logic to handle and package the predictions and attention weights could be added here
        
        return predictions, attention_weights

```

```swarmauri/experimental/utils/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/utils/get_last_frame.py

import inspect

def child_function(arg):
    # Get the stack frame of the caller
    caller_frame = inspect.currentframe().f_back
    # Get the name of the caller function
    caller_name = caller_frame.f_code.co_name
    # Inspect the arguments of the caller function
    args, _, _, values = inspect.getargvalues(caller_frame)
    # Assuming the caller has only one argument for simplicity
    arg_name = args[0]
    arg_value = values[arg_name]
    print(f"Caller Name: {caller_name}, Argument Name: {arg_name}, Argument Value: {arg_value}")

def caller_function(l):
    child_function(l)

# Example usage
caller_function("Hello")



```

```swarmauri/experimental/utils/save_schema.py

import inspect
import random

class Storage:
    def __init__(self):
        self.logs = []

    def log(self, log_data):
        self.logs.append(log_data)

    def print_logs(self):
        for log in self.logs:
            print(log)

class Loggable:
    def __init__(self, name, storage):
        self.name = name
        self.storage = storage

    def log_call(self, *args, **kwargs):
        # Inspect the call stack to get the caller's details
        caller_frame = inspect.stack()[2]
        caller_name = inspect.currentframe().f_back.f_code.co_name
        #caller_name = caller_frame.function
        module = inspect.getmodule(caller_frame[0])
        module_name = module.__name__ if module else 'N/A'

        # Log all relevant details
        log_data = {
            'caller_name': caller_name,
            'module_name': module_name,
            'called_name': self.name,
            'called_function': caller_frame[3], # The function in which log_call was invoked
            'args': args,
            'kwargs': kwargs
        }
        self.storage.log(log_data)

class Caller(Loggable):
    def __init__(self, name, storage, others):
        super().__init__(name, storage)
        self.others = others

    def __call__(self, *args, **kwargs):
        if len(self.storage.logs)<10:
            self.log_call(*args, **kwargs)
            # Randomly call another without causing recursive calls
            if args:  # Ensures it's not the first call without actual target
                next_caller_name = random.choice([name for name in self.others if name != self.name])
                self.others[next_caller_name](self.name)

# Initialize storage and callers
storage = Storage()
others = {}

# Creating callers
alice = Caller('Alice', storage, others)
bob = Caller('Bob', storage, others)
charlie = Caller('Charlie', storage, others)
dan = Caller('Dan', storage, others)

others['Alice'] = alice
others['Bob'] = bob
others['Charlie'] = charlie
others['Dan'] = dan

# Simulate the calls
dan(1, taco=23)

# Print the logs
storage.print_logs()


```

```swarmauri/experimental/utils/ISerializable.md

Creating a system that allows for the serialization of object interactions, along with enabling replay and modification of replay schemas in Python, involves several key steps. This process includes capturing the execution state, serializing it, and then providing mechanisms for replay and modification. Here's how you could implement such a system:

### Step 1: Define Serializable Representations
For each class that participates in the interaction, define a method to serialize its state to a dictionary or a similar serializable format. Additionally, include a method to instantiate an object from this serialized state.

```python
class Serializable:
    def serialize(self):
        raise NotImplementedError("Serialization method not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Deserialization method not implemented")
```

Implement these methods in your classes. For example:

```python
class ToolAgent(Serializable):
    def serialize(self):
        # Simplified example, adapt according to actual attributes
        return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

    @classmethod
    def deserialize(cls, data):
        # This method should instantiate the object based on the serialized state.
        # Example assumes the presence of model_name in the serialized state.
        model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
        return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration
```

### Step 2: Capture Executions
Capture executions and interactions by logging or emitting events, including serialized object states and method invocations.

```python
import json

def capture_execution(obj, method_name, args, kwargs):
    # Serialize object state before execution
    pre_exec_state = obj.serialize()

    # Invoke the method
    result = getattr(obj, method_name)(*args, **kwargs)

    # Serialize object state after execution and return value
    post_exec_state = obj.serialize()
    return_value = json.dumps(result) if isinstance(result, dict) else str(result)

    return {
        "object": obj.__class__.__name__,
        "method": method_name,
        "pre_exec_state": pre_exec_state,
        "post_exec_state": post_exec_state,
        "args": args,
        "kwargs": kwargs,
        "return": return_value
    }
```

### Step 3: Serialize Execution Flow
Aggregate captured execution states and interactions into a serializable format (e.g., a list of dictionaries). You can write this data to a file or database.

```python
execution_flow = []
# Example: capturing execution of a single method call
execution_snapshot = capture_execution(agent, "exec", [user_input], {})
execution_flow.append(execution_snapshot)

with open('execution_flow.json', 'w') as f:
    json.dump(execution_flow, f)
```

### Step 4: Replay Functionality
Create functionality to read the serialized execution flow and replay it. This involves deserializing object states and invoking methods according to the captured flow.

```python
def replay_execution_flow(execution_flow):
    for action in execution_flow:
        obj = globals()[action["object"]].deserialize(action["pre_exec_state"])
        getattr(obj, action["method"])(*action["args"], **action["kwargs"])
        print(f"Replayed {action['object']}.{action['method']} with args {action['args']} and kwargs {action['kwargs']}")
```

### Step 5: Modification and Customization
To enable modification of the replay schema, you can provide an interface or utility that allows users to edit the `execution_flow.json` either manually or through a GUI. This might include changing method arguments, reordering actions, or swapping objects.

This example outlines a basic framework and would need to be expanded and adapted to match the specific requirements and complexities of your application, especially for more complex interactions and state management.

```

```swarmauri/experimental/utils/ISerializable.py


# class Serializable:
#     def serialize(self):
#         raise NotImplementedError("Serialization method not implemented")
    
#     @classmethod
#     def deserialize(cls, data):
#         raise NotImplementedError("Deserialization method not implemented")
        
        
# class ToolAgent(Serializable):
#     def serialize(self):
#         # Simplified example, adapt according to actual attributes
#         return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

#     @classmethod
#     def deserialize(cls, data):
#         # This method should instantiate the object based on the serialized state.
#         # Example assumes the presence of model_name in the serialized state.
#         model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
#         return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration

```

```swarmauri/experimental/docs/replay.md

Creating a system that allows for the serialization of object interactions, along with enabling replay and modification of replay schemas in Python, involves several key steps. This process includes capturing the execution state, serializing it, and then providing mechanisms for replay and modification. Here's how you could implement such a system:

### Step 1: Define Serializable Representations
For each class that participates in the interaction, define a method to serialize its state to a dictionary or a similar serializable format. Additionally, include a method to instantiate an object from this serialized state.

```python
class Serializable:
    def serialize(self):
        raise NotImplementedError("Serialization method not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Deserialization method not implemented")
```

Implement these methods in your classes. For example:

```python
class ToolAgent(Serializable):
    def serialize(self):
        # Simplified example, adapt according to actual attributes
        return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

    @classmethod
    def deserialize(cls, data):
        # This method should instantiate the object based on the serialized state.
        # Example assumes the presence of model_name in the serialized state.
        model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
        return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration
```

### Step 2: Capture Executions
Capture executions and interactions by logging or emitting events, including serialized object states and method invocations.

```python
import json

def capture_execution(obj, method_name, args, kwargs):
    # Serialize object state before execution
    pre_exec_state = obj.serialize()

    # Invoke the method
    result = getattr(obj, method_name)(*args, **kwargs)

    # Serialize object state after execution and return value
    post_exec_state = obj.serialize()
    return_value = json.dumps(result) if isinstance(result, dict) else str(result)

    return {
        "object": obj.__class__.__name__,
        "method": method_name,
        "pre_exec_state": pre_exec_state,
        "post_exec_state": post_exec_state,
        "args": args,
        "kwargs": kwargs,
        "return": return_value
    }
```

### Step 3: Serialize Execution Flow
Aggregate captured execution states and interactions into a serializable format (e.g., a list of dictionaries). You can write this data to a file or database.

```python
execution_flow = []
# Example: capturing execution of a single method call
execution_snapshot = capture_execution(agent, "exec", [user_input], {})
execution_flow.append(execution_snapshot)

with open('execution_flow.json', 'w') as f:
    json.dump(execution_flow, f)
```

### Step 4: Replay Functionality
Create functionality to read the serialized execution flow and replay it. This involves deserializing object states and invoking methods according to the captured flow.

```python
def replay_execution_flow(execution_flow):
    for action in execution_flow:
        obj = globals()[action["object"]].deserialize(action["pre_exec_state"])
        getattr(obj, action["method"])(*action["args"], **action["kwargs"])
        print(f"Replayed {action['object']}.{action['method']} with args {action['args']} and kwargs {action['kwargs']}")
```

### Step 5: Modification and Customization
To enable modification of the replay schema, you can provide an interface or utility that allows users to edit the `execution_flow.json` either manually or through a GUI. This might include changing method arguments, reordering actions, or swapping objects.

This example outlines a basic framework and would need to be expanded and adapted to match the specific requirements and complexities of your application, especially for more complex interactions and state management.

---

To capture everything, including object instantiation like `api_key`, `conversation`, `model`, `tools`, and method calls (`exec`) in a fully comprehensive manner, we need to adopt an approach that not only captures method invocations but also objects as they are created and manipulated. This comprehensive capture and replay mechanism would involve the following stages:

### Stage 1: Capture

1. **Object Creation**: Capture the creation of all relevant objects along with their initial states and construction parameters.
2. **Method Calls**: Capture method invocations, including input parameters and return values.
3. **State Changes**: Optionally capture state changes to objects over time.

To implement this, we can use either decorators or a base class pattern that all relevent classes inherit from, which automates capturing information about object creation, method calls, and state.

#### Decorator for Capturing Method Calls and Object Creation

```python
import json
import functools

capture_log = []

def capture(cls):
    class Wrapper:
        def __init__(self, *args, **kwargs):
            capture_log.append({
                "type": "creation",
                "class_name": cls.__name__,
                "init_args": args,
                "init_kwargs": kwargs
            })
            self._instance = cls(*args, **kwargs)
        
        def __getattr__(self, name):
            attr = getattr(self._instance, name)
            if callable(attr):
                @functools.wraps(attr)
                def wrapper(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    capture_log.append({
                        "type": "method_call",
                        "class_name": cls.__name__,
                        "method_name": name,
                        "method_args": args,
                        "method_kwargs": kwargs,
                        "return_value": result
                    })
                    return result
                return wrapper
            return attr
    return Wrapper

def save_capture_log(filepath="execution_log.json"):
    with open(filepath, "w") as f:
        json.dump(capture_log, f, indent=4)
```

#### Applying the Decorator

Apply the `@capture` decorator to classes you want to monitor.

```python
@capture
class ToolAgent:
    # Your implementation
    
@capture
class OpenAIToolModel:
    # Your implementation

@capture
class Toolkit:
    # Your implementation

# Note: You may use different or additional capturing mechanisms for objects that don't fit well with this approach.
```

### Stage 2: Replay

Replaying involves reading the `execution_log.json`, recreating objects according to the log, and then calling the logged methods with their original parameters.

#### Basic Replay Function

```python
def replay_from_log(filepath="execution_log.json"):
    with open(filepath, "r") as f:
        execution_log = json.load(f)

    for action in execution_log:
        if action["type"] == "creation":
            cls = globals()[action["class_name"]]
            obj = cls(*action["init_args"], **action["init_kwargs"])
            # Additional logic to store a reference to this object for future method calls
        elif action["type"] == "method_call":
            # Logic to invoke method on previously created object
```

This solution outlines a mechanism to capture and replay execution flow, focusing on simplicity and adaptability. Depending on your specific requirements (e.g., handling static methods, managing object relationships), you may need to extend or modify this logic. Additionally, consider security implications when dynamically instantiating classes and executing methods, especially with inputs from external sources.

```

```swarmauri/experimental/parsers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/parsers/PDFToTextParser.py

import fitz  # PyMuPDF
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.ConcreteDocument import ConcreteDocument

class PDFtoTextParser(IParser):
    """
    A parser to extract text from PDF files.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses a PDF file and extracts its text content as Document instances.

        Parameters:
        - data (Union[str, Any]): The path to the PDF file.

        Returns:
        - List[IDocument]: A list with a single IDocument instance containing the extracted text.
        """
        # Ensure data is a valid str path to a PDF file
        if not isinstance(data, str):
            raise ValueError("PDFtoTextParser expects a file path in str format.")

        try:
            # Open the PDF file
            doc = fitz.open(data)
            text = ""

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            # Create a document with the extracted text
            document = ConcreteDocument(doc_id=str(hash(data)), content=text, metadata={"source": data})
            return [document]
        
        except Exception as e:
            print(f"An error occurred while parsing the PDF: {e}")
            return []


```

```swarmauri/experimental/vector_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/vector_stores/Word2VecDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/vector_stores/TriplesDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from rdflib import Graph, URIRef, Literal, BNode
from ampligraph.latent_features import ComplEx
from ampligraph.evaluation import train_test_split_no_unseen
from ampligraph.latent_features import EmbeddingModel
from ampligraph.utils import save_model, restore_model

from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.standard.vectorizers.concrete.AmpligraphVectorizer import AmpligraphVectorizer


class TriplesDocumentStore(IDocumentStore, IRetriever):
    def __init__(self, rdf_file_path: str, model_path: Optional[str] = None):
        """
        Initializes the TriplesDocumentStore.
        """
        self.graph = Graph()
        self.rdf_file_path = rdf_file_path
        self.graph.parse(rdf_file_path, format='turtle')
        self.documents = []
        self.vectorizer = AmpligraphVectorizer()
        self.model_path = model_path
        if model_path:
            self.model = restore_model(model_path)
        else:
            self.model = None
        self.metric = CosineDistance()
        self._load_documents()
        if not self.model:
            self._train_model()

    def _train_model(self):
        """
        Trains a model based on triples in the graph.
        """
        # Extract triples for embedding model
        triples = np.array([[str(s), str(p), str(o)] for s, p, o in self.graph])
        # Split data
        train, test = train_test_split_no_unseen(triples, test_size=0.1)
        self.model = ComplEx(batches_count=100, seed=0, epochs=20, k=150, eta=1,
                             optimizer='adam', optimizer_params={'lr': 1e-3},
                             loss='pairwise', regularizer='LP', regularizer_params={'p': 3, 'lambda': 1e-5},
                             verbose=True)
        self.model.fit(train)
        if self.model_path:
            save_model(self.model, self.model_path)

    def _load_documents(self):
        """
        Load documents into the store from the RDF graph.
        """
        for subj, pred, obj in self.graph:
            doc_id = str(hash((subj, pred, obj)))
            content = f"{subj} {pred} {obj}"
            document = Document(content=content, doc_id=doc_id, metadata={})
            self.documents.append(document)

    def add_document(self, document: IDocument) -> None:
        """
        Adds a single RDF triple document.
        """
        subj, pred, obj = document.content.split()  # Splitting content into RDF components
        self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.append(document)
        self._train_model()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Adds multiple RDF triple documents.
        """
        for document in documents:
            subj, pred, obj = document.content.split()  # Assuming each document's content is "subj pred obj"
            self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.extend(documents)
        self._train_model()

    # Implementation for get_document, get_all_documents, delete_document, update_document remains same as before
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve documents similar to the query string.
        """
        if not self.model:
            self._train_model()
        query_vector = self.vectorizer.infer_vector(model=self.model, samples=[query])[0]
        document_vectors = [self.vectorizer.infer_vector(model=self.model, samples=[doc.content])[0] for doc in self.documents]
        similarities = self.metric.distances(SimpleVector(data=query_vector), [SimpleVector(vector) for vector in document_vectors])
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/tracing/RemoteTrace.py

from __future__ import ITraceContext

import requests
import json
import uuid
from datetime import datetime

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.core.tracing.ITraceContext import ITraceContext

# Implementing the RemoteTraceContext class
class RemoteTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str):
        self.trace_id = trace_id
        self.name = name
        self.start_time = datetime.now()
        self.attributes = {}
        self.annotations = {}

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value):
        self.attributes[key] = value
        
    def add_annotation(self, key: str, value):
        self.annotations[key] = value

# Implementing the RemoteAPITracer class
class RemoteAPITracer(ITracer):
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    def start_trace(self, name: str, initial_attributes=None) -> 'RemoteTraceContext':
        trace_id = str(uuid.uuid4())
        context = RemoteTraceContext(trace_id, name)
        if initial_attributes:
            for key, value in initial_attributes.items():
                context.add_attribute(key, value)
        return context

    def end_trace(self, trace_context: 'RemoteTraceContext'):
        trace_context.end_time = datetime.now()
        # Pretending to serialize the context information to JSON
        trace_data = {
            "trace_id": trace_context.get_trace_id(),
            "name": trace_context.name,
            "start_time": str(trace_context.start_time),
            "end_time": str(trace_context.end_time),
            "attributes": trace_context.attributes,
            "annotations": trace_context.annotations
        }
        json_data = json.dumps(trace_data)
        # POST the serialized data to the remote REST API
        response = requests.post(self.api_endpoint, json=json_data)
        if not response.ok:
            raise Exception(f"Failed to send trace data to {self.api_endpoint}. Status code: {response.status_code}")

    def annotate_trace(self, trace_context: 'RemoteTraceContext', key: str, value):
        trace_context.add_annotation(key, value)

```

```swarmauri/experimental/tracing/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/chains/ChainOrderStrategy.py

from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainOrderStrategy(IChainOrderStrategy):
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        """
        Orders the chain steps in reverse order.

        Args:
            steps (List[IChainStep]): The original list of chain steps to be ordered.

        Returns:
            List[IChainStep]: List of chain steps in order.
        """
        # Reverse the list of steps.
        steps = list(steps)
        return steps

```

```swarmauri/experimental/chains/ChainOrderStrategyBase.py

from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainOrderStrategyBase(IChainOrderStrategy):
    """
    A base implementation of the IChainOrderStrategy interface.
    """

    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        """
        Default implementation doesn't reorder steps but must be overridden by specific strategies.
        """
        return steps

```

```swarmauri/experimental/chains/ChainProcessingStrategy.py

from typing import List, Any
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainProcessingStrategy(IChainProcessingStrategy):
    def execute_steps(self, steps: List[IChainStep]) -> Any:
        """
        Executes the given list of ordered chain steps based on the specific strategy 
        and collects their results.

        Args:
            steps (List[IChainStep]): The ordered list of chain steps to be executed.
        
        Returns:
            Any: The result of executing the steps. This could be tailored as per requirement.
        """
        results = []
        for step in steps:
            result = step.method(*step.args, **step.kwargs)
            results.append(result)
        return results

```

```swarmauri/experimental/chains/ChainProcessingStrategyBase.py

from typing import List
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainProcessingStrategyBase(IChainProcessingStrategy):
    """
    A base implementation of the IChainProcessingStrategy interface.
    """
    
    def execute_steps(self, steps: List[IChainStep]):
        """
        Default implementation which should be overridden by specific processing strategies.
        """
        for step in steps:
            print(step)
            step.method(*step.args, **step.kwargs)

```

```swarmauri/experimental/chains/IChainOrderStrategy.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.chains.IChainStep import IChainStep

# Defines how chain steps are ordered
class IChainOrderStrategy(ABC):
    @abstractmethod
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        pass

```

```swarmauri/experimental/chains/IChainProcessingStrategy.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.chains.IChainStep import IChainStep

class IChainProcessingStrategy(ABC):
    """
    Interface for defining the strategy to process the execution of chain steps.
    """
    
    @abstractmethod
    def execute_steps(self, steps: List[IChainStep]):
        """
        Executes the given list of ordered chain steps based on the specific strategy.
        
        Parameters:
            steps (List[IChainStep]): The ordered list of chain steps to be executed.
        """
        pass

```

```swarmauri/experimental/chains/MatrixOrderStrategy.py

from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class MatrixOrderStrategy(IChainOrderStrategy):
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        # Assuming 'steps' are already organized in a matrix-like structure
        ordered_steps = self.arrange_matrix(steps)
        return ordered_steps

    def arrange_matrix(self, steps_matrix):
        # Implement the logic to arrange/order steps based on matrix positions.
        # This is just a placeholder. The actual implementation would depend on the matrix specifications and task dependencies.
        return steps_matrix

```

```swarmauri/experimental/chains/MatrixProcessingStrategy.py

import asyncio
from typing import List, Any
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class MatrixProcessingStrategy(IChainProcessingStrategy):
    async def execute_steps(self, steps: List[IChainStep]) -> Any:
        # Launch tasks asynchronously, maintaining the matrix structure
        results = await self.execute_matrix(steps)
        return results

    async def execute_matrix(self, matrix):
        matrix_results = []

        # Example: Execute tasks row by row, waiting for each row to complete before moving on.
        for row in matrix:
            row_results = await asyncio.gather(*[step.method(*step.args, **step.kwargs) for step in row])
            matrix_results.append(row_results)
            # Optionally, add a call to a row callback here

        # After processing all rows, you may call a final matrix callback
        # This could be a place for final aggregation or analysis of all results
        return matrix_results

```

```swarmauri/experimental/chains/TypeAgnosticCallableChain.py

from typing import Any, Callable, List, Dict, Optional, Tuple, Union

CallableDefinition = Tuple[Callable, List[Any], Dict[str, Any], Union[str, Callable, None]]

class TypeAgnosticCallableChain:
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        self.callables = callables if callables is not None else []

    @staticmethod
    def _ignore_previous(_previous_result, *args, **kwargs):
        return args, kwargs

    @staticmethod
    def _use_first_arg(previous_result, *args, **kwargs):
        return [previous_result] + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_first(previous_result, *args, **kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result) + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_only(previous_result, *_args, **_kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result), {}

    @staticmethod
    def _add_previous_kwargs_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**kwargs, **previous_result}

    @staticmethod
    def _add_previous_kwargs_no_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**previous_result, **kwargs}

    @staticmethod
    def _use_all_args_all_kwargs_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {}
        combined_kwargs.update(kwargs)
        return combined_args, combined_kwargs

    @staticmethod
    def _use_all_args_all_kwargs_no_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = kwargs if isinstance(kwargs, dict) else {}
        combined_kwargs = {**combined_kwargs, **(previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {})}
        return combined_args, combined_kwargs

    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: Dict[str, Any] = None, input_handler: Union[str, Callable, None] = None) -> None:
        if isinstance(input_handler, str):
            # Map the string to the corresponding static method
            input_handler_method = getattr(self, f"_{input_handler}", None)
            if input_handler_method is None:
                raise ValueError(f"Unknown input handler name: {input_handler}")
            input_handler = input_handler_method
        elif input_handler is None:
            input_handler = self._ignore_previous
        self.callables.append((func, args or [], kwargs or {}, input_handler))

    def __call__(self, *initial_args, **initial_kwargs) -> Any:
        result = None
        for func, args, kwargs, input_handler in self.callables:
            if isinstance(input_handler, str):
                # Map the string to the corresponding static method
                input_handler_method = getattr(self, f"_{input_handler}", None)
                if input_handler_method is None:
                    raise ValueError(f"Unknown input handler name: {input_handler}")
                input_handler = input_handler_method
            elif input_handler is None:
                input_handler = self._ignore_previous
                
            args, kwargs = input_handler(result, *args, **kwargs) if result is not None else (args, kwargs)
            result = func(*args, **kwargs)
        return result

    def __or__(self, other: "TypeAgnosticCallableChain") -> "TypeAgnosticCallableChain":
        if not isinstance(other, TypeAgnosticCallableChain):
            raise TypeError("Operand must be an instance of TypeAgnosticCallableChain")
        
        new_chain = TypeAgnosticCallableChain(self.callables + other.callables)
        return new_chain

```

```swarmauri/experimental/chains/__init__.py

#

```

```swarmauri/experimental/vectorizers/DGLVectorizer.py

import dgl
import torch
import torch.nn.functional as F
import numpy as np
from dgl.nn import GraphConv
from typing import List, Union, Any
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class DGLGraphConv(torch.nn.Module):
    def __init__(self, in_feats, out_feats, activation=F.relu):
        super(DGLGraphConv, self).__init__()
        self.conv1 = GraphConv(in_feats, 128)
        self.conv2 = GraphConv(128, out_feats)
        self.activation = activation

    def forward(self, g, inputs):
        # Apply graph convolution and activation.
        h = self.conv1(g, inputs)
        h = self.activation(h)
        h = self.conv2(g, h)
        return h

class DGLVectorizer(IVectorize):
    def __init__(self, in_feats, out_feats, model=None):
        self.in_feats = in_feats
        self.out_feats = out_feats
        self.model = model or DGLGraphConv(in_feats, out_feats)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def fit(self, graphs, features, epochs=10, learning_rate=0.01):
        self.model.to(self.device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            for g, feat in zip(graphs, features):
                g = g.to(self.device)
                feat = feat.to(self.device)
                outputs = self.model(g, feat)
                loss = F.mse_loss(outputs, feat)  # Example loss; adjust as needed
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            print(f'Epoch {epoch + 1}, Loss: {loss.item()}')
    
    def infer_vector(self, graph, features):
        graph = graph.to(self.device)
        features = features.to(self.device)
        with torch.no_grad():
            embeddings = self.model(graph, features)
        return SimpleVector(embeddings.cpu().numpy())

```

```swarmauri/experimental/vectorizers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/document_stores/TriplesDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from rdflib import Graph, URIRef, Literal, BNode
from ampligraph.latent_features import ComplEx
from ampligraph.evaluation import train_test_split_no_unseen
from ampligraph.latent_features import EmbeddingModel
from ampligraph.utils import save_model, restore_model

from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.standard.vectorizers.concrete.AmpligraphVectorizer import AmpligraphVectorizer


class TriplesDocumentStore(IDocumentStore, IRetriever):
    def __init__(self, rdf_file_path: str, model_path: Optional[str] = None):
        """
        Initializes the TriplesDocumentStore.
        """
        self.graph = Graph()
        self.rdf_file_path = rdf_file_path
        self.graph.parse(rdf_file_path, format='turtle')
        self.documents = []
        self.vectorizer = AmpligraphVectorizer()
        self.model_path = model_path
        if model_path:
            self.model = restore_model(model_path)
        else:
            self.model = None
        self.metric = CosineDistance()
        self._load_documents()
        if not self.model:
            self._train_model()

    def _train_model(self):
        """
        Trains a model based on triples in the graph.
        """
        # Extract triples for embedding model
        triples = np.array([[str(s), str(p), str(o)] for s, p, o in self.graph])
        # Split data
        train, test = train_test_split_no_unseen(triples, test_size=0.1)
        self.model = ComplEx(batches_count=100, seed=0, epochs=20, k=150, eta=1,
                             optimizer='adam', optimizer_params={'lr': 1e-3},
                             loss='pairwise', regularizer='LP', regularizer_params={'p': 3, 'lambda': 1e-5},
                             verbose=True)
        self.model.fit(train)
        if self.model_path:
            save_model(self.model, self.model_path)

    def _load_documents(self):
        """
        Load documents into the store from the RDF graph.
        """
        for subj, pred, obj in self.graph:
            doc_id = str(hash((subj, pred, obj)))
            content = f"{subj} {pred} {obj}"
            document = Document(content=content, doc_id=doc_id, metadata={})
            self.documents.append(document)

    def add_document(self, document: IDocument) -> None:
        """
        Adds a single RDF triple document.
        """
        subj, pred, obj = document.content.split()  # Splitting content into RDF components
        self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.append(document)
        self._train_model()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Adds multiple RDF triple documents.
        """
        for document in documents:
            subj, pred, obj = document.content.split()  # Assuming each document's content is "subj pred obj"
            self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.extend(documents)
        self._train_model()

    # Implementation for get_document, get_all_documents, delete_document, update_document remains same as before
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve documents similar to the query string.
        """
        if not self.model:
            self._train_model()
        query_vector = self.vectorizer.infer_vector(model=self.model, samples=[query])[0]
        document_vectors = [self.vectorizer.infer_vector(model=self.model, samples=[doc.content])[0] for doc in self.documents]
        similarities = self.metric.distances(SimpleVector(data=query_vector), [SimpleVector(vector) for vector in document_vectors])
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/document_stores/Word2VecDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/document_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/distances/CanberraDistance.py

import numpy as np
from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class CanberraDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Canberra distance metric.
    This class now processes IVector instances instead of raw lists.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Canberra distance between two IVector instances.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Canberra distance between the vectors.
        """
        # Extract data from IVector
        data_a = np.array(vector_a.data)
        data_b = np.array(vector_b.data)

        # Checking dimensions match
        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Computing Canberra distance
        distance = np.sum(np.abs(data_a - data_b) / (np.abs(data_a) + np.abs(data_b)))
        # Handling the case where both vectors have a zero value for the same dimension
        distance = np.nan_to_num(distance)
        return distance
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute similarity using the Canberra distance. Since this distance metric isn't
        directly interpretable as a similarity, a transformation is applied to map the distance
        to a similarity score.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        # One way to derive a similarity from distance is through inversion or transformation.
        # Here we use an exponential decay based on the computed distance. This is a placeholder
        # that assumes closer vectors (smaller distance) are more similar.
        distance = self.distance(vector_a, vector_b)

        # Transform the distance into a similarity score
        similarity = np.exp(-distance)

        return similarity
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/ChebyshevDistance.py

from typing import List
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity

class ChebyshevDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Chebyshev distance metric.
    Chebyshev distance is the maximum absolute distance between two vectors' elements.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Chebyshev distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Chebyshev distance between vector_a and vector_b.
        """
        max_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            max_distance = max(max_distance, abs(a - b))
        return max_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity between two vectors based on the Chebyshev distance.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: The similarity score between the two vectors.
        """

        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/HaversineDistance.py

from typing import List
from math import radians, cos, sin, sqrt, atan2
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class HaversineDistance(IDistanceSimilarity):
    """
    Concrete implementation of IDistanceSimiliarity interface using the Haversine formula.
    
    Haversine formula determines the great-circle distance between two points on a sphere given their 
    longitudes and latitudes. This implementation is particularly useful for geo-spatial data.
    """ 

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Haversine distance between two geo-spatial points.

        Args:
            vector_a (IVector): The first point in the format [latitude, longitude].
            vector_b (IVector): The second point in the same format [latitude, longitude].

        Returns:
            float: The Haversine distance between vector_a and vector_b in kilometers.
        """
        # Earth radius in kilometers
        R = 6371.0

        lat1, lon1 = map(radians, vector_a.data)
        lat2, lon2 = map(radians, vector_b.data)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")

```

```swarmauri/experimental/distances/ManhattanDistance.py

from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class ManhattanDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Manhattan distance.
    
    The Manhattan distance between two points is the sum of the absolute differences of their Cartesian coordinates.
    This is also known as L1 distance.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Manhattan distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The Manhattan distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")
        
        return sum(abs(a - b) for a, b in zip(vector_a.data, vector_b.data))

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        The similarity based on Manhattan distance can be inversely related to the distance for some applications,
        but this method intentionally returns NotImplementedError to signal that Manhattan distance is typically
        not directly converted to similarity in the conventional sense used in this context.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            NotImplementedError: This is intended as this distance metric doesn't directly offer a similarity measure.
        """
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity measure.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity measure.")

```

```swarmauri/experimental/distances/MinkowskiDistance.py

from typing import List
from scipy.spatial.distance import minkowski
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class MinkowskiDistance(IDistanceSimilarity):
    """
    Implementation of the IDistanceSimiliarity interface using the Minkowski distance metric.
    Minkowski distance is a generalized metric form that includes Euclidean distance,
    Manhattan distance, and others depending on the order (p) parameter.

    The class provides methods to compute the Minkowski distance between two vectors.
    """

    def __init__(self, p: int = 2):
        """
        Initializes the MinkowskiDistance calculator with the specified order.

        Parameters:
        - p (int): The order of the Minkowski distance. p=2 corresponds to the Euclidean distance,
                   while p=1 corresponds to the Manhattan distance. Default is 2.
        """
        self.p = p

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Minkowski distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Minkowski distance between vector_a and vector_b.
        """
        # Check if both vectors have the same dimensionality
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")

        # Extract data from IVector instances
        data_a = vector_a.data
        data_b = vector_b.data

        # Calculate and return the Minkowski distance
        return minkowski(data_a, data_b, p=self.p)

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors based on the Minkowski distance.
        The similarity is inversely related to the distance.

        Args:
            vector_a (IVector): The first vector to compare for similarity.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)  # An example similarity score
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/ScannVectorStore.py

import numpy as np
import scann
from typing import List, Dict, Union

from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vector_stores.ISimiliarityQuery import ISimilarityQuery
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector


class ScannVectorStore(IVectorStore, ISimilarityQuery):
    """
    A vector store that utilizes ScaNN (Scalable Nearest Neighbors) for efficient similarity searches.
    """

    def __init__(self, dimension: int, num_leaves: int = 100, num_leaves_to_search: int = 10, reordering_num_neighbors: int = 100):
        """
        Initialize the ScaNN vector store with given parameters.

        Parameters:
        - dimension (int): The dimensionality of the vectors being stored.
        - num_leaves (int): The number of leaves for the ScaNN partitioning tree.
        - num_leaves_to_search (int): The number of leaves to search for query time. Must be <= num_leaves.
        - reordering_num_neighbors (int): The number of neighbors to re-rank based on the exact distance after searching leaves.
        """
        self.dimension = dimension
        self.num_leaves = num_leaves
        self.num_leaves_to_search = num_leaves_to_search
        self.reordering_num_neighbors = reordering_num_neighbors

        self.searcher = None  # Placeholder for the ScaNN searcher initialized during building
        self.dataset_vectors = []
        self.id_to_metadata = {}

    def _build_scann_searcher(self):
        """Build the ScaNN searcher based on current dataset vectors."""
        self.searcher = scann.ScannBuilder(np.array(self.dataset_vectors, dtype=np.float32), num_neighbors=self.reordering_num_neighbors, distance_measure="dot_product").tree(
            num_leaves=self.num_leaves, num_leaves_to_search=self.num_leaves_to_search, training_sample_size=25000
        ).score_ah(
            dimensions_per_block=2
        ).reorder(self.reordering_num_neighbors).build()

    def add_vector(self, vector_id: str, vector: Union[np.ndarray, List[float]], metadata: Dict = None) -> None:
        """
        Adds a vector along with its identifier and optional metadata to the store.

        Args:
            vector_id (str): Unique identifier for the vector.
            vector (Union[np.ndarray, List[float]]): The high-dimensional vector to be stored.
            metadata (Dict, optional): Optional metadata related to the vector.
        """
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector, dtype=np.float32)
        
        if self.searcher is None:
            self.dataset_vectors.append(vector)
        else:
            raise Exception("Cannot add vectors after building the index. Rebuild the index to include new vectors.")

        if metadata is None:
            metadata = {}
        self.id_to_metadata[vector_id] = metadata

    def build_index(self):
        """Builds or rebuilds the ScaNN searcher to reflect the current dataset vectors."""
        self._build_scann_searcher()

    def get_vector(self, vector_id: str) -> Union[IVector, None]:
        """
        Retrieve a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector.

        Returns:
            Union[IVector, None]: The vector associated with the given id, or None if not found.
        """
        if vector_id in self.id_to_metadata:
            metadata = self.id_to_metadata[vector_id]
            return SimpleVector(data=metadata.get('vector'), metadata=metadata)
        return None

    def delete_vector(self, vector_id: str) -> None:
        """
        Deletes a vector from the ScannVectorStore and marks the index for rebuilding.
        Note: For simplicity, this function assumes vectors are uniquely identifiable by their metadata.

        Args:
            vector_id (str): The unique identifier for the vector to be deleted.
        """
        if vector_id in self.id_to_metadata:
            # Identify index of the vector to be deleted
            vector = self.id_to_metadata[vector_id]['vector']
            index = self.dataset_vectors.index(vector)

            # Remove vector and its metadata
            del self.dataset_vectors[index]
            del self.id_to_metadata[vector_id]

            # Since vector order is important for matching ids, rebuild the searcher to reflect deletion
            self.searcher = None
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")

    def update_vector(self, vector_id: str, new_vector: Union[np.ndarray, List[float]], new_metadata: Dict = None) -> None:
        """
        Updates an existing vector in the ScannVectorStore and marks the index for rebuilding.

        Args:
            vector_id (str): The unique identifier for the vector to be updated.
            new_vector (Union[np.ndarray, List[float]]): The updated vector.
            new_metadata (Dict, optional): Optional updated metadata for the vector.
        """
        # Ensure new_vector is numpy array for consistency
        if not isinstance(new_vector, np.ndarray):
            new_vector = np.array(new_vector, dtype=np.float32)

        if vector_id in self.id_to_metadata:
            # Update operation follows delete then add strategy because vector order matters in ScaNN
            self.delete_vector(vector_id)
            self.add_vector(vector_id, new_vector, new_metadata)
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")



    def search_by_similarity_threshold(self, query_vector: Union[np.ndarray, List[float]], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (Union[np.ndarray, List[float]]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within. Not used in this implementation.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector, dtype=np.float32)
        
        if self.searcher is None:
            self._build_scann_searcher()
        
        _, indices = self.searcher.search(query_vector, final_num_neighbors=self.reordering_num_neighbors)
        results = [{"id": str(idx), "metadata": self.id_to_metadata.get(str(idx), {})} for idx in indices if idx < similarity_threshold]
        return results

```

```swarmauri/experimental/distances/SorensenDiceDistance.py

import numpy as np
from typing import List
from collections import Counter

from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SorensenDiceDistance(IDistanceSimilarity):
    """
    Implementing a concrete Vector Store class for calculating Sörensen-Dice Index Distance.
    The Sörensen-Dice Index, or Dice's coefficient, is a measure of the similarity between two sets.
    """

    def distance(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Compute the Sörensen-Dice distance between two vectors.
        
        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.
        
        Returns:
            float: The computed Sörensen-Dice distance between vector_a and vector_b.
        """
        # Convert vectors to binary sets
        set_a = set([i for i, val in enumerate(vector_a) if val])
        set_b = set([i for i, val in enumerate(vector_b) if val])
        
        # Calculate the intersection size
        intersection_size = len(set_a.intersection(set_b))
        
        # Sorensen-Dice Index calculation
        try:
            sorensen_dice_index = (2 * intersection_size) / (len(set_a) + len(set_b))
        except ZeroDivisionError:
            sorensen_dice_index = 0.0
        
        # Distance is inverse of similarity for Sörensen-Dice
        distance = 1 - sorensen_dice_index
        
        return distance
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarity(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")

```

```swarmauri/experimental/distances/SquaredEuclideanDistance.py

from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SquaredEuclideanDistance(IDistanceSimilarity):
    """
    A concrete class for computing the squared Euclidean distance between two vectors.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the squared Euclidean distance between vectors `vector_a` and `vector_b`.

        Parameters:
        - vector_a (IVector): The first vector in the comparison.
        - vector_b (IVector): The second vector in the comparison.

        Returns:
        - float: The computed squared Euclidean distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must be of the same dimensionality.")

        squared_distance = sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data))
        return squared_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Squared Euclidean distance is not used for calculating similarity.
        
        Parameters:
        - vector_a (IVector): The first vector.
        - vector_b (IVector): The second vector.

        Raises:
        - NotImplementedError: Indicates that similarity calculation is not implemented.
        """
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")
        
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")

```

```swarmauri/experimental/distances/SSASimilarity.py

from typing import Set, List, Dict
from ....core.vector_stores.ISimilarity import ISimilarity
from ....core.vectors.IVector import IVector


class SSASimilarity(ISimilarity):
    """
    Implements the State Similarity in Arity (SSA) similarity measure to
    compare states (sets of variables) for their similarity.
    """

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Calculate the SSA similarity between two documents by comparing their metadata,
        assumed to represent states as sets of variables.

        Args:
        - vector_a (IDocument): The first document.
        - vector_b (IDocument): The second document to compare with the first document.

        Returns:
        - float: The SSA similarity measure between vector_a and vector_b, ranging from 0 to 1
                 where 0 represents no similarity and 1 represents identical states.
        """
        state_a = set(vector_a.metadata.keys())
        state_b = set(vector_b.metadata.keys())

        return self.calculate_ssa(state_a, state_b)

    @staticmethod
    def calculate_ssa(state_a: Set[str], state_b: Set[str]) -> float:
        """
        Calculate the State Similarity in Arity (SSA) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.

        Returns:6
        - float: The SSA similarity measure, ranging from 0 (no similarity) to 1 (identical states).
        """
        # Calculate the intersection (shared variables) between the two states
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the union (total unique variables) of the two states
        total_variables = state_a.union(state_b)
        
        # Calculate the SSA measure as the ratio of shared to total variables
        ssa = len(shared_variables) / len(total_variables) if total_variables else 1
        
        return ssa

```

```swarmauri/experimental/distances/SSIVSimilarity.py

from typing import List, Dict, Set
from ....core.vector_stores.ISimilarity import ISimilarity

class SSIVSimilarity(ISimilarity):
    """
    Concrete class that implements ISimilarity interface using
    State Similarity of Important Variables (SSIV) as the similarity measure.
    """

    def similarity(self, state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the SSIV between two states represented by sets of variables.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        """
        return self.calculate_ssiv(state_a, state_b, importance_a, importance_b)

    @staticmethod
    def calculate_ssiv(state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the State Similarity of Important Variables (SSIV) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        
        Note: It is assumed that the importance weights are non-negative.
        """
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the summed importance of shared variables
        shared_importance_sum = sum(importance_a[var] for var in shared_variables) + sum(importance_b[var] for var in shared_variables)
        
        # Calculate the total importance of all variables in both states
        total_importance_sum = sum(importance_a.values()) + sum(importance_b.values())
        
        # Calculate and return the SSIV
        ssiv = (2 * shared_importance_sum) / total_importance_sum if total_importance_sum != 0 else 0
        return ssiv


```

```swarmauri/experimental/distances/__init__.py

# -*- coding: utf-8 -*-



```