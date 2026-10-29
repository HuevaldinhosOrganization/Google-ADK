from __future__ import annotations

from typing import Any

from google.adk.tools import ToolContext

LEARNING_CARDS = {
    "agents": {
        "concept": "An ADK agent combines a model, instructions, and optional tools.",
        "example": "A study coach can answer questions and call a quiz tool.",
    },
    "tools": {
        "concept": "ADK function tools let an agent call Python functions.",
        "example": "A study coach can retrieve a trusted concept card with a tool.",
    },
    "delegation": {
        "concept": (
            "A parent agent can delegate work to specialized sub-agents using "
            "their descriptions and instructions."
        ),
        "example": "A learning coach can hand quiz requests to a quiz specialist.",
    },
    "session state": {
        "concept": (
            "ADK session state lets tools and agents share data across turns in "
            "a session."
        ),
        "example": "A quiz tool can remember the active question until the next turn.",
    },
    "callbacks": {
        "concept": (
            "ADK callbacks let developers inspect or control execution around "
            "agent, model, and tool steps."
        ),
        "example": "A before-tool callback can reject unsupported tool arguments.",
    },
    "evaluation": {
        "concept": (
            "ADK evaluation compares agent conversations with expected responses "
            "and tool-use trajectories."
        ),
        "example": (
            "An eval case can check that the agent calls the expected tool and "
            "gives a suitable answer."
        ),
    },
}

QUIZ_QUESTIONS = {
    "agents": {
        "question": "Name one thing an ADK agent definition can include.",
        "expected_phrase": "model",
        "hint": "Think about what generates responses and what guides behavior.",
        "explanation": "An ADK agent has a model and instructions, and may also have tools.",
    },
    "tools": {
        "question": "What can an ADK function tool let an agent do?",
        "expected_phrase": "python function",
        "hint": "It connects the agent to executable application logic.",
        "explanation": "A function tool lets an agent call a Python function.",
    },
    "delegation": {
        "question": "How can a parent ADK agent hand a task to a specialist?",
        "expected_phrase": "sub-agent",
        "hint": "The specialist is attached to its parent in the agent hierarchy.",
        "explanation": "A parent can delegate to one of its sub-agents.",
    },
    "session state": {
        "question": "What ADK feature can keep an active quiz available across turns?",
        "expected_phrase": "session state",
        "hint": "It is a key-value store associated with a conversation session.",
        "explanation": "Session state can hold the quiz between turns.",
    },
    "callbacks": {
        "question": "Which callback runs before an ADK tool executes?",
        "expected_phrase": "before_tool_callback",
        "hint": "Its name describes when it runs relative to a tool.",
        "explanation": "The before_tool_callback can inspect or block a tool call.",
    },
    "evaluation": {
        "question": "Name an ADK metric that checks expected tool usage.",
        "expected_phrase": "tool_trajectory_avg_score",
        "hint": "The metric name includes the word trajectory.",
        "explanation": "tool_trajectory_avg_score measures tool-call trajectory matching.",
    },
}

MAX_QUIZ_ATTEMPTS = 2


def normalize_topic(topic: str) -> str:
    return " ".join(topic.strip().lower().replace("-", " ").split())


def get_learning_card(topic: str, tool_context: ToolContext) -> dict[str, Any]:
    """Return a learning card and record the topic in the current session."""
    normalized_topic = normalize_topic(topic)
    card = LEARNING_CARDS.get(normalized_topic)
    if card is None:
        return {
            "status": "unsupported_topic",
            "supported_topics": ", ".join(sorted(LEARNING_CARDS)),
        }

    topics_studied = list(tool_context.state.get("topics_studied", []))
    if normalized_topic not in topics_studied:
        topics_studied.append(normalized_topic)
    tool_context.state["topics_studied"] = topics_studied
    return {"status": "success", "topic": normalized_topic, **card}


def start_quiz(topic: str, tool_context: ToolContext) -> dict[str, str]:
    """Start a one-question quiz and keep its answer in session state."""
    normalized_topic = normalize_topic(topic)
    quiz = QUIZ_QUESTIONS.get(normalized_topic)
    if quiz is None:
        return {
            "status": "unsupported_topic",
            "supported_topics": ", ".join(sorted(QUIZ_QUESTIONS)),
        }

    tool_context.state["current_quiz"] = {
        "topic": normalized_topic,
        **quiz,
        "attempts": 0,
    }
    return {
        "status": "quiz_started",
        "topic": normalized_topic,
        "question": quiz["question"],
    }


def submit_quiz_answer(answer: str, tool_context: ToolContext) -> dict[str, Any]:
    """Check an answer against the active quiz and update the session score."""
    quiz = tool_context.state.get("current_quiz")
    if not quiz:
        return {"status": "no_active_quiz"}

    attempts = int(quiz["attempts"]) + 1
    is_correct = quiz["expected_phrase"] in answer.strip().lower()
    tool_context.state["quiz_attempts"] = (
        int(tool_context.state.get("quiz_attempts", 0)) + 1
    )

    if is_correct:
        tool_context.state["quiz_score"] = (
            int(tool_context.state.get("quiz_score", 0)) + 1
        )
        tool_context.state["current_quiz"] = None
        return {
            "status": "correct",
            "explanation": quiz["explanation"],
        }

    if attempts >= MAX_QUIZ_ATTEMPTS:
        tool_context.state["current_quiz"] = None
        return {
            "status": "incorrect",
            "explanation": quiz["explanation"],
        }

    tool_context.state["current_quiz"] = {**quiz, "attempts": attempts}
    return {"status": "try_again", "hint": quiz["hint"]}


def get_learning_progress(tool_context: ToolContext) -> dict[str, Any]:
    """Summarize learning and quiz progress in the current session."""
    return {
        "topics_studied": list(tool_context.state.get("topics_studied", [])),
        "quiz_score": int(tool_context.state.get("quiz_score", 0)),
        "quiz_attempts": int(tool_context.state.get("quiz_attempts", 0)),
        "active_quiz": bool(tool_context.state.get("current_quiz")),
    }
