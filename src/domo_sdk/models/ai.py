"""AI Services models — based on Domo AI Services OpenAPI spec."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from domo_sdk.models.base import DomoModel

# ============================================================================
# Supporting Types
# ============================================================================


class OutputStyle(str, Enum):
    """Output style for text generation."""

    FORMAL = "FORMAL"
    INFORMAL = "INFORMAL"
    TECHNICAL = "TECHNICAL"
    CREATIVE = "CREATIVE"


class OutputWordLength(str, Enum):
    """Output word length for summarization."""

    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"


class SqlRequestOption(str, Enum):
    """SQL generation option."""

    DEFAULT = "DEFAULT"
    STRICT = "STRICT"


class StopReason(str, Enum):
    """Reason the model stopped generating."""

    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"
    TOOL_USE = "tool_use"


class DataSourceColumn(DomoModel):
    """Column definition for AI context."""

    name: str
    type: str
    description: str = ""


class DataSourceSchema(DomoModel):
    """Dataset schema provided as context to AI."""

    dataset_id: str = Field(alias="datasetId")
    name: str = ""
    description: str = ""
    columns: list[DataSourceColumn] = Field(default_factory=list)


class ReasoningConfig(DomoModel):
    """Reasoning/thinking configuration."""

    type: str = "enabled"
    budget_tokens: int = Field(default=1024, alias="budgetTokens")


# ============================================================================
# Message Content Types
# ============================================================================


class TextContent(DomoModel):
    """Text content block."""

    type: Literal["text"] = "text"
    text: str


class ImageContent(DomoModel):
    """Image content block."""

    type: Literal["image"] = "image"
    source: dict[str, Any]  # {"type": "base64", "media_type": "...", "data": "..."}


class DocumentContent(DomoModel):
    """Document content block."""

    type: Literal["document"] = "document"
    source: dict[str, Any]


class ToolUseContent(DomoModel):
    """Tool use content block (in responses)."""

    type: Literal["tool_use"] = "tool_use"
    id: str = ""
    name: str = ""
    input: dict[str, Any] = Field(default_factory=dict)


class ToolResultContent(DomoModel):
    """Tool result content block (in requests)."""

    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str = Field(alias="toolUseId")
    content: str | list[dict[str, Any]] = ""


class ReasoningContent(DomoModel):
    """Reasoning/thinking content block."""

    type: Literal["thinking"] = "thinking"
    thinking: str = ""


MessageContent = TextContent | ImageContent | DocumentContent | ToolUseContent | ToolResultContent | ReasoningContent


# ============================================================================
# Chat Message
# ============================================================================


class ChatMessage(DomoModel):
    """A message in a chat conversation."""

    role: str  # "user", "assistant", "system"
    content: str | list[dict[str, Any]]


# ============================================================================
# Tool Definitions
# ============================================================================


class ToolParameter(DomoModel):
    """Parameter for a tool definition."""

    type: str = "string"
    description: str = ""
    enum: list[str] | None = None


class ToolInputSchema(DomoModel):
    """JSON schema for tool input."""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class ToolDefinition(DomoModel):
    """Function/tool definition for tool-calling."""

    name: str
    description: str = ""
    input_schema: ToolInputSchema = Field(alias="inputSchema")


# ============================================================================
# Request Models
# ============================================================================


class TextGenerationRequest(DomoModel):
    """Request for text generation."""

    prompt: str
    input: str = ""
    output_style: OutputStyle | None = Field(default=None, alias="outputStyle")
    max_tokens: int = Field(default=1024, alias="maxTokens")


class TextSqlRequest(DomoModel):
    """Request for natural language to SQL."""

    input: str
    datasource_schemas: list[DataSourceSchema] = Field(default_factory=list, alias="datasourceSchemas")
    options: list[SqlRequestOption] = Field(default_factory=list)
    max_tokens: int = Field(default=1024, alias="maxTokens")


class TextSummarizeRequest(DomoModel):
    """Request for text summarization."""

    input: str
    output_style: OutputStyle | None = Field(default=None, alias="outputStyle")
    output_word_length: OutputWordLength | None = Field(default=None, alias="outputWordLength")
    max_tokens: int = Field(default=1024, alias="maxTokens")


class BeastModeRequest(DomoModel):
    """Request for Beast Mode formula generation."""

    input: str
    datasource_schemas: list[DataSourceSchema] = Field(default=[], alias="datasourceSchemas")
    max_tokens: int = Field(default=1024, alias="maxTokens")


class ChatRequest(DomoModel):
    """Request for multi-turn chat."""

    messages: list[ChatMessage]
    model: str = ""
    max_tokens: int = Field(default=1024, alias="maxTokens")
    system: str = ""
    temperature: float | None = None
    thinking: ReasoningConfig | None = None


class ToolCallRequest(DomoModel):
    """Request for tool-calling."""

    messages: list[ChatMessage]
    tools: list[ToolDefinition]
    model: str = ""
    max_tokens: int = Field(default=1024, alias="maxTokens")
    system: str = ""
    temperature: float | None = None


class SentimentRequest(DomoModel):
    """Request for sentiment analysis."""

    input: str
    max_tokens: int = Field(default=256, alias="maxTokens")


class TargetedSentimentRequest(DomoModel):
    """Request for targeted sentiment analysis."""

    input: str
    targets: list[str]
    max_tokens: int = Field(default=256, alias="maxTokens")


class ClassificationLabel(DomoModel):
    """Label for classification."""

    name: str
    description: str = ""


class ClassificationRequest(DomoModel):
    """Request for text classification."""

    input: str
    labels: list[ClassificationLabel]
    multi_label: bool = Field(default=False, alias="multiLabel")
    max_tokens: int = Field(default=256, alias="maxTokens")


class ExtractionRequest(DomoModel):
    """Request for structured extraction."""

    input: str
    output_schema: dict[str, Any] = Field(alias="outputSchema")
    max_tokens: int = Field(default=1024, alias="maxTokens")


class EmbeddingTextRequest(DomoModel):
    """Request for text embedding."""

    input: str | list[str]
    model: str = ""


class EmbeddingImageRequest(DomoModel):
    """Request for image embedding."""

    input: str  # base64 image data
    model: str = ""


class ImageTextRequest(DomoModel):
    """Request for image-to-text analysis."""

    prompt: str = ""
    image: str  # base64 image data
    max_tokens: int = Field(default=1024, alias="maxTokens")


# ============================================================================
# Response Models
# ============================================================================


class ModelProviderUsage(DomoModel):
    """Token usage information from the model provider."""

    input_tokens: int = Field(default=0, alias="inputTokens")
    output_tokens: int = Field(default=0, alias="outputTokens")
    total_tokens: int = Field(default=0, alias="totalTokens")


class TextAIResponse(DomoModel):
    """Response from text generation, SQL, summarize, beastmode endpoints."""

    output: str = ""
    stop_reason: StopReason | None = Field(default=None, alias="stopReason")
    usage: ModelProviderUsage | None = None


class MessagesAIResponse(DomoModel):
    """Response from chat and tool-calling endpoints."""

    id: str = ""
    content: list[dict[str, Any]] = Field(default_factory=list)
    model: str = ""
    role: str = "assistant"
    stop_reason: StopReason | None = Field(default=None, alias="stopReason")
    usage: ModelProviderUsage | None = None


class SentimentAIResponse(DomoModel):
    """Response from sentiment analysis."""

    sentiment: str = ""  # "POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"
    confidence: float = 0.0
    usage: ModelProviderUsage | None = None


class TargetedSentimentResult(DomoModel):
    """Sentiment result for a specific target."""

    target: str = ""
    sentiment: str = ""
    confidence: float = 0.0


class TargetedSentimentAIResponse(DomoModel):
    """Response from targeted sentiment analysis."""

    results: list[TargetedSentimentResult] = Field(default_factory=list)
    usage: ModelProviderUsage | None = None


class ClassificationResult(DomoModel):
    """Classification result."""

    label: str = ""
    confidence: float = 0.0


class ClassificationAIResponse(DomoModel):
    """Response from classification."""

    classifications: list[ClassificationResult] = Field(default_factory=list)
    usage: ModelProviderUsage | None = None


class ExtractionAIResponse(DomoModel):
    """Response from extraction."""

    output: dict[str, Any] = Field(default_factory=dict)
    usage: ModelProviderUsage | None = None


class EmbeddingAIResponse(DomoModel):
    """Response from embedding endpoints."""

    embeddings: list[list[float]] = Field(default_factory=list)
    model: str = ""
    usage: ModelProviderUsage | None = None
