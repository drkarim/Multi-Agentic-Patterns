# Planning Agent (Plan-and-Execute)

## Pattern overview
This repo uses the Planning pattern from agentic design: a **Planner** (strategist) breaks a goal into steps, and an **Executor** (doer) executes them in a loop. The Planner revises the plan after each step until the work is done. This yields adaptability and clear decomposition for complex tasks.

## Implementation in this project
- **Planner node** (`planner_node` in `Planning-Agent.py`): Calls `gpt-5.x` with structured output to produce remaining steps. If it sees `DONE`, the graph ends. A recursion cap stops infinite loops.
- **Executor node** (`executor_node` in `Planning-Agent.py`): Takes the next step, runs it through an LLM-bound tool call, and logs `(step, result)` into `past_steps`. It currently uses the Tavily web search tool (`TavilySearch`).
- **State graph**: Entry is `planner`; conditional edge ends when plan starts with `DONE`, otherwise goes to `executor`, which loops back to `planner`.
- **Streamlit UI** (`streamlit_app.py`): Lets a user enter a goal, streams updates, and shows the final state.

## Setup: environment variables
The app needs two API keys:
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`

You can set them in your shell:
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:TAVILY_API_KEY="tvly-..."
```
Or place them in a `.env` file in the repo root:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

## Install dependencies
Use the existing virtual environment or install from `requirements.txt`:
```powershell
.venv\Scripts\pip install -r requirements.txt
```

## Run the Streamlit app
```powershell
.venv\Scripts\python -m streamlit run streamlit_app.py
```

After launching, open the provided local URL, enter a goal, and watch plan/execution updates stream in. The final state is printed in a human-readable form at the end.
