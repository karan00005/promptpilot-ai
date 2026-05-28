import time
import httpx
import logging
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from services.auth_service import get_current_user
from services.token_counter import count_tokens
from services.database import log_compression
from services.compression.rule_based import compress_rule_based
from services.compression.heuristic import compress_heuristic
from services.compression.summarizer import compress_summarizer
from services.compression.llmlingua_compressor import compress_llmlingua
from services.compression.semantic_cache import retrieve_relevant_chunks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["OpenAI Proxy Gateway"])

# =====================================================================
# OPENAI-COMPATIBLE CHAT COMPLETIONS PROXY GATEWAY
# =====================================================================

@router.post("/chat/completions")
async def chat_completions_proxy_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    OpenAI-Compatible Chat Completions Gateway Proxy.
    Intercepts standard payloads, performs dynamic 4-Layer prompt compression and RAG-based context
    injection, then forwards optimized payloads to OpenAI API and streams back results seamlessly!
    
    Change your client API baseURL to: http://localhost:8000/api/v1 (or your production Railway link)
    """
    # 1. Parse JSON payload
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    messages = body.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="The 'messages' array cannot be empty.")

    # 2. Extract final prompt
    last_message = messages[-1]
    original_prompt = last_message.get("content", "").strip()
    if not original_prompt:
        raise HTTPException(status_code=400, detail="The content of the last message cannot be empty.")

    # 3. Read pipeline config from request headers (or query params)
    level = int(request.headers.get("X-PromptPilot-Level", 2))
    context_title = request.headers.get("X-PromptPilot-Context-Title", "").strip()
    target_model = body.get("model", "gpt-4o")
    stream = body.get("stream", False)

    # 4. Perform dynamic Semantic RAG Context caching
    assembled_prompt = original_prompt
    retrieved_count = 0
    if context_title:
        user_id = current_user["id"]
        matched_chunks = retrieve_relevant_chunks(user_id, context_title, original_prompt, top_k=3)
        retrieved_count = len(matched_chunks)
        if matched_chunks:
            context_block = f'[Context retrieved from "{context_title}"]:\n' + "\n\n".join(matched_chunks)
            assembled_prompt = f"{context_block}\n\n[Instruction]:\n{original_prompt}"

    # 5. Apply hybrid 3-Layer compression pipeline
    orig_tokens = count_tokens(assembled_prompt, target_model)
    
    # Layer 1: Rule-based Conversational pruning (always applied)
    compressed_text = compress_rule_based(assembled_prompt)

    # Layer 2: Heuristic sentence selection (Level >= 2)
    if level >= 2:
        compressed_text = compress_heuristic(compressed_text, preserve_ratio=0.75)

    # Layer 3: Advanced AI Summarization/BART (Level >= 3)
    if level >= 3:
        llm_compressed = compress_llmlingua(compressed_text, target_rate=0.5)
        if llm_compressed == compressed_text and orig_tokens > 500:
            compressed_text = compress_summarizer(compressed_text)
        else:
            compressed_text = llm_compressed

    comp_tokens = count_tokens(compressed_text, target_model)
    savings_pct = round(((orig_tokens - comp_tokens) / max(1, orig_tokens)) * 100, 2)

    # Update messages object with optimized prompt
    body["messages"][-1]["content"] = compressed_text

    # Log token savings in SQLite DB
    log_compression(
        user_id=current_user["id"],
        original_tokens=orig_tokens,
        compressed_tokens=comp_tokens,
        model=target_model,
        savings_percent=max(0.0, savings_pct)
    )

    # 6. Retrieve OpenAI API key from environment variables or custom headers
    openai_api_key = request.headers.get("X-PromptPilot-OpenAI-Key") or request.headers.get("Openai-Key")
    if not openai_api_key:
        import os
        openai_api_key = os.getenv("OPENAI_API_KEY")

    # If no OpenAI Key is available, return optimized payload immediately as fallback
    if not openai_api_key:
        logger.info("No OpenAI API key found. Returning optimized prompt payload as offline response.")
        return {
            "success": True,
            "info": "No OpenAI Key found. Prompt compressed and returned locally.",
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "savings_percent": savings_pct,
            "retrieved_context_chunks": retrieved_count,
            "optimized_payload": body
        }

    # 7. Forward optimized request payload to real OpenAI API
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    async def stream_generator():
        # Handle streaming response seamlessly chunk-by-chunk
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", "https://api.openai.com/v1/chat/completions", json=body, headers=headers) as resp:
                if resp.status_code != 200:
                    err_msg = await resp.aread()
                    logger.error(f"OpenAI API returned error: {err_msg.decode()}")
                    yield f"data: {{\"error\": \"OpenAI Gateway failed: {err_msg.decode()}\"}}\n\n"
                    return
                
                async for chunk in resp.aiter_bytes():
                    yield chunk

    # Return stream or non-stream JSON
    if stream:
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
