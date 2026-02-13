import json
from typing import Any
from langchain_core.messages import ToolMessage, AIMessage, BaseMessage
from app.core.logger_config import logger

def try_parse(string: str) -> str | dict[str, Any]:
    try:
        return json.loads(string)
    except Exception:
        return string


def remove_incomplete_tool_calls(messages: list[BaseMessage]) -> list[BaseMessage]:
    """
    Remove AI messages with incomplete tool_calls and orphaned tool messages.
    Single-pass algorithm for better performance.
    """
    if not messages:
        return messages
    
    result = []
    valid_tool_call_ids = set()
    i = 0
    
    while i < len(messages):
        msg = messages[i]
        
        # Check if this is an AI message with tool_calls
        if isinstance(msg, AIMessage) and msg.tool_calls:
            
            # Get all tool_call_ids from this message
            expected_ids = {
                tc.get('id') if isinstance(tc, dict) else getattr(tc, 'id', None)
                for tc in msg.tool_calls
            }
            # Clean up None values if any
            expected_ids.discard(None)
            
            # Look ahead for tool responses
            j = i + 1
            found_ids = set()
            tool_responses = []
            while j < len(messages) and isinstance(messages[j], ToolMessage):
                if hasattr(messages[j], 'tool_call_id'):
                    found_ids.add(messages[j].tool_call_id)
                tool_responses.append(messages[j])
                j += 1
            
            # Only include if ALL tool calls have responses
            if expected_ids and expected_ids.issubset(found_ids):
                result.append(msg)
                result.extend(tool_responses)
                # Track these as valid for orphan detection
                valid_tool_call_ids.update(expected_ids)
            else:
                logger.warning(
                    f"Removing AI message with incomplete tool responses. "
                    f"Expected: {expected_ids}, Found: {found_ids}"
                )
            
            i = j
        elif isinstance(msg, ToolMessage):
            # This is an orphaned tool message (shouldn't happen after above logic, but just in case)
            if hasattr(msg, 'tool_call_id') and msg.tool_call_id in valid_tool_call_ids:
                result.append(msg)
            else:
                logger.warning(
                    f"Removing orphaned tool message: {getattr(msg, 'tool_call_id', 'unknown')}"
                )
            i += 1
        else:
            result.append(msg)
            i += 1
    
    return result
