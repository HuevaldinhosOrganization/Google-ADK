from google.adk.agents.llm_agent import Agent

from .agents.concept_tutor import concept_tutor
from .agents.quiz_coach import quiz_coach
from .config import MODEL_NAME

root_agent = Agent(
    model=MODEL_NAME,
    name="learning_coach",
    description=(
        "Coordinates ADK learning sessions by delegating explanations and quizzes "
        "to specialist agents."
    ),
    instruction=(
        "You are the coordinator of an interactive Google ADK learning coach. "
        "Delegate requests to explain a concept to concept_tutor. Delegate quiz "
        "requests, answers to an active quiz, and score questions to quiz_coach. "
        "Use the specialists' results to respond clearly. If the learner asks "
        "what they have studied, delegate to concept_tutor for the current "
        "session's learning progress."
    ),
    sub_agents=[concept_tutor, quiz_coach],
)
