import logging
from .compression.summarizer import fallback_summarize_paragraph

logger = logging.getLogger(__name__)

def compress_conversation(messages: list[dict]) -> dict:
    """
    Compresses a multi-turn conversation history list of messages.
    Keeps the first message (system instructions) and the last 2 messages intact.
    Summarizes all intermediate messages to reduce token costs in long chat sessions.
    """
    if not messages or len(messages) <= 4:
        # Too short to compress, return as is
        return {
            "compressed": False,
            "original_message_count": len(messages),
            "compressed_message_count": len(messages),
            "messages": messages
        }
        
    original_count = len(messages)
    
    # 1. Separate system prompt (if first message is system)
    has_system = messages[0].get("role") == "system"
    system_msg = messages[0] if has_system else None
    
    # Starting index of intermediate messages
    start_idx = 1 if has_system else 0
    # Ending index of intermediate messages (keep last 2 intact)
    end_idx = len(messages) - 2
    
    intermediate_msgs = messages[start_idx:end_idx]
    intact_tail_msgs = messages[end_idx:]
    
    if len(intermediate_msgs) <= 2:
        # Not enough intermediate messages to summarize productively
        return {
            "compressed": False,
            "original_message_count": len(messages),
            "compressed_message_count": len(messages),
            "messages": messages
        }
        
    # 2. Compile intermediate history into a single narrative text
    history_lines = []
    for msg in intermediate_msgs:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "").strip()
        if content:
            history_lines.append(f"{role}: {content}")
            
    history_text = "\n\n".join(history_lines)
    
    # 3. Summarize intermediate history text
    logger.info(f"Summarizing conversation history chunk of size: {len(history_text)} chars")
    # Using our modular context fallback/summarization logic
    summary_text = fallback_summarize_paragraph(history_text)
    
    # 4. Construct a unified System context summary message
    summary_message = {
        "role": "system",
        "content": (
            "[SYSTEM NOTE: The following is a concise summary of the preceding chat history. "
            "Use this summary as reference context: "
            f"{summary_text}]"
        )
    }
    
    # 5. Reassemble the new message log array
    compressed_messages = []
    
    if system_msg:
        compressed_messages.append(system_msg)
        
    compressed_messages.append(summary_message)
    compressed_messages.extend(intact_tail_msgs)
    
    return {
        "compressed": True,
        "original_message_count": original_count,
        "compressed_message_count": len(compressed_messages),
        "messages": compressed_messages
    }
