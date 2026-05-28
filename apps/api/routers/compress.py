from fastapi import APIRouter, HTTPException, Depends
import time
from models.schemas import (
    CompressionRequest,
    CompressionResponse,
    TokenCountRequest,
    TokenCountResponse,
    HealthResponse,
    RouteRequest,
    RouteResponse,
    ChatMessage,
    ConversationRequest,
    ConversationResponse
)
from services.token_counter import count_tokens, estimate_cost
from services.compression.rule_based import compress_rule_based
from services.compression.heuristic import compress_heuristic
from services.compression.summarizer import compress_summarizer
from services.compression.llmlingua_compressor import compress_llmlingua
from services.compression.quality_evaluator import QualityEvaluator
from services.model_router import route_prompt
from services.rate_limiter import check_rate_limit
from services.conversation_manager import compress_conversation
from services.auth_service import get_current_user
from services.database import log_compression

router = APIRouter(prefix="/api/v1", tags=["Prompt Compression"])

@router.post("/compress", response_model=CompressionResponse)
async def compress_prompt_endpoint(
    req: CompressionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Compresses a prompt based on the specified level (1, 2, or 3).
    - Level 1: Rule-based (whitespace optimization + redundant phrase removal).
    - Level 2: Rule-based + Heuristic sentence TF-IDF scoring and selection.
    - Level 3: Rule-based + Heuristic + Local BART summarization for large context.
    
    Requires JWT authorization. Logs metrics automatically.
    """
    start_time = time.time()
    original_prompt = req.prompt.strip()
    if not original_prompt:
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty.")
        
    # Count original tokens
    orig_tokens = count_tokens(original_prompt, req.model)
    
    # Enforce plan rate limits and token sizes
    check_rate_limit(current_user["id"], current_user["plan"], orig_tokens)
    
    # Run Layer 1: Rule-based compression (always applied)
    compressed_text = compress_rule_based(original_prompt)
    
    # Run Layer 2: Heuristic TF-IDF sentence cleaning (if level is 2 or 3)
    if req.level >= 2:
        # We preserve a generous 75% of text structure
        compressed_text = compress_heuristic(compressed_text, preserve_ratio=0.75)
        
    # Run Layer 3: AI Intelligence Layer (LLMLingua model with BART fallback)
    if req.level >= 3:
        # 1. Attempt advanced LLMLingua compression
        llm_compressed = compress_llmlingua(compressed_text, target_rate=0.6)
        # 2. If LLMLingua returned original text (due to fallback/errors) and size is large, apply BART summarizer
        if llm_compressed == compressed_text and orig_tokens > 500:
            compressed_text = compress_summarizer(compressed_text)
        else:
            compressed_text = llm_compressed
            
    # Count compressed tokens
    comp_tokens = count_tokens(compressed_text, req.model)
    
    # Calculate savings
    if orig_tokens > 0:
        savings_pct = round(((orig_tokens - comp_tokens) / orig_tokens) * 100, 2)
    else:
        savings_pct = 0.0
        
    # Safeguard in case compression actually increased tokens (shouldn't happen, but just in case)
    if comp_tokens > orig_tokens:
        compressed_text = original_prompt
        comp_tokens = orig_tokens
        savings_pct = 0.0
        
    # Calculate processing latency in milliseconds
    latency_ms = (time.time() - start_time) * 1000
    
    # Run AI Quality Evaluator to measure semantic retention
    eval_res = QualityEvaluator.evaluate_quality(
        original=original_prompt,
        compressed=compressed_text,
        model=req.model,
        latency_ms=latency_ms
    )
        
    # Log compression metrics in database under authenticated user's ID
    log_compression(
        user_id=current_user["id"],
        original_tokens=orig_tokens,
        compressed_tokens=comp_tokens,
        model=req.model,
        savings_percent=max(0.0, savings_pct)
    )
        
    return CompressionResponse(
        original_prompt=original_prompt,
        compressed_prompt=compressed_text,
        original_tokens=orig_tokens,
        compressed_tokens=comp_tokens,
        savings_percent=max(0.0, savings_pct),
        quality_score=eval_res["quality_score"]
    )

@router.post("/count-tokens", response_model=TokenCountResponse)
async def count_tokens_endpoint(req: TokenCountRequest):
    """
    Counts the number of tokens in the given text and estimates input API cost.
    No auth required for quick token estimations.
    """
    text = req.text
    t_count = count_tokens(text, req.model)
    est_cost = estimate_cost(t_count, req.model)
    
    return TokenCountResponse(
        token_count=t_count,
        estimated_cost=est_cost
    )

@router.post("/route", response_model=RouteResponse)
async def route_prompt_endpoint(req: RouteRequest):
    """
    Intelligently routes a prompt payload to the most optimal and cost-effective model based on token weights and code constructs.
    """
    res = route_prompt(req.prompt, req.user_preference)
    return RouteResponse(
        original_preference=res["original_preference"],
        recommended_model=res["recommended_model"],
        reason=res["reason"],
        savings_factor=res["savings_factor"],
        token_count=res["token_count"]
    )

@router.post("/compress-conversation", response_model=ConversationResponse)
async def compress_conversation_endpoint(req: ConversationRequest):
    """
    Summarizes intermediate conversation log histories to save up to 80% tokens in active chat sessions.
    """
    # Convert list of ChatMessage pydantic objects to native dict lists
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in req.messages]
    res = compress_conversation(messages_dict)
    
    # Convert response dict lists back to ChatMessage pydantic list formats
    res_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in res["messages"]]
    
    return ConversationResponse(
        compressed=res["compressed"],
        original_message_count=res["original_message_count"],
        compressed_message_count=res["compressed_message_count"],
        messages=res_messages
    )

@router.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """
    Performs a standard API health status check.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )
