# Google ADK Learning Lab

A hands-on Python project for learning what Google's official Agent Development Kit (ADK) can do. The exercise grows a single-agent demo into a stateful, multi-agent learning coach and evaluates its behavior with ADK's evaluation framework.

## Learning exercise and implemented features

The exercise is organized around these ADK capabilities:

1. **LLM agents and instructions** — expose a `root_agent` and use clear descriptions and instructions to guide behavior.
2. **Function tools and `ToolContext`** — define typed Python tools, access ADK's injected context, and read/write session state.
3. **Multi-agent delegation** — use a coordinator with focused sub-agents, an ADK concept tutor and quiz coach; let ADK transfer control to the appropriate specialist.
4. **Session state** — keep track of the current quiz and topics studied so the agent can continue a learning session instead of treating every turn as unrelated.
5. **Tool callbacks and guardrails** — inspect tool calls before execution, reject unsupported requests safely, and make the decision visible to the agent.
6. **Official ADK evaluation** — use an `.evalset.json` dataset and `test_config.json` to check both expected tool trajectories and reference-answer similarity.
7. **ADK developer tools** — run the agent with `adk run`, inspect conversations with `adk web`, and execute evaluations with `adk eval`.

The core capabilities above are implemented. The suggested extensions below are intentionally separate follow-up exercises. Code-level tests cover deterministic tool/state behavior and ADK schemas. Model-backed evaluation is a separate step, since it needs credentials and makes model calls.

## Requirements

- Python 3.11 or later
- A Google AI Studio API key for running the agent or model-backed evaluation
- Internet access for model calls
- The configured model is Gemini 3.1 Flash-Lite, selected as a lower-cost model for this learning agent.

The project installs `google-adk[eval]`, including the official ADK evaluation dependencies.

The shared model ID is in [learning_coach/config.py](./learning_coach/config.py), so the coordinator and both specialists stay on the same model. Flash-Lite is less capable than Gemini Flash for complex reasoning, but supports the function calling this exercise uses. Quotas are assigned per project and model, so switching models does not guarantee higher request limits.

## Installation

From the project root, create and activate a virtual environment, then install the project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Set up the Gemini API key. Copy the example file and replace the placeholder with your key:

```powershell
Copy-Item learning_coach\.env.example learning_coach\.env
```

The `.env` file is ignored by Git. Never commit API keys.

## Explore the agent

The repository follows ADK's agent-package convention: [learning_coach/](./learning_coach/) is the importable agent folder, [agent.py](./learning_coach/agent.py) exposes `root_agent`, and `__init__.py` makes the package discoverable by the ADK CLI. The coordinator, specialists, tools, and callbacks are separated into focused modules so you can follow the system without navigating a monolithic file.

Run the agent interactively:

```powershell
adk run learning_coach
```

Or launch the ADK development UI from the repository root:

```powershell
adk web --port 8000
```

Then open `http://localhost:8000` and select `learning_coach`. The development UI is for local development, not production deployment.

Try these prompts to explore delegation and session state:

- “Teach me what an ADK function tool is.”
- “Quiz me on tools, then tell me whether my answer is right.”
- “What topics have I studied so far?”
- “Can you teach me about a topic that is not supported?”

## ADK Web screenshots

These screenshots show the learning coach running in the ADK development UI. Start the UI with `adk web --port 8000` and select `learning_coach` to explore the same views.

### Agent conversation

![ADK Web chat showing an agent response and tool calls](assets/agent-response.png)

The chat shows the coordinator handing a question to `concept_tutor`, a `get_learning_card` call, and the specialist's final explanation.

### Agent hierarchy

![ADK Web agent hierarchy graph](assets/graph.png)

The graph shows `learning_coach` connected to its `concept_tutor` and `quiz_coach` sub-agents, along with their learning and quiz tools.

### Invocation and trace views

![ADK Web event and trace view with the invocation graph](assets/invocation-graph-view.png)

This view combines conversation events with trace timing and a compact graph highlighting the selected concept-tutor tool path.

![ADK Web trace details for a sub-agent invocation](assets/invoke-subagent-raw-json.png)

The trace details identify the `invoke_agent concept_tutor` span and show its agent attributes, parent span, and timing metadata.

![ADK Web trace timeline for coordinator and specialist calls](assets/traces-info.png)

The timeline breaks an invocation into coordinator model generation, `transfer_to_agent`, and specialist execution spans.

### Tool execution and raw event data

![ADK Web tool event with state changes and function response](assets/tool-usage.png)

The selected `get_learning_card` event shows its state delta (`tool_call_log` and `topics_studied`) and the function response returned to the agent.

![ADK Web raw event JSON](assets/raw-json.png)

The event details expose the underlying serialized assistant message, including its text content and finish reason.

### Session management

![ADK Web session selector and session actions](assets/select-session.png)

The session panel lists the current conversation and provides controls to import, view, export, or delete a session.

### Evaluation results

![ADK Web evaluation metrics and failed eval cases](assets/evals.png)

This example run shows three failed cases, the tool-trajectory and response-match scores, and the trace for a quiz request. The scores reflect that specific run and its selected thresholds; see [Run the official ADK evaluation](#run-the-official-adk-evaluation) for how to interpret them.

## Run the official ADK evaluation

The evaluation dataset in [learning_coach/learning_coach_basics.evalset.json](./learning_coach/learning_coach_basics.evalset.json) contains conversations with reference responses and expected tool calls. Its criteria are configured in [eval/test_config.json](./eval/test_config.json).

The eval set is stored in the `learning_coach` agent folder as [learning_coach_basics.evalset.json](./learning_coach/learning_coach_basics.evalset.json), which lets ADK Web discover it in the **Eval** tab. Run the same dataset with the official ADK CLI:

```powershell
adk eval learning_coach learning_coach/learning_coach_basics.evalset.json --config_file_path eval/test_config.json --print_detailed_results
```

ADK prints the detailed report in the terminal and automatically saves each run as a structured JSON file in `learning_coach/.adk/eval_history/`. This is ADK's native result format; the latest run is the `.evalset_result.json` file with the newest timestamp. The `.adk` folder is generated locally and excluded from Git. A non-zero exit code means one or more evaluation criteria failed; ADK still saves the result JSON for that run.

The CLI does not provide an option to choose a local output filename. Its `--eval_storage_uri` option is for storing evals in a Google Cloud Storage bucket (`gs://...`), not for writing to an arbitrary local path.

The run uses two ADK metrics:

- `tool_trajectory_avg_score` compares actual tool calls with the calls in the eval case. The current `EXACT` match type requires every call to match exactly, with no extras.
- `response_match_score` uses ROUGE-1 word overlap to compare the final response with the reference. It is not a semantic correctness check, so a correct answer worded differently can score poorly.

Model-backed evaluation requires the API key. It may incur model usage costs.

### What the saved result tells you

Each `.evalset_result.json` includes the expected and actual invocation data, final responses, metric scores and statuses, and per-invocation efficiency information. Use it to answer questions such as:

- Did the answer resemble the reference closely enough?
- Did the agent call the expected tool, with the expected arguments?
- How many tools and model calls did the invocation use?
- How many tokens did it consume, and how long did it take?

The ADK Web **Eval** view makes it easier to compare passing and failing cases; the **Trace** view can help inspect the agent and tool execution behind a run. These explain what happened, but do not by themselves establish that an answer is factually correct.

### Other ADK evaluation criteria to explore

The current [test configuration](./eval/test_config.json) enables two pass/fail criteria. ADK also supports the following built-in criteria. A criterion only provides useful evidence when the eval data contains what it needs; some also make additional LLM-judge calls.

| Criterion | What it evaluates | What the eval needs |
|---|---|---|
| `tool_trajectory_avg_score` | Whether actual tool calls match the expected tool-call trajectory. Supports `EXACT`, `IN_ORDER`, and `ANY_ORDER` matching. | Expected tool calls; choose a match type that reflects the behavior you want to test. |
| `response_match_score` | ROUGE-1 word overlap between the actual and reference response. | A reference response for each case. |
| `final_response_match_v2` | LLM-judged semantic similarity to a reference answer. | A reference response; uses a judge model and may add model cost. |
| `response_evaluation_score` | Vertex AI evaluation of response coherence. | Vertex AI evaluation setup and suitable reference/evaluation data. |
| `rubric_based_final_response_quality_v1` | LLM-judged final-answer quality against criteria you define, such as accuracy, clarity, or helpfulness. | Rubrics that describe a good answer; an LLM judge. |
| `rubric_based_tool_use_quality_v1` | Whether tool use is relevant and follows your quality criteria. | Tool-use rubrics; an LLM judge. |
| `rubric_based_multi_turn_trajectory_quality_v1` | Whether a multi-turn execution follows a desired trajectory. | A multi-turn scenario and trajectory rubrics; an LLM judge. |
| `hallucinations_v1` | Whether answer claims are supported by, or contradict, the available context. | Grounding context, such as tool results; an LLM judge. |
| `safety_v1` | Whether the response meets safety and harmlessness expectations. | Representative safety test cases; an evaluator/judge. |
| `multi_turn_task_success_v1` | Whether the agent achieved the goal of the full conversation. | A multi-turn conversation with a clearly stated goal; an LLM judge. |
| `multi_turn_trajectory_quality_v1` | The overall effectiveness and logic of the conversation trajectory. | A multi-turn conversation; an LLM judge. |
| `multi_turn_tool_use_quality_v1` | The quality and correctness of tool use across a conversation. | A multi-turn conversation with relevant tool-use context; an LLM judge. |
| `per_turn_user_simulator_quality_v1` | The quality of user-simulator turns in simulated conversations. | A user-simulated multi-turn evaluation; an LLM judge. |

ADK also reports these **informational efficiency metrics automatically** for each evaluation; they are not pass/fail criteria and do not need to be added to `test_config.json`:

| Metric | What it reports |
|---|---|
| `tool_call_count_v1` | Number of tool calls. |
| `inference_call_count_v1` | Number of model calls. |
| `token_usage_v1` | Token usage, including available input/output breakdowns. |
| `invocation_duration_v1` | Total invocation time, with available model, tool, and framework breakdowns. |

### How to choose what to measure

The right criteria depend on the behavior you want to verify and what each eval case records:

- For stable regression checks of known prompts, keep a small reference answer and expected tool calls. Use `response_match_score` and `tool_trajectory_avg_score`.
- If correct wording can vary, consider `final_response_match_v2` rather than relying only on word overlap. It uses a model judge, so review its settings and cost.
- If an answer must satisfy a quality standard without one exact reference answer, write a rubric and try `rubric_based_final_response_quality_v1`.
- To test answers grounded in retrieved learning content, include relevant context/tool responses in cases and explore `hallucinations_v1`.
- To test a workflow, create multi-turn cases that include the goal, intermediate turns, and expected behavior, then explore the multi-turn criteria.
- For efficiency regressions, compare the automatic token, call-count, and duration metrics across runs.

This repository's current eval set has three single-turn examples, each with a reference response and expected tool call. That makes the first two criteria applicable, but it does not yet provide a meaningful multi-turn task-success test, a safety-focused suite, or broad hallucination coverage. Add cases for those behaviors before enabling the related criteria. LLM-judged metrics can be probabilistic and may require additional model configuration, API access, time, and cost. See the [official ADK evaluation criteria guide](https://google.github.io/adk-docs/evaluate/criteria/) and [custom metrics guide](https://google.github.io/adk-docs/evaluate/custom_metrics/) for current setup details.

## Ideas for extending this learning repository

These are follow-up exercises, not features currently implemented:

- **Improve evaluation design:** Decide whether evals should expect coordinator handoffs as well as specialist tool calls; compare `EXACT` with `IN_ORDER` matching; add examples for unsupported topics, quiz answers, and session progress.
- **Explore quality metrics:** Add reference answers or rubrics, then try semantic response matching, response-quality rubrics, or groundedness checks. Keep metric configuration with the eval data and compare results across runs.
- **Add multi-turn evaluations:** Test a complete learning flow, such as starting a quiz, answering incorrectly, receiving a hint, retrying, and checking the score.
- **Add safety-focused cases:** Include representative unsupported or unsafe requests and define the expected safe behavior before evaluating `safety_v1`.
- **Try workflow agents:** Use `SequentialAgent`, `ParallelAgent`, or `LoopAgent` to contrast deterministic orchestration with the coordinator's current LLM-directed delegation.
- **Use artifacts:** Have an agent create and retrieve durable learning notes or study plans.
- **Connect trusted information:** Add a built-in or MCP tool that searches official ADK documentation rather than relying only on the bundled learning cards.
- **Experiment with callbacks:** Add model/agent callbacks for tracing, policy enforcement, or modifying execution around model and tool steps.
- **Add durable sessions and deployment:** Replace local in-memory development services with persistence and deploy the agent beyond the local ADK Web UI.

## Run the local tests

These tests verify the agent configuration and tool behavior without calling a model:

```powershell
python -m pytest -q
```

## Project structure

```text
.
├── .gitignore
├── .vscode/
│   └── settings.json               # VS Code Python test configuration
├── assets/                         # Screenshots embedded in this README
│   ├── agent-response.png
│   ├── evals.png
│   ├── graph.png
│   ├── invocation-graph-view.png
│   ├── invoke-subagent-raw-json.png
│   ├── raw-json.png
│   ├── select-session.png
│   ├── tool-usage.png
│   └── traces-info.png
├── eval/
│   ├── results/                    # Local, generated evaluation output (ignored)
│   │   └── learning_coach_eval_results.txt # Existing captured CLI log, if present
│   └── test_config.json            # ADK evaluation criteria and thresholds
├── learning_coach/                 # ADK-discoverable agent package
│   ├── .adk/                       # Local ADK session and evaluation history (ignored)
│   │   ├── eval_history/
│   │   │   └── *.evalset_result.json # Structured result from each ADK eval run
│   │   └── session.db              # Local ADK session storage
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── concept_tutor.py        # Concept specialist
│   │   └── quiz_coach.py           # Quiz specialist
│   ├── .env                        # Local API key; ignored and not committed
│   ├── .env.example                # Credentials template
│   ├── __init__.py                 # Exposes root_agent
│   ├── agent.py                    # Root coordinator
│   ├── callbacks.py                # Tool-call guardrail and logging
│   ├── config.py                   # Shared Gemini model ID
│   ├── learning_coach_basics.evalset.json # Eval set shown in ADK Web
│   └── tools.py                    # Learning, quiz, and progress tools
├── tests/
│   └── test_learning_coach.py      # Offline tests
├── pyproject.toml
└── README.md
```

The tree includes the local `.env`, `.adk` data, and evaluation log to show where they live when present; these are generated or machine-specific files and should not be committed. Evaluation history grows as runs are added, so `*.evalset_result.json` represents the generated files in that folder. The local `.venv/`, `.pytest_cache/`, and Python `__pycache__/` directories are also generated and ignored, and are omitted from the tree.

This follows the official ADK agent-package shape (`<agent>/__init__.py` and `<agent>/agent.py`) while splitting specialists, tools, callbacks, evaluation configuration, and unit tests into focused modules. The eval set itself stays beside the agent package because ADK Web discovers it there.

## Wins

- Uses the official Google ADK package and CLI rather than reimplementing agent execution or evaluation.
- Demonstrates function tools, context-aware session state, callback guardrails, and multi-agent delegation.
- Exercises both tool-use trajectories and final answers using ADK's built-in evaluation metrics.
- Keeps the lesson reproducible: local tools do not depend on external data services.
- Separates offline tests from model-backed evaluations, so tool and state behavior can be checked without API calls.

## Limitations

- Running the agent and official evaluation requires a valid Gemini API key, network access, and may incur model charges.
- Model output is probabilistic. Response matching is approximate, while exact tool matching can fail if the model changes the tool choice or arguments.
- The learning content is a small local example, not a live documentation search or a production knowledge base.
- Session-state persistence depends on the configured ADK session service; local development is not a production persistence setup.
- Automatic delegation and generated answers are probabilistic; the evaluation dataset checks a small set of scenarios, not every possible conversation.
- Workflow agents, artifacts, external MCP integrations, production deployment, and production observability remain suggested extensions rather than part of the core exercise.
- This project is an educational example, not a deployed service or a comprehensive certification of agent quality.
