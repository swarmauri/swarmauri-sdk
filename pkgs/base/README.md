
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-base/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-base" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/base/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/base.svg"/></a>
    <a href="https://pypi.org/project/swarmauri-base/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-base" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-base/">
        <img src="https://img.shields.io/pypi/l/swarmauri-base" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri-base/">
        <img src="https://img.shields.io/pypi/v/swarmauri-base?label=swarmauri-base&color=green" alt="PyPI - swarmauri-base"/></a>

</p>

---

# Swarmauri Base

## Getting Started

### Installing Swarmauri Base from pypi

To start developing with the Core Library, include it as a module in your Python project. Ensure you have Python 3.10 or later installed.

```sh
pip install swarmauri-base
```



### Example Usage:

```python
# Example of using the base class
from swarmauri_base.llms.LLMBase import LLMBase

class MyConcreteClass(LLMBase):
    
    pass
```

## Features

### agents
- [`AgentBase.py`](./swarmauri_base/agents/AgentBase.py): Base class for agents.
- [`AgentConversationMixin.py`](./swarmauri_base/agents/AgentConversationMixin.py): Mixin for conversation capabilities.
- [`AgentRetrieveMixin.py`](./swarmauri_base/agents/AgentRetrieveMixin.py): Mixin for retrieval functionalities.
- [`AgentSystemContextMixin.py`](./swarmauri_base/agents/AgentSystemContextMixin.py): Mixin for system context.
- [`AgentToolMixin.py`](./swarmauri_base/agents/AgentToolMixin.py): Mixin for tool integration.
- [`AgentVectorStoreMixin.py`](./swarmauri_base/agents/AgentVectorStoreMixin.py): Mixin for vector store functionalities.

### chains
- [`ChainBase.py`](./swarmauri_base/chains/ChainBase.py): Base class for chains.
- [`ChainContextBase.py`](./swarmauri_base/chains/ChainContextBase.py): Base class for chain context.
- [`ChainStepBase.py`](./swarmauri_base/chains/ChainStepBase.py): Base class for chain steps.
- [`PromptContextChainBase.py`](./swarmauri_base/chains/PromptContextChainBase.py): Base class for prompt context chains.

### chunkers
- [`ChunkerBase.py`](./swarmauri_base/chunkers/ChunkerBase.py): Base class for chunkers.

### control_panels
- [`ControlPanelBase.py`](./swarmauri_base/control_panels/ControlPanelBase.py): Base class for control panels.

### conversations
- [`ConversationBase.py`](./swarmauri_base/conversations/ConversationBase.py): Base class for conversations.
- [`ConversationSystemContextMixin.py`](./swarmauri_base/conversations/ConversationSystemContextMixin.py): Mixin for system context in conversations.

### dataconnectors
- [`DataConnectorBase.py`](./swarmauri_base/dataconnectors/DataConnectorBase.py): Base class for data connectors.

### distances
- [`DistanceBase.py`](./swarmauri_base/distances/DistanceBase.py): Base class for distance calculations.
- [`VisionDistanceBase.py`](./swarmauri_base/distances/VisionDistanceBase.py): Base class for vision distance calculations.

### documents
- [`DocumentBase.py`](./swarmauri_base/documents/DocumentBase.py): Base class for documents.

### document_stores
- [`DocumentStoreBase.py`](./swarmauri_base/document_stores/DocumentStoreBase.py): Base class for document stores.
- [`DocumentStoreRetrieveBase.py`](./swarmauri_base/document_stores/DocumentStoreRetrieveBase.py): Base class for document retrieval.

### embeddings
- [`EmbeddingBase.py`](./swarmauri_base/embeddings/EmbeddingBase.py): Base class for embeddings.
- [`VisionEmbeddingBase.py`](./swarmauri_base/embeddings/VisionEmbeddingBase.py): Base class for vision embeddings.

### factories
- [`FactoryBase.py`](./swarmauri_base/factories/FactoryBase.py): Base class for factories.

### image_gens
- [`ImageGenBase.py`](./swarmauri_base/image_gens/ImageGenBase.py): Base class for image generation.

### llms
- [`LLMBase.py`](./swarmauri_base/llms/LLMBase.py): Base class for large language models.

### logging
- [`HandlerBase.py`](./swarmauri_base/logging/HandlerBase.py): Base class for logging handlers.
- [`LoggerBase.py`](./swarmauri_base/logging/LoggerBase.py): Base class for loggers.

### measurements
- [`MeasurementAggregateMixin.py`](./swarmauri_base/measurements/MeasurementAggregateMixin.py): Mixin for measurement aggregation.
- [`MeasurementBase.py`](./swarmauri_base/measurements/MeasurementBase.py): Base class for measurements.
- [`MeasurementCalculateMixin.py`](./swarmauri_base/measurements/MeasurementCalculateMixin.py): Mixin for measurement calculations.
- [`MeasurementThresholdMixin.py`](./swarmauri_base/measurements/MeasurementThresholdMixin.py): Mixin for measurement thresholds.

### messages
- [`MessageBase.py`](./swarmauri_base/messages/MessageBase.py): Base class for messages.

### ocrs
- [`OCRBase.py`](./swarmauri_base/ocrs/OCRBase.py): Base class for OCR functionalities.

### parsers
- [`ParserBase.py`](./swarmauri_base/parsers/ParserBase.py): Base class for parsers.

### pipelines
- [`PipelineBase.py`](./swarmauri_base/pipelines/PipelineBase.py): Base class for pipelines.

### prompts
- [`PromptBase.py`](./swarmauri_base/prompts/PromptBase.py): Base class for prompts.
- [`PromptGeneratorBase.py`](./swarmauri_base/prompts/PromptGeneratorBase.py): Base class for prompt generators.
- [`PromptMatrixBase.py`](./swarmauri_base/prompts/PromptMatrixBase.py): Base class for prompt matrices.

### prompt_templates
- [`PromptTemplateBase.py`](./swarmauri_base/prompt_templates/PromptTemplateBase.py): Base class for prompt templates.

### schema_converters
- [`SchemaConverterBase.py`](./swarmauri_base/schema_converters/SchemaConverterBase.py): Base class for schema converters.

### service_registries
- [`ServiceRegistryBase.py`](./swarmauri_base/service_registries/ServiceRegistryBase.py): Base class for service registries.

### state
- [`StateBase.py`](./swarmauri_base/state/StateBase.py): Base class for state management.

### stt
- [`STTBase.py`](./swarmauri_base/stt/STTBase.py): Base class for speech-to-text functionalities.

### swarms
- [`SwarmBase.py`](./swarmauri_base/swarms/SwarmBase.py): Base class for swarm intelligence.

### task_mgmt_strategies
- [`TaskMgmtStrategyBase.py`](./swarmauri_base/task_mgmt_strategies/TaskMgmtStrategyBase.py): Base class for task management strategies.

### toolkits
- [`ToolkitBase.py`](./swarmauri_base/toolkits/ToolkitBase.py): Base class for toolkits.

### tool_llms
- [`ToolLLMBase.py`](./swarmauri_base/tool_llms/ToolLLMBase.py): Base class for tools for large language models.

### tools
- [`ParameterBase.py`](./swarmauri_base/tools/ParameterBase.py): Base class for parameters.
- [`ToolBase.py`](./swarmauri_base/tools/ToolBase.py): Base class for tools.

### transports
- [`TransportBase.py`](./swarmauri_base/transports/TransportBase.py): Base class for transports.

### tts
- [`TTSBase.py`](./swarmauri_base/tts/TTSBase.py): Base class for text-to-speech functionalities.

### vectors
- [`VectorBase.py`](./swarmauri_base/vectors/VectorBase.py): Base class for vectors.

### vector_stores
- [`VectorStoreBase.py`](./swarmauri_base/vector_stores/VectorStoreBase.py): Base class for vector stores.
- [`VectorStoreCloudMixin.py`](./swarmauri_base/vector_stores/VectorStoreCloudMixin.py): Mixin for cloud vector stores.
- [`VectorStorePersistentMixin.py`](./swarmauri_base/vector_stores/VectorStorePersistentMixin.py): Mixin for persistent vector stores.
- [`VectorStoreRetrieveMixin.py`](./swarmauri_base/vector_stores/VectorStoreRetrieveMixin.py): Mixin for vector store retrieval.
- [`VectorStoreSaveLoadMixin.py`](./swarmauri_base/vector_stores/VectorStoreSaveLoadMixin.py): Mixin for saving and loading vector stores.
- [`VisionVectorStoreBase.py`](./swarmauri_base/vector_stores/VisionVectorStoreBase.py): Base class for vision vector stores.

### vlms
- [`VLMBase.py`](./swarmauri_base/vlms/VLMBase.py): Base class for visual language models.


## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, kindly go through the [contributions guidelines](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) first.
