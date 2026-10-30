from pathlib import Path
from types import SimpleNamespace

from google.adk.agents.llm_agent import Agent
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager

from learning_coach.agent import root_agent
from learning_coach.agents.concept_tutor import concept_tutor
from learning_coach.agents.quiz_coach import quiz_coach
from learning_coach.callbacks import guardrail_and_log_tool_call
from learning_coach.config import MODEL_NAME
from learning_coach.tools import (
    get_learning_card,
    get_learning_progress,
    start_quiz,
    submit_quiz_answer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_root_agent_is_a_google_adk_agent():
    assert isinstance(root_agent, Agent)
    assert root_agent.name == "learning_coach"
    assert [agent.name for agent in root_agent.sub_agents] == [
        "concept_tutor",
        "quiz_coach",
    ]
    assert root_agent.model == MODEL_NAME
    assert all(agent.model == MODEL_NAME for agent in root_agent.sub_agents)
    assert concept_tutor.before_tool_callback is guardrail_and_log_tool_call
    assert quiz_coach.before_tool_callback is guardrail_and_log_tool_call


def test_learning_card_returns_supported_topic_content():
    context = SimpleNamespace(state={})
    card = get_learning_card("tools", context)

    assert card["status"] == "success"
    assert card["topic"] == "tools"
    assert "Python functions" in card["concept"]
    assert card["example"]
    assert context.state["topics_studied"] == ["tools"]


def test_tool_guardrail_blocks_unsupported_topic_and_logs_call():
    context = SimpleNamespace(state={})
    tool = SimpleNamespace(name="get_learning_card")

    result = guardrail_and_log_tool_call(
        tool,
        {"topic": "deployment"},
        context,
    )

    assert result == {
        "status": "unsupported_topic",
        "supported_topics": (
            "agents, callbacks, delegation, evaluation, session state, tools"
        ),
    }
    assert context.state["tool_call_log"] == [
        {"tool": "get_learning_card", "topic": "deployment"}
    ]


def test_quiz_uses_session_state_for_retries_and_scoring():
    context = SimpleNamespace(state={})

    question = start_quiz("tools", context)
    retry = submit_quiz_answer("A network request", context)
    result = submit_quiz_answer(
        "It lets an agent call a Python function.",
        context,
    )

    assert question["status"] == "quiz_started"
    assert "function tool" in question["question"]
    assert retry["status"] == "try_again"
    assert result["status"] == "correct"
    assert context.state["current_quiz"] is None
    assert context.state["quiz_score"] == 1
    assert context.state["quiz_attempts"] == 2
    assert get_learning_progress(context) == {
        "topics_studied": [],
        "quiz_score": 1,
        "quiz_attempts": 2,
        "active_quiz": False,
    }


def test_quiz_rejects_answer_without_active_quiz():
    result = submit_quiz_answer("model", SimpleNamespace(state={}))

    assert result == {"status": "no_active_quiz"}


def test_evaluation_files_match_google_adk_schemas():
    evalset_path = PROJECT_ROOT / "learning_coach" / (
        "learning_coach_basics.evalset.json"
    )
    config_path = PROJECT_ROOT / "eval" / "test_config.json"

    eval_set = EvalSet.model_validate_json(evalset_path.read_text(encoding="utf-8"))
    config = EvalConfig.model_validate_json(config_path.read_text(encoding="utf-8"))

    assert len(eval_set.eval_cases) == 3
    # FR-02: the ROUGE-1 `response_match_score` gate (which penalised correct
    # paraphrases) is replaced by the LLM-judged `final_response_match_v2`.
    assert set(config.criteria) == {
        "tool_trajectory_avg_score",
        "final_response_match_v2",
    }

    eval_manager = LocalEvalSetsManager(str(PROJECT_ROOT))
    assert eval_manager.list_eval_sets("learning_coach") == [
        "learning_coach_basics"
    ]
