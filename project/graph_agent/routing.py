from project.graph_agent.commands import Command
from project.graph_agent.state import AgentState


def route_from_supervisor(state: AgentState) -> Command:

    question = state["user_input"].lower()

    if "document" in question:
        return Command(goto="retriever")

    if "contract" in question:
        return Command(goto="retriever")

    if "invoice" in question:
        return Command(goto="retriever")

    return Command(goto="analyst")