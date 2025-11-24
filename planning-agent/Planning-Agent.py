"""
pip install langgraph langchain langchain_openai langchain-tavily pydantic
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from functools import lru_cache
from typing import List, Tuple, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field, SecretStr, ValidationError


RECURSION_LIMIT = 2


# --- State definition ---
class PlanExecuteState(TypedDict):
    input: str
    plan: List[str]
    past_steps: List[Tuple[str, str]]
    response: str


# --- Data model for structured planner output ---
class Plan(BaseModel):
    steps: List[str] = Field(..., description="Ordered list of remaining steps.")


# --- Settings ---
class Settings(BaseModel):
    openai_api_key: SecretStr
    tavily_api_key: SecretStr


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Load secrets from environment once. Set OPENAI_API_KEY in your shell or env file.
    Example (PowerShell): `$env:OPENAI_API_KEY='sk-...'`.
    """
    raw = os.getenv("OPENAI_API_KEY")
    tavily_raw = os.getenv("TAVILY_API_KEY")

    env_path = Path(__file__).resolve().parent / ".env"
    if (not raw or not tavily_raw) and env_path.exists():
        with env_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not raw and line.strip().startswith("OPENAI_API_KEY="):
                    raw = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                if not tavily_raw and line.strip().startswith("TAVILY_API_KEY="):
                    tavily_raw = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

    if not raw or not tavily_raw:
        raise RuntimeError(
            "OPENAI_API_KEY and/or TAVILY_API_KEY is not set. Export them in your shell "
            "or add them to a .env file in this folder."
        )
    # Ensure downstream libs that rely on environment variables can pick them up.
    os.environ.setdefault("OPENAI_API_KEY", raw)
    os.environ.setdefault("TAVILY_API_KEY", tavily_raw)
    return Settings(openai_api_key=SecretStr(raw), tavily_api_key=SecretStr(tavily_raw))


def _build_search_tool(settings: Settings) -> TavilySearchResults:
    return TavilySearch(max_results=3, api_key=settings.tavily_api_key.get_secret_value())


def _build_planner():
    settings = get_settings()
    llm = init_chat_model(
        "gpt-5.1",
        model_provider="openai",
        temperature=0,
        api_key=settings.openai_api_key.get_secret_value(),
    )
    prompt = ChatPromptTemplate.from_template(
        "You are an expert planner.\n"
        "User goal: {input}\n"
        "Past steps and results: {past_steps}\n"
        "Output the remaining steps to finish the goal. "
        "If finished, output 'DONE' as the only step."
    )
    return prompt | llm.with_structured_output(Plan)


def planner_node(state: PlanExecuteState) -> PlanExecuteState:
    if len(state["past_steps"]) >= RECURSION_LIMIT:
        return {"plan": ["DONE"], "response": "Recursion limit reached."}

    chain = _build_planner()
    try:
        plan = chain.invoke({"input": state["input"], "past_steps": state["past_steps"]})
        return {"plan": plan.steps}
    except ValidationError as exc:
        logging.error("Planner validation failed: %s", exc)
        return {"plan": ["DONE"], "response": "Planner failed; terminating."}
    except Exception as exc:  # noqa: BLE001
        logging.exception("Planner errored")
        return {"plan": ["DONE"], "response": f"Planner error: {exc}"}


def _run_step_with_tools(step: str) -> str:
    """Minimal tool-calling loop without AgentExecutor (not available in langchain 1.0.x)."""
    settings = get_settings()
    search_tool = _build_search_tool(settings)
    llm = init_chat_model(
        "gpt-5.1",
        model_provider="openai",
        temperature=0,
        api_key=settings.openai_api_key.get_secret_value(),
    ).bind_tools([search_tool])

    messages = [
        SystemMessage(
            content="You execute a single step from the plan. Keep answers concise and factual."
        ),
        HumanMessage(content=step),
    ]

    ai: AIMessage = llm.invoke(messages)  # type: ignore[assignment]

    # Handle tool calls, if any
    while getattr(ai, "tool_calls", None):
        messages.append(ai)  # keep the AI message that contains tool_calls
        tool_messages: List[ToolMessage] = []
        for call in ai.tool_calls:
            try:
                # Tavily tool expects kwargs dict; call["args"] already a mapping
                result = search_tool.invoke(call["args"])
            except Exception as exc:  # noqa: BLE001
                result = f"Tool error: {exc}"
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
        messages.extend(tool_messages)
        ai = llm.invoke(messages)  # type: ignore[assignment]

    content = ai.content
    return content if isinstance(content, str) else str(content)


def executor_node(state: PlanExecuteState) -> PlanExecuteState:
    if not state["plan"]:
        return {"plan": ["DONE"], "response": "No plan to execute."}

    step = state["plan"][0]
    try:
        result = _run_step_with_tools(step)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Executor errored")
        result = f"Executor error: {exc}"

    updated_past = state["past_steps"] + [(step, result)]
    updated_plan = state["plan"][1:]

    return {
        "past_steps": updated_past,
        "plan": updated_plan,
        "response": result,
    }


# --- Graph wiring ---
def build_graph():
    graph = StateGraph(PlanExecuteState)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)

    graph.set_entry_point("planner")

    def should_end(state: PlanExecuteState) -> str:
        if state["plan"] and state["plan"][0].strip().upper() == "DONE":
            return END
        return "executor"

    graph.add_conditional_edges("planner", should_end)
    graph.add_edge("executor", "planner")
    return graph.compile()


async def main():
    logging.basicConfig(level=logging.INFO)
    app = build_graph()
    query = "Research the GDP of France for the last 3 years."
    initial_state: PlanExecuteState = {
        "input": query,
        "plan": [],
        "past_steps": [],
        "response": "",
    }

    print("=== Streaming plan/execution updates ===")
    async for update in app.astream(initial_state, stream_mode="updates"):
        print(update)

    final = await app.ainvoke(initial_state)
    print("\n=== Final state ===")
    print(final)


if __name__ == "__main__":
    asyncio.run(main())
