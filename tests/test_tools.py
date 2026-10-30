from types import SimpleNamespace

import pytest

from learning_coach.callbacks import guardrail_and_log_tool_call
from learning_coach.tools import get_learning_card, normalize_topic


@pytest.mark.req("FR-04")
def test_normalize_topic_strips_adk_qualifier():
    # "ADK tools" is how the model naturally phrases the topic; it must resolve
    # to the "tools" card, not be rejected as an unsupported topic (FR-04).
    assert normalize_topic("ADK tools") == "tools"
    assert normalize_topic("adk session state") == "session state"
    # The bare qualifier is not a topic and must not collapse to "".
    assert normalize_topic("adk") == "adk"
    # Existing exact topics are unaffected.
    assert normalize_topic("tools") == "tools"


@pytest.mark.req("FR-04")
def test_get_learning_card_accepts_adk_tools():
    context = SimpleNamespace(state={})

    card = get_learning_card("ADK tools", context)

    assert card["status"] == "success"
    assert card["topic"] == "tools"


@pytest.mark.req("FR-04")
def test_guardrail_does_not_block_adk_tools():
    context = SimpleNamespace(state={})
    tool = SimpleNamespace(name="get_learning_card")

    result = guardrail_and_log_tool_call(tool, {"topic": "ADK tools"}, context)

    assert result is None  # not blocked
    assert context.state["tool_call_log"] == [
        {"tool": "get_learning_card", "topic": "tools"}
    ]
