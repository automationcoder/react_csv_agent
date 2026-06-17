from typing import Dict, Any

from project.graph_agent.state import AgentState
from project.graph_agent.commands import Command
from project.graph_agent.routing import route_from_supervisor
from project.rag.rag_service import RAGService


def add_message(state: AgentState, role: str, content: str) -> None:
    state["messages"].append(
        {
            "role": role,
            "content": content,
        }
    )


def supervisor_node(state: AgentState) -> Command:
    add_message(state, "supervisor", "Supervisor received the user request.")

    route = route_from_supervisor(state)

    add_message(
        state,
        "supervisor",
        f"Supervisor decided to route to: {route.goto}",
    )

    state["current_agent"] = "supervisor"

    return route


def retriever_node(state: AgentState) -> Command:
    state["current_agent"] = "retriever"
    add_message(state, "retriever", "Retriever started semantic document search.")

    try:
        rag = RAGService()

        results = rag.search(
            query=state["user_input"],
            top_k=3,
        )

        state["documents_found"] = results
        state["error"] = None

        add_message(
            state,
            "retriever",
            f"Retriever found {len(results)} relevant chunk(s).",
        )

        return Command(goto="analyst")

    except Exception as exc:
        state["error"] = str(exc)
        add_message(
            state,
            "retriever",
            f"Retriever failed with error: {exc}",
        )

        return Command(goto="fallback")


def analyst_node(state: AgentState) -> Command:
    state["current_agent"] = "analyst"
    add_message(state, "analyst", "Analyst is preparing final answer.")

    documents = state["documents_found"]

    if documents:
        lines = []

        for item in documents:
            filename = item.get("filename", "unknown")
            content = item.get("content", "")
            score = item.get("score", 0)

            lines.append(
                f"Source: {filename}\n"
                f"Score: {score:.3f}\n"
                f"Content: {content}"
            )

        state["final_answer"] = (
            "Answer based on retrieved documents:\n\n"
            + "\n\n".join(lines)
        )

    else:
        state["final_answer"] = (
            "I could not find relevant information in the stored documents."
        )

    add_message(state, "analyst", "Analyst generated final answer.")

    return Command(goto="end")


def fallback_node(state: AgentState) -> Command:
    state["current_agent"] = "fallback"
    state["retry_count"] += 1

    add_message(
        state,
        "fallback",
        f"Fallback activated. Retry count: {state['retry_count']}",
    )

    if state["retry_count"] <= 1:
        add_message(state, "fallback", "Retrying retriever once.")
        return Command(goto="retriever")

    state["final_answer"] = (
        "The system could not complete the request after retry. "
        f"Last error: {state['error']}"
    )

    return Command(goto="end")