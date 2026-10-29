from google.adk.agents.llm_agent import Agent

from ..callbacks import guardrail_and_log_tool_call
from ..config import MODEL_NAME
from ..tools import get_learning_progress, start_quiz, submit_quiz_answer

quiz_coach = Agent(
    model=MODEL_NAME,
    name="quiz_coach",
    description=(
        "Creates short quizzes about Google ADK concepts, checks answers, and "
        "tracks the learner's score."
    ),
    instruction=(
        "You are the ADK quiz specialist. When a learner asks for a quiz, call "
        "start_quiz for one supported topic and ask the returned question. For "
        "an answer to an active quiz, call submit_quiz_answer and explain the "
        "result. Use get_learning_progress when asked for quiz scores or overall "
        "progress. Do not claim a session is complete while a quiz is active."
    ),
    tools=[start_quiz, submit_quiz_answer, get_learning_progress],
    before_tool_callback=guardrail_and_log_tool_call,
)
