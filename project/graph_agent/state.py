from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """
    Shared state between all nodes.
    """

    user_input: str

    current_agent: str

    messages: List[Dict[str, str]]

    documents_found: List[Dict[str, Any]]

    final_answer: Optional[str]

    error: Optional[str]

    retry_count: int

    metadata: Dict[str, Any]