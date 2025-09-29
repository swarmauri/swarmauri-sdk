# plugin_citizenship_registry.py

"""
plugin_citizenship_registry.py

Defines the PluginCitizenshipRegistry class responsible for managing plugin registrations across
first, second, and third-class citizens within the swarmauri framework.
"""

import logging
from importlib.metadata import EntryPoint
from typing import Dict, Optional

# Configure logger
logger = logging.getLogger(__name__)


class PluginCitizenshipRegistry:
    """
    PluginCitizenshipRegistry

    A centralized class to manage the registration and retrieval of plugins categorized
    as first, second, or third-class citizens within the swarmauri framework.

    Citizenship Classification:
        - **First-Class Plugins**:
            - Pre-registered and have priority.
            - Mapped under specific namespaces like `swarmauri.agents`.
            - Must implement required interfaces.
        - **Second-Class Plugins**:
            - Community-contributed.
            - Not pre-registered but share the same namespace as first-class plugins.
            - Must implement required interfaces.
        - **Third-Class Plugins**:
            - Generic plugins not tied to specific resource kinds.
            - Mapped under `swarmauri.plugins`.
            - Do not require interface validation.

    Mappings:
        - **Resource Path to Module Path**: Each plugin is identified by a unique resource path (e.g.,
          `'swarmauri.llms.OpenAIModel'`), which maps to its corresponding external module path (e.g.,
          `'external_repo.OpenAIModel'`). This mapping facilitates dynamic loading and validation
          of plugins based on their classification and interface requirements.
    """

    # Class variables for registries
    FIRST_CLASS_REGISTRY: Dict[str, str] = {
        "swarmauri.crypto.ICrypto": "swarmauri_core.crypto.ICrypto",
        "swarmauri.crypto.CryptoBase": "swarmauri_base.crypto.CryptoBase",
        "swarmauri.signings.Ed25519EnvelopeSigner": "swarmauri_signing_ed25519.Ed25519EnvelopeSigner",
        "swarmauri.signing.ISigning": "swarmauri_core.signing.ISigning",
        "swarmauri.signing.SigningBase": "swarmauri_base.signing.SigningBase",
        "swarmauri.signings.PgpEnvelopeSigner": "swarmauri_signing_pgp.PgpEnvelopeSigner",
        "swarmauri.signings.Secp256k1EnvelopeSigner": "swarmauri_signing_secp256k1.Secp256k1EnvelopeSigner",
        "swarmauri.signings.HmacEnvelopeSigner": "swarmauri_signing_hmac.HmacEnvelopeSigner",
        "swarmauri.signings.EcdsaEnvelopeSigner": "swarmauri_signing_ecdsa.EcdsaEnvelopeSigner",
        "swarmauri.signings.RSAEnvelopeSigner": "swarmauri_signing_rsa.RSAEnvelopeSigner",
        "swarmauri.signings.SshEnvelopeSigner": "swarmauri_signing_ssh.SshEnvelopeSigner",
        "swarmauri.signings.JwsSignerVerifier": "swarmauri_signing_jws.JwsSignerVerifier",
        "swarmauri.cipher_suites.ICipherSuite": "swarmauri_core.cipher_suites.ICipherSuite",
        "swarmauri.cipher_suites.CipherSuiteBase": "swarmauri_base.cipher_suites.CipherSuiteBase",
        "swarmauri.cipher_suites.JwaCipherSuite": "swarmauri_cipher_jwa.JwaCipherSuite",
        "swarmauri.cipher_suites.CoseCipherSuite": "swarmauri_cipher_cose.CoseCipherSuite",
        "swarmauri.cipher_suites.FipsCipherSuite": "swarmauri_cipher_fips1403.FipsCipherSuite",
        "swarmauri.cipher_suites.JwsCipherSuite": "swarmauri_cipher_jws.JwsCipherSuite",
        "swarmauri.cipher_suites.Tls13CipherSuite": "swarmauri_cipher_tls13.Tls13CipherSuite",
        "swarmauri.cipher_suites.WebAuthnCipherSuite": "swarmauri_cipher_webauthn.WebAuthnCipherSuite",
        "swarmauri.cipher_suites.SigstoreCipherSuite": "swarmauri_cipher_sigstore.SigstoreCipherSuite",
        "swarmauri.cipher_suites.SshCipherSuite": "swarmauri_cipher_ssh.SshCipherSuite",
        "swarmauri.cipher_suites.IpsecCipherSuite": "swarmauri_cipher_ipsec.IpsecCipherSuite",
        "swarmauri.cipher_suites.CadesCipherSuite": "swarmauri_cipher_cades.CadesCipherSuite",
        "swarmauri.cipher_suites.XadesCipherSuite": "swarmauri_cipher_xades.XadesCipherSuite",
        "swarmauri.cipher_suites.PadesCipherSuite": "swarmauri_cipher_pades.PadesCipherSuite",
        "swarmauri.cipher_suites.Cnsa20CipherSuite": "swarmauri_cipher_cnsa20.Cnsa20CipherSuite",
        "swarmauri.tokens.JWTTokenService": "swarmauri_tokens_jwt.JWTTokenService",
        "swarmauri.tokens.SshSigTokenService": "swarmauri_tokens_sshsig.SshSigTokenService",
        "swarmauri.tokens.SshCertTokenService": "swarmauri_tokens_sshcert.SshCertTokenService",
        "swarmauri.tokens.IntrospectionTokenService": "swarmauri_tokens_introspection.IntrospectionTokenService",
        "swarmauri.tokens.PasetoV4TokenService": "swarmauri_tokens_paseto_v4.PasetoV4TokenService",
        "swarmauri.tokens.CompositeTokenService": "swarmauri_tokens_composite.CompositeTokenService",
        "swarmauri.tokens.RemoteOIDCTokenService": "swarmauri_tokens_remoteoidc.RemoteOIDCTokenService",
        "swarmauri.tokens.DPoPBoundJWTTokenService": "swarmauri_tokens_dpopboundjwt.DPoPBoundJWTTokenService",
        "swarmauri.tokens.RotatingJWTTokenService": "swarmauri_tokens_rotatingjwt.RotatingJWTTokenService",
        "swarmauri.tokens.TlsBoundJWTTokenService": "swarmauri_tokens_tlsboundjwt.TlsBoundJWTTokenService",
        ###
        # key providers
        ###
        "swarmauri.key_providers.IKeyProvider": "swarmauri_core.keys.IKeyProvider",
        "swarmauri.key_providers.KeyProviderBase": "swarmauri_base.keys.KeyProviderBase",
        "swarmauri.key_providers.InMemoryKeyProvider": "swarmauri_standard.key_providers.InMemoryKeyProvider",
        "swarmauri.agents.ExampleAgent": "swm_example_package.ExampleAgent",
        "swarmauri.agents.QAAgent": "swarmauri_standard.agents.QAAgent",
        "swarmauri.agents.RagAgent": "swarmauri_standard.agents.RagAgent",
        "swarmauri.agents.SimpleConversationAgent": "swarmauri_standard.agents.SimpleConversationAgent",
        "swarmauri.agents.ToolAgent": "swarmauri_standard.agents.ToolAgent",
        "swarmauri.chains.CallableChain": "swarmauri_standard.chains.CallableChain",
        "swarmauri.chains.ChainStep": "swarmauri_standard.chains.ChainStep",
        "swarmauri.chains.ContextChain": "swarmauri_standard.chains.ContextChain",
        "swarmauri.chains.PromptContextChain": "swarmauri_standard.chains.PromptContextChain",
        "swarmauri.chunkers.DelimiterBasedChunker": "swarmauri_standard.chunkers.DelimiterBasedChunker",
        "swarmauri.chunkers.FixedLengthChunker": "swarmauri_standard.chunkers.FixedLengthChunker",
        "swarmauri.chunkers.MdSnippetChunker": "swarmauri_standard.chunkers.MdSnippetChunker",
        "swarmauri.chunkers.SentenceChunker": "swarmauri_standard.chunkers.SentenceChunker",
        "swarmauri.chunkers.SlidingWindowChunker": "swarmauri_standard.chunkers.SlidingWindowChunker",
        "swarmauri.control_panels.ControlPanel": "swarmauri_standard.control_panels.ControlPanel",
        "swarmauri.conversations.Conversation": "swarmauri_standard.conversations.Conversation",
        "swarmauri.conversations.MaxSizeConversation": "swarmauri_standard.conversations.MaxSizeConversation",
        "swarmauri.conversations.MaxSystemContextConversation": "swarmauri_standard.conversations.MaxSystemContextConversation",
        "swarmauri.conversations.SessionCacheConversation": "swarmauri_standard.conversations.SessionCacheConversation",
        "swarmauri.dataconnectors.GoogleDriveDataConnector": "swarmauri_standard.dataconnectors.GoogleDriveDataConnector",
        "swarmauri.distances.CanberraDistance": "swarmauri_standard.distances.CanberraDistance",
        "swarmauri.distances.ChebyshevDistance": "swarmauri_standard.distances.ChebyshevDistance",
        "swarmauri.distances.ChiSquaredDistance": "swarmauri_standard.distances.ChiSquaredDistance",
        "swarmauri.distances.CosineDistance": "swarmauri_standard.distances.CosineDistance",
        "swarmauri.distances.EuclideanDistance": "swarmauri_standard.distances.EuclideanDistance",
        "swarmauri.distances.HaversineDistance": "swarmauri_standard.distances.HaversineDistance",
        "swarmauri.distances.JaccardIndexDistance": "swarmauri_standard.distances.JaccardIndexDistance",
        "swarmauri.distances.LevenshteinDistance": "swarmauri_standard.distances.LevenshteinDistance",
        "swarmauri.distances.ManhattanDistance": "swarmauri_standard.distances.ManhattanDistance",
        # "swarmauri.distances.MinkowskiDistance": "swarmauri_standard.distances.MinkowskiDistance",
        "swarmauri.distances.SorensenDiceDistance": "swarmauri_standard.distances.SorensenDiceDistance",
        "swarmauri.distances.SquaredEuclideanDistance": "swarmauri_standard.distances.SquaredEuclideanDistance",
        ###
        # decorators
        ###
        "swarmauri.decorators.maybe_async": "swarmauri.decorators.maybe_async",
        "swarmauri.decorators.tool_decorator": "swarmauri.decorators.tool_decorator",
        "swarmauri.decorators.retry_on_status_codes": "swarmauri.decorators.retry_on_status_codes",
        "swarmauri.decorators.deprecate": "swarmauri.decorators.deprecate",
        ###
        # documents
        ###
        "swarmauri.documents.Document": "swarmauri_standard.documents.Document",
        ###
        # embeddings
        ###
        "swarmauri.embeddings.CohereEmbedding": "swarmauri_standard.embeddings.CohereEmbedding",
        "swarmauri.embeddings.GeminiEmbedding": "swarmauri_standard.embeddings.GeminiEmbedding",
        "swarmauri.embeddings.MistralEmbedding": "swarmauri_standard.embeddings.MistralEmbedding",
        # "swarmauri.embeddings.NmfEmbedding": "swarmauri_standard.embeddings.NmfEmbedding",
        "swarmauri.embeddings.OpenAIEmbedding": "swarmauri_standard.embeddings.OpenAIEmbedding",
        "swarmauri.embeddings.TfidfEmbedding": "swarmauri_standard.embeddings.TfidfEmbedding",
        "swarmauri.embeddings.VoyageEmbedding": "swarmauri_standard.embeddings.VoyageEmbedding",
        "swarmauri.exceptions.IndexErrorWithContext": "swarmauri_standard.exceptions.IndexErrorWithContext",
        "swarmauri.factories.AgentFactory": "swarmauri_standard.factories.AgentFactory",
        "swarmauri.factories.Factory": "swarmauri_standard.factories.Factory",
        "swarmauri.image_gens.BlackForestImgGenModel": "swarmauri_standard.image_gens.BlackForestImgGenModel",
        "swarmauri.image_gens.DeepInfraImgGenModel": "swarmauri_standard.image_gens.DeepInfraImgGenModel",
        "swarmauri.image_gens.FalAIImgGenModel": "swarmauri_standard.image_gens.FalAIImgGenModel",
        "swarmauri.image_gens.HyperbolicImgGenModel": "swarmauri_standard.image_gens.HyperbolicImgGenModel",
        "swarmauri.image_gens.OpenAIImgGenModel": "swarmauri_standard.image_gens.OpenAIImgGenModel",
        ###
        # LLMS
        ##
        "swarmauri.llms.AI21StudioModel": "swarmauri_standard.llms.AI21StudioModel",
        "swarmauri.llms.AnthropicModel": "swarmauri_standard.llms.AnthropicModel",
        "swarmauri.llms.AnthropicToolModel": "swarmauri_standard.llms.AnthropicToolModel",
        "swarmauri.llms.CerebrasModel": "swarmauri_standard.llms.CerebrasModel",
        "swarmauri.llms.CohereModel": "swarmauri_standard.llms.CohereModel",
        "swarmauri.llms.CohereToolModel": "swarmauri_standard.llms.CohereToolModel",
        "swarmauri.llms.DeepInfraModel": "swarmauri_standard.llms.DeepInfraModel",
        "swarmauri.llms.DeepSeekModel": "swarmauri_standard.llms.DeepSeekModel",
        "swarmauri.llms.FalAIVisionModel": "swarmauri_standard.llms.FalAIVisionModel",
        "swarmauri.llms.GeminiProModel": "swarmauri_standard.llms.GeminiProModel",
        "swarmauri.llms.GeminiToolModel": "swarmauri_standard.llms.GeminiToolModel",
        "swarmauri.llms.GroqAIAudio": "swarmauri_standard.llms.GroqAIAudio",
        "swarmauri.llms.GroqModel": "swarmauri_standard.llms.GroqModel",
        "swarmauri.llms.GroqToolModel": "swarmauri_standard.llms.GroqToolModel",
        "swarmauri.llms.GroqVisionModel": "swarmauri_standard.llms.GroqVisionModel",
        "swarmauri.llms.HyperbolicAudioTTS": "swarmauri_standard.llms.HyperbolicAudioTTS",
        "swarmauri.llms.HyperbolicModel": "swarmauri_standard.llms.HyperbolicModel",
        "swarmauri.llms.HyperbolicVisionModel": "swarmauri_standard.llms.HyperbolicVisionModel",
        "swarmauri.llms.LlamaCppModel": "swarmauri_standard.llms.LlamaCppModel",
        "swarmauri.llms.MistralModel": "swarmauri_standard.llms.MistralModel",
        "swarmauri.llms.MistralToolModel": "swarmauri_standard.llms.MistralToolModel",
        "swarmauri.llms.OpenAIAudio": "swarmauri_standard.llms.OpenAIAudio",
        "swarmauri.llms.OpenAIAudioTTS": "swarmauri_standard.llms.OpenAIAudioTTS",
        "swarmauri.llms.OpenAIModel": "swarmauri_standard.llms.OpenAIModel",
        "swarmauri.llms.OpenAIToolModel": "swarmauri_standard.llms.OpenAIToolModel",
        "swarmauri.llms.PerplexityModel": "swarmauri_standard.llms.PerplexityModel",
        "swarmauri.llms.PlayHTModel": "swarmauri_standard.llms.PlayHTModel",
        "swarmauri.llms.WhisperLargeModel": "swarmauri_standard.llms.WhisperLargeModel",
        ###
        # Tool LLMS
        ###
        "swarmauri.tool_llms.OpenAIToolModel": "swarmauri_standard.tool_llms.OpenAIToolModel",
        "swarmauri.tool_llms.AnthropicToolModel": "swarmauri_standard.tool_llms.AnthropicToolModel",
        "swarmauri.tool_llms.CohereToolModel": "swarmauri_standard.tool_llms.CohereToolModel",
        "swarmauri.tool_llms.GeminiToolModel": "swarmauri_standard.tool_llms.GeminiToolModel",
        "swarmauri.tool_llms.GroqToolModel": "swarmauri_standard.tool_llms.GroqToolModel",
        "swarmauri.tool_llms.MistralToolModel": "swarmauri_standard.tool_llms.MistralToolModel",
        "swarmauri.tool_llms.ToolLLM": "swarmauri_standard.tool_llms.ToolLLM",
        "swarmauri.stt.WhisperLargeSTT": "swarmauri_standard.stt.WhisperLargeSTT",
        "swarmauri.stt.GroqSTT": "swarmauri_standard.stt.GroqSTT",
        "swarmauri.stt.OpenaiSTT": "swarmauri_standard.stt.OpenaiSTT",
        "swarmauri.tts.HyperbolicTTS": "swarmauri_standard.tts.HyperbolicTTS",
        "swarmauri.tts.OpenaiTTS": "swarmauri_standard.tts.OpenaiTTS",
        "swarmauri.tts.PlayhtTTS": "swarmauri_standard.tts.PlayhtTTS",
        "swarmauri.vlms.FalVLM": "swarmauri_standard.vlms.FalVLM",
        "swarmauri.vlms.GroqVLM": "swarmauri_standard.vlms.GroqVLM",
        "swarmauri.vlms.HyperbolicVLM": "swarmauri_standard.vlms.HyperbolicVLM",
        "swarmauri.measurements.CompletenessMeasurement": "swarmauri_standard.measurements.CompletenessMeasurement",
        "swarmauri.measurements.DistinctivenessMeasurement": "swarmauri_standard.measurements.DistinctivenessMeasurement",
        "swarmauri.measurements.FirstImpressionMeasurement": "swarmauri_standard.measurements.FirstImpressionMeasurement",
        "swarmauri.measurements.MeanMeasurement": "swarmauri_standard.measurements.MeanMeasurement",
        "swarmauri.measurements.MiscMeasurement": "swarmauri_standard.measurements.MiscMeasurement",
        "swarmauri.measurements.MissingnessMeasurement": "swarmauri_standard.measurements.MissingnessMeasurement",
        "swarmauri.measurements.PatternMatchingMeasurement": "swarmauri_standard.measurements.PatternMatchingMeasurement",
        "swarmauri.measurements.RatioOfSumsMeasurement": "swarmauri_standard.measurements.RatioOfSumsMeasurement",
        "swarmauri.measurements.StaticMeasurement": "swarmauri_standard.measurements.StaticMeasurement",
        "swarmauri.measurements.UniquenessMeasurement": "swarmauri_standard.measurements.UniquenessMeasurement",
        "swarmauri.measurements.ZeroMeasurement": "swarmauri_standard.measurements.ZeroMeasurement",
        "swarmauri.messages.AgentMessage": "swarmauri_standard.messages.AgentMessage",
        "swarmauri.messages.FunctionMessage": "swarmauri_standard.messages.FunctionMessage",
        "swarmauri.messages.HumanMessage": "swarmauri_standard.messages.HumanMessage",
        "swarmauri.messages.SystemMessage": "swarmauri_standard.messages.SystemMessage",
        # "swarmauri.parsers.BeautifulSoupElementParser": "swarmauri_standard.parsers.BeautifulSoupElementParser",
        "swarmauri.parsers.CSVParser": "swarmauri_standard.parsers.CSVParser",
        "swarmauri.parsers.HTMLTagStripParser": "swarmauri_standard.parsers.HTMLTagStripParser",
        # "swarmauri.parsers.KeywordExtractorParser": "swarmauri_standard.parsers.KeywordExtractorParser",
        "swarmauri.parsers.Md2HtmlParser": "swarmauri_standard.parsers.Md2HtmlParser",
        "swarmauri.parsers.OpenAPISpecParser": "swarmauri_standard.parsers.OpenAPISpecParser",
        "swarmauri.parsers.PhoneNumberExtractorParser": "swarmauri_standard.parsers.PhoneNumberExtractorParser",
        "swarmauri.parsers.PythonParser": "swarmauri_standard.parsers.PythonParser",
        "swarmauri.parsers.RegExParser": "swarmauri_standard.parsers.RegExParser",
        "swarmauri.parsers.URLExtractorParser": "swarmauri_standard.parsers.URLExtractorParser",
        "swarmauri.parsers.XMLParser": "swarmauri_standard.parsers.XMLParser",
        "swarmauri.pipelines.Pipeline": "swarmauri_standard.pipelines.Pipeline",
        "swarmauri.prompts.Prompt": "swarmauri_standard.prompts.Prompt",
        "swarmauri.prompts.PromptGenerator": "swarmauri_standard.prompts.PromptGenerator",
        "swarmauri.prompts.PromptMatrix": "swarmauri_standard.prompts.PromptMatrix",
        "swarmauri.prompt_templates.PromptTemplate": "swarmauri_standard.prompt_templates.PromptTemplate",
        "swarmauri.schema_converters.AnthropicSchemaConverter": "swarmauri_standard.schema_converters.AnthropicSchemaConverter",
        "swarmauri.schema_converters.CohereSchemaConverter": "swarmauri_standard.schema_converters.CohereSchemaConverter",
        "swarmauri.schema_converters.GeminiSchemaConverter": "swarmauri_standard.schema_converters.GeminiSchemaConverter",
        "swarmauri.schema_converters.GroqSchemaConverter": "swarmauri_standard.schema_converters.GroqSchemaConverter",
        "swarmauri.schema_converters.MistralSchemaConverter": "swarmauri_standard.schema_converters.MistralSchemaConverter",
        "swarmauri.schema_converters.OpenAISchemaConverter": "swarmauri_standard.schema_converters.OpenAISchemaConverter",
        "swarmauri.schema_converters.ShuttleAISchemaConverter": "swarmauri_standard.schema_converters.ShuttleAISchemaConverter",
        "swarmauri.service_registries.ServiceRegistry": "swarmauri_standard.service_registries.ServiceRegistry",
        "swarmauri.state.DictState": "swarmauri_standard.state.DictState",
        "swarmauri.swarms.Swarm": "swarmauri_standard.swarms.Swarm",
        "swarmauri.task_mgmt_strategies.RoundRobinStrategy": "swarmauri_standard.task_mgmt_strategies.RoundRobinStrategy",
        "swarmauri.toolkits.AccessibilityToolkit": "swarmauri_standard.toolkits.AccessibilityToolkit",
        "swarmauri.toolkits.Toolkit": "swarmauri_standard.toolkits.Toolkit",
        "swarmauri.tools.AdditionTool": "swarmauri_standard.tools.AdditionTool",
        "swarmauri.tools.AutomatedReadabilityIndexTool": "swarmauri_standard.tools.AutomatedReadabilityIndexTool",
        "swarmauri.tools.CalculatorTool": "swarmauri_standard.tools.CalculatorTool",
        "swarmauri.tools.CodeExtractorTool": "swarmauri_standard.tools.CodeExtractorTool",
        "swarmauri.tools.CodeInterpreterTool": "swarmauri_standard.tools.CodeInterpreterTool",
        "swarmauri.tools.ColemanLiauIndexTool": "swarmauri_standard.tools.ColemanLiauIndexTool",
        "swarmauri.tools.FleschKincaidTool": "swarmauri_standard.tools.FleschKincaidTool",
        "swarmauri.tools.FleschReadingEaseTool": "swarmauri_standard.tools.FleschReadingEaseTool",
        "swarmauri.tools.GunningFogTool": "swarmauri_standard.tools.GunningFogTool",
        "swarmauri.tools.ImportMemoryModuleTool": "swarmauri_standard.tools.ImportMemoryModuleTool",
        "swarmauri.tools.JSONRequestsTool": "swarmauri_standard.tools.JSONRequestsTool",
        # "swarmauri.tools.MatplotlibCsvTool": "swarmauri_standard.tools.MatplotlibCsvTool",
        # "swarmauri.tools.MatplotlibTool": "swarmauri_standard.tools.MatplotlibTool",
        "swarmauri.tools.Parameter": "swarmauri_standard.tools.Parameter",
        "swarmauri.tools.RequestsTool": "swarmauri_standard.tools.RequestsTool",
        "swarmauri.tools.SentenceComplexityTool": "swarmauri_standard.tools.SentenceComplexityTool",
        "swarmauri.tools.TemperatureConverterTool": "swarmauri_standard.tools.TemperatureConverterTool",
        "swarmauri.tools.TestTool": "swarmauri_standard.tools.TestTool",
        "swarmauri.tools.WeatherTool": "swarmauri_standard.tools.WeatherTool",
        "swarmauri.tracing.CallableTracer": "swarmauri_standard.tracing.CallableTracer",
        "swarmauri.tracing.ChainTracer": "swarmauri_standard.tracing.ChainTracer",
        "swarmauri.tracing.SimpleTraceContext": "swarmauri_standard.tracing.SimpleTraceContext",
        "swarmauri.tracing.SimpleTracer": "swarmauri_standard.tracing.SimpleTracer",
        "swarmauri.tracing.TracedVariable": "swarmauri_standard.tracing.TracedVariable",
        "swarmauri.tracing.VariableTracer": "swarmauri_standard.tracing.VariableTracer",
        "swarmauri.transports.PubSubTransport": "swarmauri_standard.transports.PubSubTransport",
        ###
        # Utils
        ##
        "swarmauri.utils.LazyLoader": "swarmauri_standard.utils.LazyLoader",
        "swarmauri.utils._get_subclasses": "swarmauri_standard.utils._get_subclasses",
        "swarmauri.utils._lazy_import": "swarmauri_standard.utils._lazy_import",
        "swarmauri.utils.apply_metaclass": "swarmauri_standard.utils.apply_metaclass",
        "swarmauri.utils.base64_encoder": "swarmauri_standard.utils.base64_encoder",
        "swarmauri.utils.base64_to_file_path": "swarmauri_standard.utils.base64_to_file_path",
        "swarmauri.utils.base64_to_img_url": "swarmauri_standard.utils.base64_to_img_url",
        "swarmauri.utils.base64_to_in_memory_img": "swarmauri_standard.utils.base64_to_in_memory_img",
        "swarmauri.utils.decorate": "swarmauri_standard.utils.decorate",
        "swarmauri.utils.duration_manager": "swarmauri_standard.utils.duration_manager",
        "swarmauri.utils.file_path_to_base64": "swarmauri_standard.utils.file_path_to_base64",
        "swarmauri.utils.file_path_to_img_url": "swarmauri_standard.utils.file_path_to_img_url",
        "swarmauri.utils.file_path_to_in_memory_img": "swarmauri_standard.utils.file_path_to_in_memory_img",
        "swarmauri.utils.get_class_hash": "swarmauri_standard.utils.get_class_hash",
        "swarmauri.utils.img_url_to_base64": "swarmauri_standard.utils.img_url_to_base64",
        "swarmauri.utils.img_url_to_file_path": "swarmauri_standard.utils.img_url_to_file_path",
        "swarmauri.utils.img_url_to_in_memory_img": "swarmauri_standard.utils.img_url_to_in_memory_img",
        "swarmauri.utils.in_memory_img_to_base64": "swarmauri_standard.utils.in_memory_img_to_base64",
        "swarmauri.utils.in_memory_img_to_file_path": "swarmauri_standard.utils.in_memory_img_to_file_path",
        "swarmauri.utils.in_memory_img_to_img_url": "swarmauri_standard.utils.in_memory_img_to_img_url",
        "swarmauri.utils.json_validator": "swarmauri_standard.utils.json_validator",
        "swarmauri.utils.load_documents_from_folder": "swarmauri_standard.utils.load_documents_from_folder",
        "swarmauri.utils.load_documents_from_json": "swarmauri_standard.utils.load_documents_from_json",
        "swarmauri.utils.memoize": "swarmauri_standard.utils.memoize",
        "swarmauri.utils.method_signature_extractor_decorator": "swarmauri_standard.utils.method_signature_extractor_decorator",
        "swarmauri.utils.print_notebook_metadata": "swarmauri_standard.utils.print_notebook_metadata",
        "swarmauri.utils.retry_decorator": "swarmauri_standard.utils.retry_decorator",
        "swarmauri.utils.sql_log": "swarmauri_standard.utils.sql_log",
        "swarmauri.utils.timeout_wrapper": "swarmauri_standard.utils.timeout_wrapper",
        ###
        # Vector Stores
        ###
        "swarmauri.vector_stores.SqliteVectorStore": "swarmauri_standard.vector_stores.SqliteVectorStore",
        "swarmauri.vector_stores.TfidfVectorStore": "swarmauri_standard.vector_stores.TfidfVectorStore",
        "swarmauri.vectors.Vector": "swarmauri_standard.vectors.Vector",
        # extra
        "swarmauri.vector_stores.Doc2vecVectorStore": "swarmauri_vectorstore_doc2vec.Doc2vecVectorStore",
        "swarmauri.embeddings.Doc2VecEmbedding": "swarmauri_embedding_doc2vec.Doc2VecEmbedding",
        "swarmauri.tools.MatplotlibCsvTool": "swarmauri_tool_matplotlib.MatplotlibCsvTool",
        "swarmauri.tools.MatplotlibTool": "swarmauri_tool_matplotlib.MatplotlibTool",
        "swarmauri.parsers.KeywordExtractorParser": "swarmauri_parser_keywordextractor.KeywordExtractorParser",
        "swarmauri.embeddings.NmfEmbedding": "swarmauri_embedding_nmf.NmfEmbedding",
        "swarmauri.parsers.BeautifulSoupElementParser": "swarmauri_parser_beautifulsoupelement.BeautifulSoupElementParser",
        "swarmauri.distances.MinkowskiDistance": "swarmauri_distance_minkowski.MinkowskiDistance",
        "swarmauri.loggers.Logger": "swarmauri_standard.loggers.Logger",
        "swarmauri.logger_handlers.StreamHandler": "swarmauri_standard.logger_handlers.StreamHandler",
        "swarmauri.logger_formatters.LoggerFormatter": "swarmauri_standard.logger_formatters.LoggerFormatter",
        "swarmauri.middlewares.AuthMiddleware": "swarmauri_middleware_auth.AuthMiddleware",
        "swarmauri.middlewares.BulkheadMiddleware": "swarmauri_middleware_bulkhead.BulkheadMiddleware",
        "swarmauri.middlewares.CacheControlMiddleware": "swarmauri_middleware_cachecontrol.CacheControlMiddleware",
        "swarmauri.middlewares.CustomCORSMiddleware": "swarmauri_middleware_cors.CustomCORSMiddleware",
        "swarmauri.middlewares.ExceptionHandlingMiddleware": "swarmauri_middleware_exceptionhadling.ExceptionHandlingMiddleware",
        "swarmauri.middlewares.GzipCompressionMiddleware": "swarmauri_middleware_gzipcompression.GzipCompressionMiddleware",
        "swarmauri.middlewares.LlamaGuardMiddleware": "swarmauri_middleware_llamaguard.LlamaGuardMiddleware",
        "swarmauri.middlewares.LoggingMiddleware": "swarmauri_middleware_logging.LoggingMiddleware",
        "swarmauri.middlewares.RateLimitMiddleware": "swarmauri_middleware_ratelimit.RateLimitMiddleware",
        "swarmauri.middlewares.SecurityHeadersMiddleware": "swarmauri_middleware_sercurityheaders.SecurityHeadersMiddleware",
        "swarmauri.middlewares.SessionMiddleware": "swarmauri_middleware_session.SessionMiddleware",
        "swarmauri.middlewares.TimerMiddleware": "swarmauri_middleware_time.TimerMiddleware",
        "swarmauri.rate_limits.TokenBucketRateLimit": "swarmauri_standard.rate_limits.TokenBucketRateLimit",
        "swarmauri.crypto.ParamikoCrypto": "swarmauri_crypto_paramiko.ParamikoCrypto",
        "swarmauri.crypto.PGPCrypto": "swarmauri_crypto_pgp.PGPCrypto",
        "swarmauri.mre_cryptos.ShamirMreCrypto": "swarmauri_mre_crypto_shamir.ShamirMreCrypto",
        "swarmauri.mre_crypto.KeyringMreCrypto": "swarmauri_mre_crypto_keyring.KeyringMreCrypto",
        "swarmauri.mre_crypto.AgeMreCrypto": "swarmauri_mre_crypto_age.AgeMreCrypto",
        "swarmauri.mre_crypto.PGPSealMreCrypto": "swarmauri_mre_crypto_pgp.PGPSealMreCrypto",
        "swarmauri.secret.AutoGpgSecretDrive": "swarmauri_secret_autogpg.AutoGpgSecretDrive",
    }
    _KNOWN_GROUPS_CACHE: set[str] | None = None
    SECOND_CLASS_REGISTRY: Dict[str, str] = {}
    THIRD_CLASS_REGISTRY: Dict[str, str] = {}

    @classmethod
    def total_registry(cls) -> Dict[str, str]:
        """
        Property: total_registry

        Aggregates all plugin registrations from first, second, and third-class registries.
        Provides a comprehensive mapping of resource paths to their corresponding external module paths.

        :return: A dictionary containing all registered plugins across all classifications.
        """
        aggregated_registry = {
            **cls.FIRST_CLASS_REGISTRY,
            **cls.SECOND_CLASS_REGISTRY,
            **cls.THIRD_CLASS_REGISTRY,
        }
        logger.debug("Aggregated total registry from all class registries.")
        return aggregated_registry

    @classmethod
    def add_to_registry(
        cls, class_type: str, resource_path: str, module_path: str
    ) -> None:
        """
        Add an entry to the appropriate registry.

        :param class_type: Type of the plugin ('first', 'second', 'third').
        :param resource_path: The resource path (e.g., 'swarmauri.llms.OpenAIModel').
        :param module_path: The external module path it maps to (e.g., 'external_repo.OpenAIModel').
        :raises ValueError: If class_type is invalid.
        """
        registry_map = {
            "first": cls.FIRST_CLASS_REGISTRY,
            "second": cls.SECOND_CLASS_REGISTRY,
            "third": cls.THIRD_CLASS_REGISTRY,
        }

        if class_type not in registry_map:
            logger.error(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )
            raise ValueError(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )

        registry = registry_map[class_type]

        if resource_path in registry:
            logger.debug(
                f"Resource path '{resource_path}' already exists in the {class_type}-class registry. Skipping registration."
            )
            return

        # Add to the specific registry
        registry[resource_path] = module_path
        cls._KNOWN_GROUPS_CACHE = None
        logger.info(
            f"Added to {class_type}-class registry: {resource_path} -> {module_path}"
        )

    @classmethod
    def remove_from_registry(cls, class_type: str, resource_path: str) -> None:
        """
        Remove an entry from the appropriate registry.

        :param class_type: Type of the plugin ('first', 'second', 'third').
        :param resource_path: The resource path to remove.
        :raises ValueError: If class_type is invalid.
        :raises KeyError: If resource_path does not exist in the specified registry.
        """
        registry_map = {
            "first": cls.FIRST_CLASS_REGISTRY,
            "second": cls.SECOND_CLASS_REGISTRY,
            "third": cls.THIRD_CLASS_REGISTRY,
        }

        if class_type not in registry_map:
            logger.error(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )
            raise ValueError(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )

        registry = registry_map[class_type]

        if resource_path not in registry:
            logger.error(
                f"Resource path '{resource_path}' does not exist in the {class_type}-class registry."
            )
            raise KeyError(
                f"Resource path '{resource_path}' does not exist in the {class_type}-class registry."
            )

        # Remove from the specific registry
        del registry[resource_path]
        cls._KNOWN_GROUPS_CACHE = None
        logger.info(f"Removed from {class_type}-class registry: {resource_path}")

    @classmethod
    def list_registry(cls, class_type: Optional[str] = None) -> Dict[str, str]:
        """
        List all entries in a specific registry or the total registry.

        :param class_type: Type of the registry to list ('first', 'second', 'third').
                           If None, lists the total registry.
        :return: A dictionary of resource_path to module_path.
        :raises ValueError: If class_type is invalid.
        """
        if class_type is None:
            logger.debug("Listing TOTAL registry.")
            return cls.total_registry()

        registry_map = {
            "first": cls.FIRST_CLASS_REGISTRY,
            "second": cls.SECOND_CLASS_REGISTRY,
            "third": cls.THIRD_CLASS_REGISTRY,
        }

        if class_type not in registry_map:
            logger.error(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )
            raise ValueError(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )

        logger.debug(f"Listing {class_type}-class registry.")
        return dict(registry_map[class_type])

    @classmethod
    def get_external_module_path(cls, resource_path: str) -> Optional[str]:
        """
        Get the external module path for a given resource path.

        :param resource_path: Full resource path (e.g., 'swarmauri.llms.OpenAIModel').
        :return: External module path or None if not found.
        """
        module_path = cls.total_registry().get(resource_path)
        if module_path:
            logger.debug(
                f"Retrieved module path '{module_path}' for resource path '{resource_path}'."
            )
        else:
            logger.debug(
                f"Resource path '{resource_path}' not found in TOTAL registry."
            )
        return module_path

    @classmethod
    def resource_exists(cls, resource_path: str) -> bool:
        """Check if a resource path is registered in any registry."""
        return resource_path in cls.total_registry()

    @classmethod
    def known_groups(cls) -> set[str]:
        """Return the set of entry point groups known to the registry."""
        if cls._KNOWN_GROUPS_CACHE is None:
            groups: set[str] = set()
            for registry in (
                cls.FIRST_CLASS_REGISTRY,
                cls.SECOND_CLASS_REGISTRY,
                cls.THIRD_CLASS_REGISTRY,
            ):
                for resource_path in registry.keys():
                    groups.add(".".join(resource_path.split(".")[:-1]))
            cls._KNOWN_GROUPS_CACHE = groups
        return cls._KNOWN_GROUPS_CACHE

    @classmethod
    def update_entry(
        cls, class_type: str, resource_path: str, new_module_path: str
    ) -> None:
        """
        Update an existing entry in the appropriate registry.

        :param class_type: Type of the plugin ('first', 'second', 'third').
        :param resource_path: The resource path to update.
        :param new_module_path: The new external module path to associate with the resource path.
        :raises ValueError: If class_type is invalid.
        :raises KeyError: If resource_path does not exist in the specified registry.
        """
        registry_map = {
            "first": cls.FIRST_CLASS_REGISTRY,
            "second": cls.SECOND_CLASS_REGISTRY,
            "third": cls.THIRD_CLASS_REGISTRY,
        }

        if class_type not in registry_map:
            logger.error(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )
            raise ValueError(
                f"Invalid class type '{class_type}'. Must be 'first', 'second', or 'third'."
            )

        registry = registry_map[class_type]

        if resource_path not in registry:
            logger.error(
                f"Resource path '{resource_path}' does not exist in the {class_type}-class registry."
            )
            raise KeyError(
                f"Resource path '{resource_path}' does not exist in the {class_type}-class registry."
            )

        old_module_path = registry[resource_path]
        registry[resource_path] = new_module_path
        logger.info(
            f"Updated {class_type}-class registry entry: {resource_path} -> {new_module_path} (was: {old_module_path})"
        )

    @classmethod
    def delete_entry(cls, class_type: str, resource_path: str) -> None:
        """
        Delete an entry from the appropriate registry.

        :param class_type: Type of the plugin ('first', 'second', 'third').
        :param resource_path: The resource path to delete.
        :raises ValueError: If class_type is invalid.
        :raises KeyError: If resource_path does not exist in the specified registry.
        """
        cls.remove_from_registry(class_type, resource_path)

    @classmethod
    def list_all_registries(cls) -> Dict[str, Dict[str, str]]:
        """
        Lists all registries: first, second, third, and total.

        :return: A dictionary containing all registries.
        """
        logger.debug("Listing all registries.")
        return {
            "first": cls.list_registry("first"),
            "second": cls.list_registry("second"),
            "third": cls.list_registry("third"),
            "total": cls.total_registry(),
        }

    @classmethod
    def is_first_class(cls, entry_point: EntryPoint) -> bool:
        """
        Determines if the given plugin is a first-class citizen.

        :param entry_point: The entry point of the plugin.
        :return: True if first-class, False otherwise.
        """
        resource_path = f"{entry_point.group}.{entry_point.name}"
        is_first = resource_path in cls.FIRST_CLASS_REGISTRY
        logger.debug(
            f"Plugin '{entry_point.name}' is {'first-class' if is_first else 'not first-class'}."
        )
        return is_first

    @classmethod
    def is_second_class(cls, entry_point: EntryPoint) -> bool:
        """
        Determines if the given plugin is a second-class citizen.

        :param entry_point: The entry point of the plugin.
        :return: True if second-class, False otherwise.
        """
        resource_path = f"{entry_point.group}.{entry_point.name}"
        is_second = resource_path in cls.SECOND_CLASS_REGISTRY
        logger.debug(
            f"Plugin '{entry_point.name}' is {'second-class' if is_second else 'not second-class'}."
        )
        return is_second

    @classmethod
    def register_first_class_plugin(cls, entry_point: EntryPoint, module_path: str):
        """
        Registers a first-class plugin.

        :param entry_point: The entry point of the plugin.
        :param module_path: The external module path of the plugin.
        """
        resource_path = f"{entry_point.group}.{entry_point.name}"
        cls.FIRST_CLASS_REGISTRY[resource_path] = module_path
        logger.info(f"Registered first-class plugin: {resource_path} -> {module_path}")

    @classmethod
    def register_second_class_plugin(cls, entry_point: EntryPoint, module_path: str):
        """
        Registers a second-class plugin.

        :param entry_point: The entry point of the plugin.
        :param module_path: The external module path of the plugin.
        """
        resource_path = f"{entry_point.group}.{entry_point.name}"
        cls.SECOND_CLASS_REGISTRY[resource_path] = module_path
        logger.info(f"Registered second-class plugin: {resource_path} -> {module_path}")

    @classmethod
    def register_third_class_plugin(cls, entry_point: EntryPoint, module_path: str):
        """
        Registers a third-class plugin.

        :param entry_point: The entry point of the plugin.
        :param module_path: The external module path of the plugin.
        """
        resource_path = f"{entry_point.group}.{entry_point.name}"
        cls.THIRD_CLASS_REGISTRY[resource_path] = module_path
        logger.info(f"Registered third-class plugin: {resource_path} -> {module_path}")
