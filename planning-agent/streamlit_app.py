"""
pip install streamlit langgraph langchain langchain_openai pydantic
"""

from __future__ import annotations

import asyncio
import importlib.util
import pathlib
import sys
from typing import Any, Dict, List

import streamlit as st


def _load_agent_module():
    """
    Load the Planning-Agent.py module (hyphenated filename) via importlib.
    Cached so Streamlit reruns do not reload repeatedly.
    """
    module_path = pathlib.Path(__file__).with_name("Planning-Agent.py")
    spec = importlib.util.spec_from_file_location("planning_agent_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Planning-Agent.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["planning_agent_module"] = module
    spec.loader.exec_module(module)
    return module


@st.cache_resource
def _get_app():
    mod = _load_agent_module()
    app = mod.build_graph()
    return mod, app


def _run_plan(app, mod, user_input: str):
    initial_state = mod.PlanExecuteState(  # type: ignore[attr-defined]
        input=user_input,
        plan=[],
        past_steps=[],
        response="",
    )

    updates: List[Dict[str, Any]] = []

    async def _execute():
        async for update in app.astream(initial_state, stream_mode="updates"):
            updates.append(update)
        final = await app.ainvoke(initial_state)
        return final

    final_state = asyncio.run(_execute())
    return updates, final_state


def main():
    st.set_page_config(page_title="Planning Agent", page_icon="🧭")
    st.title("Plan-and-Execute Agent")

    user_input = st.text_area(
        "Enter your goal", "Research the GDP of France for the last 3 years."
    )

    if st.button("Run plan"):
        with st.spinner("Running agent..."):
            try:
                mod, app = _get_app()
                updates, final = _run_plan(app, mod, user_input)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Error running agent: {exc}")
                return

        st.subheader("Execution updates")
        for idx, upd in enumerate(updates, start=1):
            st.write(f"Step {idx}", upd)

        st.subheader("Final output")
        st.write(final)


if __name__ == "__main__":
    main()
