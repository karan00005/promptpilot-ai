from pydantic import BaseModel, Field

class CompressionRequest(BaseModel):
    prompt: str = Field(..., description="The original prompt text to compress")
    model: str = Field("gpt-4o", description="The LLM model targeted (e.g., gpt-4o, claude-3-5-sonnet, gemini-pro)")
    level: int = Field(2, ge=1, le=3, description="Compression level: 1 (Rule-based), 2 (Heuristic), 3 (AI Summarization)")

class CompressionResponse(BaseModel):
    original_prompt: str
    compressed_prompt: str
    original_tokens: int
    compressed_tokens: int
    savings_percent: float
    quality_score: float

class TokenCountRequest(BaseModel):
    text: str = Field(..., description="The text to count tokens for")
    model: str = Field("gpt-4o", description="The LLM model targeted")

class TokenCountResponse(BaseModel):
    token_count: int
    estimated_cost: float

class HealthResponse(BaseModel):
    status: str
    version: str

class RouteRequest(BaseModel):
    prompt: str = Field(..., description="The prompt text to analyze and route")
    user_preference: str = Field("gpt-4o", description="User's originally preferred model")

class RouteResponse(BaseModel):
    original_preference: str
    recommended_model: str
    reason: str
    savings_factor: str
    token_count: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ConversationRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="The conversation history messages")

class ConversationResponse(BaseModel):
    compressed: bool
    original_message_count: int
    compressed_message_count: int
    messages: list[ChatMessage]
