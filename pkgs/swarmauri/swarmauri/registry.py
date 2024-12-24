REGISTRY = {
 'swarmauri.agents.QAAgent': 'swarmauri_standard.agents.QAAgent',
 'swarmauri.agents.RagAgent': 'swarmauri_standard.agents.RagAgent',
 'swarmauri.agents.SimpleConversationAgent': 'swarmauri_standard.agents.SimpleConversationAgent',
 'swarmauri.agents.ToolAgent': 'swarmauri_standard.agents.ToolAgent',
 'swarmauri.chains.CallableChain': 'swarmauri_standard.chains.CallableChain',
 'swarmauri.chains.ChainStep': 'swarmauri_standard.chains.ChainStep',
 'swarmauri.chains.ContextChain': 'swarmauri_standard.chains.ContextChain',
 'swarmauri.chains.PromptContextChain': 'swarmauri_standard.chains.PromptContextChain',
 'swarmauri.chunkers.DelimiterBasedChunker': 'swarmauri_standard.chunkers.DelimiterBasedChunker',
 'swarmauri.chunkers.FixedLengthChunker': 'swarmauri_standard.chunkers.FixedLengthChunker',
 'swarmauri.chunkers.MdSnippetChunker': 'swarmauri_standard.chunkers.MdSnippetChunker',
 'swarmauri.chunkers.SentenceChunker': 'swarmauri_standard.chunkers.SentenceChunker',
 'swarmauri.chunkers.SlidingWindowChunker': 'swarmauri_standard.chunkers.SlidingWindowChunker',
 'swarmauri.control_panels.ControlPanel': 'swarmauri_standard.control_panels.ControlPanel',
 'swarmauri.conversations.Conversation': 'swarmauri_standard.conversations.Conversation',
 'swarmauri.conversations.MaxSizeConversation': 'swarmauri_standard.conversations.MaxSizeConversation',
 'swarmauri.conversations.MaxSystemContextConversation': 'swarmauri_standard.conversations.MaxSystemContextConversation',
 'swarmauri.conversations.SessionCacheConversation': 'swarmauri_standard.conversations.SessionCacheConversation',
 'swarmauri.dataconnectors.GoogleDriveDataConnector': 'swarmauri_standard.dataconnectors.GoogleDriveDataConnector',
 'swarmauri.distances.CanberraDistance': 'swarmauri_standard.distances.CanberraDistance',
 'swarmauri.distances.ChebyshevDistance': 'swarmauri_standard.distances.ChebyshevDistance',
 'swarmauri.distances.ChiSquaredDistance': 'swarmauri_standard.distances.ChiSquaredDistance',
 'swarmauri.distances.CosineDistance': 'swarmauri_standard.distances.CosineDistance',
 'swarmauri.distances.EuclideanDistance': 'swarmauri_standard.distances.EuclideanDistance',
 'swarmauri.distances.HaversineDistance': 'swarmauri_standard.distances.HaversineDistance',
 'swarmauri.distances.JaccardIndexDistance': 'swarmauri_standard.distances.JaccardIndexDistance',
 'swarmauri.distances.LevenshteinDistance': 'swarmauri_standard.distances.LevenshteinDistance',
 'swarmauri.distances.ManhattanDistance': 'swarmauri_standard.distances.ManhattanDistance',
 'swarmauri.distances.MinkowskiDistance': 'swarmauri_standard.distances.MinkowskiDistance',
 'swarmauri.distances.SorensenDiceDistance': 'swarmauri_standard.distances.SorensenDiceDistance',
 'swarmauri.distances.SquaredEuclideanDistance': 'swarmauri_standard.distances.SquaredEuclideanDistance',
 'swarmauri.documents.Document': 'swarmauri_standard.documents.Document',
 'swarmauri.embeddings.CohereEmbedding': 'swarmauri_standard.embeddings.CohereEmbedding',
 'swarmauri.embeddings.GeminiEmbedding': 'swarmauri_standard.embeddings.GeminiEmbedding',
 'swarmauri.embeddings.MistralEmbedding': 'swarmauri_standard.embeddings.MistralEmbedding',
 'swarmauri.embeddings.NmfEmbedding': 'swarmauri_standard.embeddings.NmfEmbedding',
 'swarmauri.embeddings.OpenAIEmbedding': 'swarmauri_standard.embeddings.OpenAIEmbedding',
 'swarmauri.embeddings.TfidfEmbedding': 'swarmauri_standard.embeddings.TfidfEmbedding',
 'swarmauri.embeddings.VoyageEmbedding': 'swarmauri_standard.embeddings.VoyageEmbedding',
 'swarmauri.exceptions.IndexErrorWithContext': 'swarmauri_standard.exceptions.IndexErrorWithContext',
 'swarmauri.factories.AgentFactory': 'swarmauri_standard.factories.AgentFactory',
 'swarmauri.factories.Factory': 'swarmauri_standard.factories.Factory',
 'swarmauri.image_gens.BlackForestImgGenModel': 'swarmauri_standard.image_gens.BlackForestImgGenModel',
 'swarmauri.image_gens.DeepInfraImgGenModel': 'swarmauri_standard.image_gens.DeepInfraImgGenModel',
 'swarmauri.image_gens.FalAIImgGenModel': 'swarmauri_standard.image_gens.FalAIImgGenModel',
 'swarmauri.image_gens.HyperbolicImgGenModel': 'swarmauri_standard.image_gens.HyperbolicImgGenModel',
 'swarmauri.image_gens.OpenAIImgGenModel': 'swarmauri_standard.image_gens.OpenAIImgGenModel',
 'swarmauri.llms.AI21StudioModel': 'swarmauri_standard.llms.AI21StudioModel',
 'swarmauri.llms.AnthropicModel': 'swarmauri_standard.llms.AnthropicModel',
 'swarmauri.llms.AnthropicToolModel': 'swarmauri_standard.llms.AnthropicToolModel',
 'swarmauri.llms.CohereModel': 'swarmauri_standard.llms.CohereModel',
 'swarmauri.llms.CohereToolModel': 'swarmauri_standard.llms.CohereToolModel',
 'swarmauri.llms.DeepInfraModel': 'swarmauri_standard.llms.DeepInfraModel',
 'swarmauri.llms.DeepSeekModel': 'swarmauri_standard.llms.DeepSeekModel',
 'swarmauri.llms.FalAIVisionModel': 'swarmauri_standard.llms.FalAIVisionModel',
 'swarmauri.llms.GeminiProModel': 'swarmauri_standard.llms.GeminiProModel',
 'swarmauri.llms.GeminiToolModel': 'swarmauri_standard.llms.GeminiToolModel',
 'swarmauri.llms.GroqAIAudio': 'swarmauri_standard.llms.GroqAIAudio',
 'swarmauri.llms.GroqModel': 'swarmauri_standard.llms.GroqModel',
 'swarmauri.llms.GroqToolModel': 'swarmauri_standard.llms.GroqToolModel',
 'swarmauri.llms.GroqVisionModel': 'swarmauri_standard.llms.GroqVisionModel',
 'swarmauri.llms.HyperbolicAudioTTS': 'swarmauri_standard.llms.HyperbolicAudioTTS',
 'swarmauri.llms.HyperbolicModel': 'swarmauri_standard.llms.HyperbolicModel',
 'swarmauri.llms.HyperbolicVisionModel': 'swarmauri_standard.llms.HyperbolicVisionModel',
 'swarmauri.llms.MistralModel': 'swarmauri_standard.llms.MistralModel',
 'swarmauri.llms.MistralToolModel': 'swarmauri_standard.llms.MistralToolModel',
 'swarmauri.llms.OpenAIAudio': 'swarmauri_standard.llms.OpenAIAudio',
 'swarmauri.llms.OpenAIAudioTTS': 'swarmauri_standard.llms.OpenAIAudioTTS',
 'swarmauri.llms.OpenAIModel': 'swarmauri_standard.llms.OpenAIModel',
 'swarmauri.llms.OpenAIToolModel': 'swarmauri_standard.llms.OpenAIToolModel',
 'swarmauri.llms.PerplexityModel': 'swarmauri_standard.llms.PerplexityModel',
 'swarmauri.llms.PlayHTModel': 'swarmauri_standard.llms.PlayHTModel',
 'swarmauri.llms.WhisperLargeModel': 'swarmauri_standard.llms.WhisperLargeModel',
 'swarmauri.measurements.CompletenessMeasurement': 'swarmauri_standard.measurements.CompletenessMeasurement',
 'swarmauri.measurements.DistinctivenessMeasurement': 'swarmauri_standard.measurements.DistinctivenessMeasurement',
 'swarmauri.measurements.FirstImpressionMeasurement': 'swarmauri_standard.measurements.FirstImpressionMeasurement',
 'swarmauri.measurements.MeanMeasurement': 'swarmauri_standard.measurements.MeanMeasurement',
 'swarmauri.measurements.MiscMeasurement': 'swarmauri_standard.measurements.MiscMeasurement',
 'swarmauri.measurements.MissingnessMeasurement': 'swarmauri_standard.measurements.MissingnessMeasurement',
 'swarmauri.measurements.PatternMatchingMeasurement': 'swarmauri_standard.measurements.PatternMatchingMeasurement',
 'swarmauri.measurements.RatioOfSumsMeasurement': 'swarmauri_standard.measurements.RatioOfSumsMeasurement',
 'swarmauri.measurements.StaticMeasurement': 'swarmauri_standard.measurements.StaticMeasurement',
 'swarmauri.measurements.UniquenessMeasurement': 'swarmauri_standard.measurements.UniquenessMeasurement',
 'swarmauri.measurements.ZeroMeasurement': 'swarmauri_standard.measurements.ZeroMeasurement',
 'swarmauri.messages.AgentMessage': 'swarmauri_standard.messages.AgentMessage',
 'swarmauri.messages.FunctionMessage': 'swarmauri_standard.messages.FunctionMessage',
 'swarmauri.messages.HumanMessage': 'swarmauri_standard.messages.HumanMessage',
 'swarmauri.messages.SystemMessage': 'swarmauri_standard.messages.SystemMessage',
 'swarmauri.parsers.BeautifulSoupElementParser': 'swarmauri_standard.parsers.BeautifulSoupElementParser',
 'swarmauri.parsers.CSVParser': 'swarmauri_standard.parsers.CSVParser',
 'swarmauri.parsers.HTMLTagStripParser': 'swarmauri_standard.parsers.HTMLTagStripParser',
 'swarmauri.parsers.KeywordExtractorParser': 'swarmauri_standard.parsers.KeywordExtractorParser',
 'swarmauri.parsers.Md2HtmlParser': 'swarmauri_standard.parsers.Md2HtmlParser',
 'swarmauri.parsers.OpenAPISpecParser': 'swarmauri_standard.parsers.OpenAPISpecParser',
 'swarmauri.parsers.PhoneNumberExtractorParser': 'swarmauri_standard.parsers.PhoneNumberExtractorParser',
 'swarmauri.parsers.PythonParser': 'swarmauri_standard.parsers.PythonParser',
 'swarmauri.parsers.RegExParser': 'swarmauri_standard.parsers.RegExParser',
 'swarmauri.parsers.URLExtractorParser': 'swarmauri_standard.parsers.URLExtractorParser',
 'swarmauri.parsers.XMLParser': 'swarmauri_standard.parsers.XMLParser',
 'swarmauri.pipelines.Pipeline': 'swarmauri_standard.pipelines.Pipeline',
 'swarmauri.prompts.Prompt': 'swarmauri_standard.prompts.Prompt',
 'swarmauri.prompts.PromptGenerator': 'swarmauri_standard.prompts.PromptGenerator',
 'swarmauri.prompts.PromptMatrix': 'swarmauri_standard.prompts.PromptMatrix',
 'swarmauri.prompts.PromptTemplate': 'swarmauri_standard.prompts.PromptTemplate',
 'swarmauri.schema_converters.AnthropicSchemaConverter': 'swarmauri_standard.schema_converters.AnthropicSchemaConverter',
 'swarmauri.schema_converters.CohereSchemaConverter': 'swarmauri_standard.schema_converters.CohereSchemaConverter',
 'swarmauri.schema_converters.GeminiSchemaConverter': 'swarmauri_standard.schema_converters.GeminiSchemaConverter',
 'swarmauri.schema_converters.GroqSchemaConverter': 'swarmauri_standard.schema_converters.GroqSchemaConverter',
 'swarmauri.schema_converters.MistralSchemaConverter': 'swarmauri_standard.schema_converters.MistralSchemaConverter',
 'swarmauri.schema_converters.OpenAISchemaConverter': 'swarmauri_standard.schema_converters.OpenAISchemaConverter',
 'swarmauri.schema_converters.ShuttleAISchemaConverter': 'swarmauri_standard.schema_converters.ShuttleAISchemaConverter',
 'swarmauri.service_registries.ServiceRegistry': 'swarmauri_standard.service_registries.ServiceRegistry',
 'swarmauri.state.DictState': 'swarmauri_standard.state.DictState',
 'swarmauri.swarms.Swarm': 'swarmauri_standard.swarms.Swarm',
 'swarmauri.task_mgt_strategies.RoundRobinStrategy': 'swarmauri_standard.task_mgt_strategies.RoundRobinStrategy',
 'swarmauri.toolkits.AccessibilityToolkit': 'swarmauri_standard.toolkits.AccessibilityToolkit',
 'swarmauri.toolkits.Toolkit': 'swarmauri_standard.toolkits.Toolkit',
 'swarmauri.tools.AdditionTool': 'swarmauri_standard.tools.AdditionTool',
 'swarmauri.tools.AutomatedReadabilityIndexTool': 'swarmauri_standard.tools.AutomatedReadabilityIndexTool',
 'swarmauri.tools.CalculatorTool': 'swarmauri_standard.tools.CalculatorTool',
 'swarmauri.tools.CodeExtractorTool': 'swarmauri_standard.tools.CodeExtractorTool',
 'swarmauri.tools.CodeInterpreterTool': 'swarmauri_standard.tools.CodeInterpreterTool',
 'swarmauri.tools.ColemanLiauIndexTool': 'swarmauri_standard.tools.ColemanLiauIndexTool',
 'swarmauri.tools.FleschKincaidTool': 'swarmauri_standard.tools.FleschKincaidTool',
 'swarmauri.tools.FleschReadingEaseTool': 'swarmauri_standard.tools.FleschReadingEaseTool',
 'swarmauri.tools.GunningFogTool': 'swarmauri_standard.tools.GunningFogTool',
 'swarmauri.tools.ImportMemoryModuleTool': 'swarmauri_standard.tools.ImportMemoryModuleTool',
 'swarmauri.tools.JSONRequestsTool': 'swarmauri_standard.tools.JSONRequestsTool',
 'swarmauri.tools.MatplotlibCsvTool': 'swarmauri_standard.tools.MatplotlibCsvTool',
 'swarmauri.tools.MatplotlibTool': 'swarmauri_standard.tools.MatplotlibTool',
 'swarmauri.tools.Parameter': 'swarmauri_standard.tools.Parameter',
 'swarmauri.tools.RequestsTool': 'swarmauri_standard.tools.RequestsTool',
 'swarmauri.tools.SentenceComplexityTool': 'swarmauri_standard.tools.SentenceComplexityTool',
 'swarmauri.tools.TemperatureConverterTool': 'swarmauri_standard.tools.TemperatureConverterTool',
 'swarmauri.tools.TestTool': 'swarmauri_standard.tools.TestTool',
 'swarmauri.tools.WeatherTool': 'swarmauri_standard.tools.WeatherTool',
 'swarmauri.tracing.CallableTracer': 'swarmauri_standard.tracing.CallableTracer',
 'swarmauri.tracing.ChainTracer': 'swarmauri_standard.tracing.ChainTracer',
 'swarmauri.tracing.SimpleTraceContext': 'swarmauri_standard.tracing.SimpleTraceContext',
 'swarmauri.tracing.SimpleTracer': 'swarmauri_standard.tracing.SimpleTracer',
 'swarmauri.tracing.TracedVariable': 'swarmauri_standard.tracing.TracedVariable',
 'swarmauri.tracing.VariableTracer': 'swarmauri_standard.tracing.VariableTracer',
 'swarmauri.transports.PubSubTransport': 'swarmauri_standard.transports.PubSubTransport',
 'swarmauri.utils.LazyLoader': 'swarmauri_standard.utils.LazyLoader',
 'swarmauri.utils._get_subclasses': 'swarmauri_standard.utils._get_subclasses',
 'swarmauri.utils._lazy_import': 'swarmauri_standard.utils._lazy_import',
 'swarmauri.utils.apply_metaclass': 'swarmauri_standard.utils.apply_metaclass',
 'swarmauri.utils.base64_encoder': 'swarmauri_standard.utils.base64_encoder',
 'swarmauri.utils.base64_to_file_path': 'swarmauri_standard.utils.base64_to_file_path',
 'swarmauri.utils.base64_to_img_url': 'swarmauri_standard.utils.base64_to_img_url',
 'swarmauri.utils.base64_to_in_memory_img': 'swarmauri_standard.utils.base64_to_in_memory_img',
 'swarmauri.utils.decorate': 'swarmauri_standard.utils.decorate',
 'swarmauri.utils.duration_manager': 'swarmauri_standard.utils.duration_manager',
 'swarmauri.utils.file_path_to_base64': 'swarmauri_standard.utils.file_path_to_base64',
 'swarmauri.utils.file_path_to_img_url': 'swarmauri_standard.utils.file_path_to_img_url',
 'swarmauri.utils.file_path_to_in_memory_img': 'swarmauri_standard.utils.file_path_to_in_memory_img',
 'swarmauri.utils.get_class_hash': 'swarmauri_standard.utils.get_class_hash',
 'swarmauri.utils.img_url_to_base64': 'swarmauri_standard.utils.img_url_to_base64',
 'swarmauri.utils.img_url_to_file_path': 'swarmauri_standard.utils.img_url_to_file_path',
 'swarmauri.utils.img_url_to_in_memory_img': 'swarmauri_standard.utils.img_url_to_in_memory_img',
 'swarmauri.utils.in_memory_img_to_base64': 'swarmauri_standard.utils.in_memory_img_to_base64',
 'swarmauri.utils.in_memory_img_to_file_path': 'swarmauri_standard.utils.in_memory_img_to_file_path',
 'swarmauri.utils.in_memory_img_to_img_url': 'swarmauri_standard.utils.in_memory_img_to_img_url',
 'swarmauri.utils.json_validator': 'swarmauri_standard.utils.json_validator',
 'swarmauri.utils.load_documents_from_folder': 'swarmauri_standard.utils.load_documents_from_folder',
 'swarmauri.utils.load_documents_from_json': 'swarmauri_standard.utils.load_documents_from_json',
 'swarmauri.utils.memoize': 'swarmauri_standard.utils.memoize',
 'swarmauri.utils.method_signature_extractor_decorator': 'swarmauri_standard.utils.method_signature_extractor_decorator',
 'swarmauri.utils.print_notebook_metadata': 'swarmauri_standard.utils.print_notebook_metadata',
 'swarmauri.utils.retry_decorator': 'swarmauri_standard.utils.retry_decorator',
 'swarmauri.utils.sql_log': 'swarmauri_standard.utils.sql_log',
 'swarmauri.utils.timeout_wrapper': 'swarmauri_standard.utils.timeout_wrapper',
 'swarmauri.vector_stores.SqliteVectorStore': 'swarmauri_standard.vector_stores.SqliteVectorStore',
 'swarmauri.vector_stores.TfidfVectorStore': 'swarmauri_standard.vector_stores.TfidfVectorStore',
 'swarmauri.vectors.Vector': 'swarmauri_standard.vectors.Vector'
 }

def get_external_module_path(resource_path):
    """
    Get the external module path for a given resource path.
    
    :param resource_path: Full resource path (e.g., "swarmauri.llms.OpenAIModel.OpenAiModel").
    :return: External module path (e.g., "external_repo.OpenAiModel") or None if not found.
    """
    return REGISTRY.get(resource_path)