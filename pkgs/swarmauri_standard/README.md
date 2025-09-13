<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri-standard/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-standard" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_standard/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_standard.svg"/></a>
    <a href="https://pypi.org/project/swarmauri-standard/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-standard" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-standard/">
        <img src="https://img.shields.io/pypi/l/swarmauri-standard" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri-standard/">
        <img src="https://img.shields.io/pypi/v/swarmauri-standard?label=swarmauri-standard&color=green" alt="PyPI - swarmauri-standard"/></a>


</p>

---

# Swarmauri Standard

The Swarmauri SDK offers a comprehensive suite of tools designed for building distributed, extensible systems using the Swarmauri framework. 


## Standard

- **Concrete Classes**: Ready-to-use, pre-implemented classes that fulfill standard system needs while adhering to Swarmauri principles. **These classes are the first in line for ongoing support and maintenance, ensuring they remain stable, performant, and up to date with future SDK developments.**



## AI Kit

The AI Kit provides a collection of tools and components for building intelligent systems with the Swarmauri SDK. Below is an overview of the directories and their contents:

### Agents
- [QAAgent.py](swarmauri_standard/agents/QAAgent.py): Implements a question-answering agent.
- [RagAgent.py](swarmauri_standard/agents/RagAgent.py): Implements a retrieval-augmented generation agent.
- [SimpleConversationAgent.py](swarmauri_standard/agents/SimpleConversationAgent.py): Implements a basic conversational agent.
- [ToolAgent.py](swarmauri_standard/agents/ToolAgent.py): Implements an agent that uses various tools.

### Chains
- [CallableChain.py](swarmauri_standard/chains/CallableChain.py): Defines a chain of callable steps.
- [ChainStep.py](swarmauri_standard/chains/ChainStep.py): Represents a single step in a chain.
- [ContextChain.py](swarmauri_standard/chains/ContextChain.py): Manages context within a chain.
- [PromptContextChain.py](swarmauri_standard/chains/PromptContextChain.py): Handles prompt-based context in a chain.

### Chunkers
- [DelimiterBasedChunker.py](swarmauri_standard/chunkers/DelimiterBasedChunker.py): Splits text based on delimiters.
- [FixedLengthChunker.py](swarmauri_standard/chunkers/FixedLengthChunker.py): Splits text into fixed-length chunks.
- [MdSnippetChunker.py](swarmauri_standard/chunkers/MdSnippetChunker.py): Splits markdown text into snippets.
- [SentenceChunker.py](swarmauri_standard/chunkers/SentenceChunker.py): Splits text into sentences.
- [SlidingWindowChunker.py](swarmauri_standard/chunkers/SlidingWindowChunker.py): Splits text using a sliding window approach.

### Control Panels
- [ControlPanel.py](swarmauri_standard/control_panels/ControlPanel.py): Manages control panel operations.

### Conversations
- [Conversation.py](swarmauri_standard/conversations/Conversation.py): Manages conversation state and flow.
- [MaxSizeConversation.py](swarmauri_standard/conversations/MaxSizeConversation.py): Implements a conversation with a maximum size limit.
- [MaxSystemContextConversation.py](swarmauri_standard/conversations/MaxSystemContextConversation.py): Manages conversation with system context constraints.
- [SessionCacheConversation.py](swarmauri_standard/conversations/SessionCacheConversation.py): Implements a session-cached conversation.

### Data Connectors
- [GoogleDriveDataConnector.py](swarmauri_standard/dataconnectors/GoogleDriveDataConnector.py): Connects to Google Drive for data access.

### Decorators
- [deprecate.py](swarmauri_standard/decorators/deprecate.py): Marks functions as deprecated.
- [maybe_async.py](swarmauri_standard/decorators/maybe_async.py): Allows functions to be optionally asynchronous.
- [retry_on_status_codes.py](swarmauri_standard/decorators/retry_on_status_codes.py): Retries functions based on status codes.
- [tool_decorator.py](swarmauri_standard/decorators/tool_decorator.py): Decorates tool functions.

### Distances
- [CanberraDistance.py](swarmauri_standard/distances/CanberraDistance.py): Calculates Canberra distance.
- [ChebyshevDistance.py](swarmauri_standard/distances/ChebyshevDistance.py): Calculates Chebyshev distance.
- [ChiSquaredDistance.py](swarmauri_standard/distances/ChiSquaredDistance.py): Calculates Chi-squared distance.
- [CosineDistance.py](swarmauri_standard/distances/CosineDistance.py): Calculates Cosine distance.
- [EuclideanDistance.py](swarmauri_standard/distances/EuclideanDistance.py): Calculates Euclidean distance.
- [HaversineDistance.py](swarmauri_standard/distances/HaversineDistance.py): Calculates Haversine distance.
- [JaccardIndexDistance.py](swarmauri_standard/distances/JaccardIndexDistance.py): Calculates Jaccard index distance.
- [LevenshteinDistance.py](swarmauri_standard/distances/LevenshteinDistance.py): Calculates Levenshtein distance.
- [ManhattanDistance.py](swarmauri_standard/distances/ManhattanDistance.py): Calculates Manhattan distance.
- [SorensenDiceDistance.py](swarmauri_standard/distances/SorensenDiceDistance.py): Calculates Sørensen-Dice distance.
- [SquaredEuclideanDistance.py](swarmauri_standard/distances/SquaredEuclideanDistance.py): Calculates squared Euclidean distance.

### Documents
- [Document.py](swarmauri_standard/documents/Document.py): Manages document data and operations.

### Embeddings
- [CohereEmbedding.py](swarmauri_standard/embeddings/CohereEmbedding.py): Generates embeddings using Cohere.
- [GeminiEmbedding.py](swarmauri_standard/embeddings/GeminiEmbedding.py): Generates embeddings using Gemini.
- [MistralEmbedding.py](swarmauri_standard/embeddings/MistralEmbedding.py): Generates embeddings using Mistral.
- [OpenAIEmbedding.py](swarmauri_standard/embeddings/OpenAIEmbedding.py): Generates embeddings using OpenAI.
- [TfidfEmbedding.py](swarmauri_standard/embeddings/TfidfEmbedding.py): Generates TF-IDF embeddings.
- [VoyageEmbedding.py](swarmauri_standard/embeddings/VoyageEmbedding.py): Generates embeddings using Voyage.

### Exceptions
- [IndexErrorWithContext.py](swarmauri_standard/exceptions/IndexErrorWithContext.py): Custom index error with context.

### Factories
- [AgentFactory.py](swarmauri_standard/factories/AgentFactory.py): Creates
agents using predefined configurations.

### Image Generators
- [BlackForestImgGenModel.py](swarmauri_standard/image_gens/BlackForestImgGenModel.py): Generates images using the Black Forest model.
- [DeepInfraImgGenModel.py](swarmauri_standard/image_gens/DeepInfraImgGenModel.py): Generates images using the Deep Infra model.
- [FalAIImgGenModel.py](swarmauri_standard/image_gens/FalAIImgGenModel.py): Generates images using the Fal AI model.
- [HyperbolicImgGenModel.py](swarmauri_standard/image_gens/HyperbolicImgGenModel.py): Generates images using the Hyperbolic model.
- [OpenAIImgGenModel.py](swarmauri_standard/image_gens/OpenAIImgGenModel.py): Generates images using the OpenAI model.

### LLMs
- [AI21StudioModel.py](swarmauri_standard/llms/AI21StudioModel.py): Implements the AI21 Studio model.
- [AnthropicModel.py](swarmauri_standard/llms/AnthropicModel.py): Implements the Anthropic model.
- [AnthropicToolModel.py](swarmauri_standard/llms/AnthropicToolModel.py): Implements the Anthropic tool model.
- [CohereModel.py](swarmauri_standard/llms/CohereModel.py): Implements the Cohere model.
- [CohereToolModel.py](swarmauri_standard/llms/CohereToolModel.py): Implements the Cohere tool model.
- [DeepInfraModel.py](swarmauri_standard/llms/DeepInfraModel.py): Implements the Deep Infra model.
- [DeepSeekModel.py](swarmauri_standard/llms/DeepSeekModel.py): Implements the Deep Seek model.
- [FalAIVisionModel.py](swarmauri_standard/llms/FalAIVisionModel.py): Implements the Fal AI Vision model.
- [GeminiProModel.py](swarmauri_standard/llms/GeminiProModel.py): Implements the Gemini Pro model.
- [GeminiToolModel.py](swarmauri_standard/llms/GeminiToolModel.py): Implements the Gemini tool model.
- [GroqAIAudio.py](swarmauri_standard/llms/GroqAIAudio.py): Implements the Groq AI audio model.
- [GroqModel.py](swarmauri_standard/llms/GroqModel.py): Implements the Groq model.
- [GroqToolModel.py](swarmauri_standard/llms/GroqToolModel.py): Implements the Groq tool model.
- [GroqVisionModel.py](swarmauri_standard/llms/GroqVisionModel.py): Implements the Groq vision model.
- [HyperbolicAudioTTS.py](swarmauri_standard/llms/HyperbolicAudioTTS.py): Implements the Hyperbolic audio TTS model.
- [HyperbolicModel.py](swarmauri_standard/llms/HyperbolicModel.py): Implements the Hyperbolic model.
- [HyperbolicVisionModel.py](swarmauri_standard/llms/HyperbolicVisionModel.py): Implements the Hyperbolic vision model.
- [LlamaCppModel.py](swarmauri_standard/llms/LlamaCppModel.py): Implements the Llama Cpp model.
- [MistralModel.py](swarmauri_standard/llms/MistralModel.py): Implements the Mistral model.
- [MistralToolModel.py](swarmauri_standard/llms/MistralToolModel.py): Implements the Mistral tool model.
- [OpenAIAudio.py](swarmauri_standard/llms/OpenAIAudio.py): Implements the OpenAI audio model.
- [OpenAIAudioTTS.py](swarmauri_standard/llms/OpenAIAudioTTS.py): Implements the OpenAI audio TTS model.
- [OpenAIModel.py](swarmauri_standard/llms/OpenAIModel.py): Implements the OpenAI model.
- [OpenAIReasonModel.py](swarmauri_standard/llms/OpenAIReasonModel.py): Implements the OpenAI reason model.
- [OpenAIToolModel.py](swarmauri_standard/llms/OpenAIToolModel.py): Implements the OpenAI tool model.
- [PerplexityModel.py](swarmauri_standard/llms/PerplexityModel.py): Implements the Perplexity model.
- [PlayHTModel.py](swarmauri_standard/llms/PlayHTModel.py): Implements the PlayHT model.
- [WhisperLargeModel.py](swarmauri_standard/llms/WhisperLargeModel.py): Implements the Whisper Large model.

### Measurements
- [CompletenessMeasurement.py](swarmauri_standard/measurements/CompletenessMeasurement.py): Measures the completeness of data.
- [DistinctivenessMeasurement.py](swarmauri_standard/measurements/DistinctivenessMeasurement.py): Measures the distinctiveness of data.
- [FirstImpressionMeasurement.py](swarmauri_standard/measurements/FirstImpressionMeasurement.py): Measures the first impression of data.
- [MeanMeasurement.py](swarmauri_standard/measurements/MeanMeasurement.py): Measures the mean of data.
- [MiscMeasurement.py](swarmauri_standard/measurements/MiscMeasurement.py): Miscellaneous measurements.
- [MissingnessMeasurement.py](swarmauri_standard/measurements/MissingnessMeasurement.py): Measures the missingness of data.
- [PatternMatchingMeasurement.py](swarmauri_standard/measurements/PatternMatchingMeasurement.py): Measures pattern matching in data.
- [RatioOfSumsMeasurement.py](swarmauri_standard/measurements/RatioOfSumsMeasurement.py): Measures the ratio of sums in data.
- [StaticMeasurement.py](swarmauri_standard/measurements/StaticMeasurement.py): Static measurements.
- [UniquenessMeasurement.py](swarmauri_standard/measurements/UniquenessMeasurement.py): Measures the uniqueness of data.
- [ZeroMeasurement.py](swarmauri_standard/measurements/ZeroMeasurement.py): Measures zero values in data.

### Messages
- [AgentMessage.py](swarmauri_standard/messages/AgentMessage.py): Defines messages sent by agents.
- [FunctionMessage.py](swarmauri_standard/messages/FunctionMessage.py): Defines messages for functions.
- [HumanMessage.py](swarmauri_standard/messages/HumanMessage.py): Defines messages sent by humans.
- [SystemMessage.py](swarmauri_standard/messages/SystemMessage.py): Defines system messages.

### Parsers
- [CSVParser.py](swarmauri_standard/parsers/CSVParser.py): Parses CSV files.
- [HTMLTagStripParser.py](swarmauri_standard/parsers/HTMLTagStripParser.py): Strips HTML tags from text.
- [Md2HtmlParser.py](swarmauri_standard/parsers/Md2HtmlParser.py): Converts markdown to HTML.
- [OpenAPISpecParser.py](swarmauri_standard/parsers/OpenAPISpecParser.py): Parses OpenAPI specifications.
- [PhoneNumberExtractorParser.py](swarmauri_standard/parsers/PhoneNumberExtractorParser.py): Extracts phone numbers from text.
- [PythonParser.py](swarmauri_standard/parsers/PythonParser.py): Parses Python code.
- [RegExParser.py](swarmauri_standard/parsers/RegExParser.py): Parses text using regular expressions.
- [URLExtractorParser.py](swarmauri_standard/parsers/URLExtractorParser.py): Extracts URLs from text.
- [XMLParser.py](swarmauri_standard/parsers/XMLParser.py): Parses XML files.

### Pipelines
- [Pipeline.py](swarmauri_standard/pipelines/Pipeline.py): Defines data processing pipelines.

### Prompts
- [PromptGenerator.py](swarmauri_standard/prompts/PromptGenerator.py): Generates prompts.
- [PromptMatrix.py](swarmauri_standard/prompts/PromptMatrix.py): Defines a matrix of prompts.
- [Prompt.py](swarmauri_standard/prompts/Prompt.py): Defines a single prompt.

### Prompt Templates
- [PromptTemplate.py](swarmauri_standard/prompt_templates/PromptTemplate.py): Defines templates for generating prompts.

### Schema Converters
- [AnthropicSchemaConverter.py](swarmauri_standard/schema_converters/AnthropicSchemaConverter.py): Converts schemas for Anthropic models.
- [CohereSchemaConverter.py](swarmauri_standard/schema_converters/CohereSchemaConverter.py): Converts schemas for Cohere models.
- [GeminiSchemaConverter.py](swarmauri_standard/schema_converters/GeminiSchemaConverter.py): Converts schemas for Gemini models.
- [GroqSchemaConverter.py](swarmauri_standard/schema_converters/GroqSchemaConverter.py): Converts schemas for Groq models.
- [MistralSchemaConverter.py](swarmauri_standard/schema_converters/MistralSchemaConverter.py): Converts schemas for Mistral models.
- [OpenAISchemaConverter.py](swarmauri_standard/schema_converters/OpenAISchemaConverter.py): Converts schemas for OpenAI models.
- [ShuttleAISchemaConverter.py](swarmauri_standard/schema_converters/ShuttleAISchemaConverter.py): Converts schemas for Shuttle AI models.

### Service Registries
- [ServiceRegistry.py](swarmauri_standard/service_registries/ServiceRegistry.py): Manages service registrations.

### State
- [DictState.py](swarmauri_standard/state/DictState.py): Manages state using dictionaries.

### STT (Speech-to-Text)
- [GroqSTT.py](swarmauri_standard/stt/GroqSTT.py): Implements speech-to-text using Groq.
- [OpenaiSTT.py](swarmauri_standard/stt/OpenaiSTT.py): Implements speech-to-text using OpenAI.
- [WhisperLargeSTT.py](swarmauri_standard/stt/WhisperLargeSTT.py): Implements speech-to-text using Whisper Large.

### Swarms
- [Swarm.py](swarmauri_standard/swarms/Swarm.py): Manages swarm operations.

### Task Management Strategies
- [RoundRobinStrategy.py](swarmauri_standard/task_mgmt_strategies/RoundRobinStrategy.py): Implements a round-robin task management strategy.

### Toolkits
- [AccessibilityToolkit.py](swarmauri_standard/toolkits/AccessibilityToolkit.py): Provides tools for accessibility.
- [Toolkit.py](swarmauri_standard/toolkits/Toolkit.py): Defines a general toolkit.

### Tool LLMs
- [AnthropicToolModel.py](swarmauri_standard/tool_llms/AnthropicToolModel.py): Implements the Anthropic tool model.
- [CohereToolModel.py](swarmauri_standard/tool_llms/CohereToolModel.py): Implements the Cohere tool model.
- [GeminiToolModel.py](swarmauri_standard/tool_llms/GeminiToolModel.py): Implements the Gemini tool model.
- [GroqToolModel.py](swarmauri_standard/tool_llms/GroqToolModel.py): Implements the Groq tool model.
- [MistralToolModel.py](swarmauri_standard/tool_llms/MistralToolModel.py): Implements the Mistral tool model.
- [OpenAIToolModel.py](swarmauri_standard/tool_llms/OpenAIToolModel.py): Implements the OpenAI tool model.

### Tools
- [AdditionTool.py](swarmauri_standard/tools/AdditionTool.py): Implements a tool for performing addition operations.
- [AutomatedReadabilityIndexTool.py](swarmauri_standard/tools/AutomatedReadabilityIndexTool.py): Calculates the Automated Readability Index.
- [CalculatorTool.py](swarmauri_standard/tools/CalculatorTool.py): Provides basic calculator functionalities.
- [CodeExtractorTool.py](swarmauri_standard/tools/CodeExtractorTool.py): Extracts code snippets from text.
- [CodeInterpreterTool.py](swarmauri_standard/tools/CodeInterpreterTool.py): Interprets and executes code snippets.
- [ColemanLiauIndexTool.py](swarmauri_standard/tools/ColemanLiauIndexTool.py): Calculates the Coleman-Liau Index.
- [FleschKincaidTool.py](swarmauri_standard/tools/FleschKincaidTool.py): Calculates the Flesch-Kincaid Grade Level.
- [FleschReadingEaseTool.py](swarmauri_standard/tools/FleschReadingEaseTool.py): Calculates the Flesch Reading Ease score.
- [GunningFogTool.py](swarmauri_standard/tools/GunningFogTool.py): Calculates the Gunning Fog Index.
- [ImportMemoryModuleTool.py](swarmauri_standard/tools/ImportMemoryModuleTool.py): Imports memory modules.
- [JSONRequestsTool.py](swarmauri_standard/tools/JSONRequestsTool.py): Handles JSON-based HTTP requests.
- [Parameter.py](swarmauri_standard/tools/Parameter.py): Manages tool parameters.
- [RequestsTool.py](swarmauri_standard/tools/RequestsTool.py): Handles HTTP requests.
- [TemperatureConverterTool.py](swarmauri_standard/tools/TemperatureConverterTool.py): Converts temperatures between different units.
- [TestTool.py](swarmauri_standard/tools/TestTool.py): Implements a test tool.
- [WeatherTool.py](swarmauri_standard/tools/WeatherTool.py): Provides weather-related functionalities.

### Tracing
- [CallableTracer.py](swarmauri_standard/tracing/CallableTracer.py): Traces callable objects.
- [ChainTracer.py](swarmauri_standard/tracing/ChainTracer.py): Traces chains of operations.
- [SimpleTraceContext.py](swarmauri_standard/tracing/SimpleTraceContext.py): Provides a simple trace context.
- [SimpleTracer.py](swarmauri_standard/tracing/SimpleTracer.py): Implements a simple tracer.
- [TracedVariable.py](swarmauri_standard/tracing/TracedVariable.py): Manages traced variables.
- [VariableTracer.py](swarmauri_standard/tracing/VariableTracer.py): Traces variable changes.

### Transports
- [PubSubTransport.py](swarmauri_standard/transports/PubSubTransport.py): Implements a publish-subscribe transport mechanism.

### TTS (Text-to-Speech)
- [HyperbolicTTS.py](swarmauri_standard/tts/HyperbolicTTS.py): Implements text-to-speech using Hyperbolic.
- [OpenaiTTS.py](swarmauri_standard/tts/OpenaiTTS.py): Implements text-to-speech using OpenAI.
- [PlayhtTTS.py](swarmauri_standard/tts/PlayhtTTS.py): Implements text-to-speech using PlayHT.


### Vectors
- [Vector.py](swarmauri_standard/vectors/Vector.py): Defines vector operations and manipulations.

### Vector Stores
- [TfidfVectorStore.py](swarmauri_standard/vector_stores/TfidfVectorStore.py): Implements a vector store using TF-IDF.

### VLMs (Vision-Language Models)
- [FalVLM.py](swarmauri_standard/vlms/FalVLM.py): Implements the Fal Vision-Language Model.
- [GroqVLM.py](swarmauri_standard/vlms/GroqVLM.py): Implements the Groq Vision-Language Model.
- [HyperbolicVLM.py](swarmauri_standard/vlms/HyperbolicVLM.py): Implements the Hyperbolic Vision-Language Model.

# Features

- **Polymorphism**: Allows for dynamic behavior switching between components, enabling flexible, context-aware system behavior.
- **Discriminated Unions**: Provides a robust method for handling multiple possible object types in a type-safe manner.
- **Serialization**: Efficiently encode and decode data for transmission across different environments and system components, with support for both standard and custom serialization formats.
- **Intensional and Extensional Programming**: Leverages both rule-based (intensional) and set-based (extensional) approaches to building and manipulating complex data structures, offering developers a wide range of tools for system design.

## Use Cases

- **Modular Systems**: Develop scalable, pluggable systems that can evolve over time by adding or modifying components without disrupting the entire ecosystem.
- **Distributed Architectures**: Build systems with distributed nodes that seamlessly communicate using the SDK’s standardized interfaces.
- **Third-Party Integrations**: Extend the system's capabilities by easily incorporating third-party tools, libraries, and services.
- **Prototype and Experimentation**: Test cutting-edge ideas using the experimental components in the SDK, while retaining the reliability of core and standard features for production systems.

# Future Development

The Swarmauri SDK is an evolving platform, and the community is encouraged to contribute to its growth. Upcoming releases will focus on enhancing the framework's modularity, providing more advanced serialization methods, and expanding the community-driven component library.


## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, kindly go through the [contributions guidelines](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) first.

