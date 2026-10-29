from google.adk.tools import BaseTool, ToolContext

from .tools import LEARNING_CARDS, normalize_topic

_TOPIC_TOOLS = {"get_learning_card", "start_quiz"}


def guardrail_and_log_tool_call(
    tool: BaseTool,
    args: dict[str, object],
    tool_context: ToolContext,
) -> dict[str, str] | None:
    """Log tool calls and block unsupported learning topics before execution."""
    calls = list(tool_context.state.get("tool_call_log", []))
    call = {"tool": tool.name}
    if "topic" in args:
        call["topic"] = normalize_topic(str(args["topic"]))
    calls.append(call)
    tool_context.state["tool_call_log"] = calls

    if tool.name in _TOPIC_TOOLS:
        topic = normalize_topic(str(args.get("topic", "")))
        if topic not in LEARNING_CARDS:
            return {
                "status": "unsupported_topic",
                "supported_topics": ", ".join(sorted(LEARNING_CARDS)),
            }
    return None
