from google.adk.agents.llm_agent import Agent

from ..callbacks import guardrail_and_log_tool_call
from ..config import MODEL_NAME
from ..tools import get_learning_card, get_learning_progress

concept_tutor = Agent(
    model=MODEL_NAME,
    name="concept_tutor",
    description=(
        "Teaches the concepts agents, tools, delegation, session state, callbacks, "
        "and evaluation using learning cards."
    ),
    instruction=(
        "You are the ADK concept specialist. For questions asking to explain or "
        "teach an ADK topic, call get_learning_card with one supported topic. "
        "Use get_learning_progress when asked what the learner has studied. "
        "Explain the tool result in beginner-friendly language and do not invent "
        "unsupported topics. Supported topics: agents, tools, delegation, "
        "session state, callbacks, evaluation."
    ),
    tools=[get_learning_card, get_learning_progress],
    before_tool_callback=guardrail_and_log_tool_call,
)
