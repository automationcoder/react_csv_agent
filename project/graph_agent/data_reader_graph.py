from typing import Callable, Dict

from project.graph_agent.commands import Command
from project.graph_agent.nodes import (
    analyst_node,
    fallback_node,
    retriever_node,
    supervisor_node,
)
from project.graph_agent.state import AgentState


class DataReaderGraph:
    """
    Small LangGraph-like runner:
    state -> node -> command -> next node
    """

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps

        self.nodes: Dict[str, Callable[[AgentState], Command]] = {
            "supervisor": supervisor_node,
            "retriever": retriever_node,
            "analyst": analyst_node,
            "fallback": fallback_node,
        }

    def run(self, user_input: str) -> AgentState:
        state: AgentState = {
            "user_input": user_input,
            "current_agent": "supervisor",
            "messages": [],
            "documents_found": [],
            "final_answer": None,
            "error": None,
            "retry_count": 0,
            "metadata": {},
        }

        current_node = "supervisor"

        for step in range(self.max_steps):
            state["metadata"]["step"] = step
            state["current_agent"] = current_node

            if current_node == "end":
                return state

            node_function = self.nodes.get(current_node)

            if node_function is None:
                state["error"] = f"Unknown node: {current_node}"
                state["final_answer"] = state["error"]
                return state

            command = node_function(state)

            if command.update:
                state.update(command.update)

            current_node = command.goto

        state["error"] = "Graph stopped because max_steps was reached."
        state["final_answer"] = state["error"]

        return state
