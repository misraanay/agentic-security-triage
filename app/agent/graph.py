from typing import TypedDict
from uuid import UUID
from langgraph.graph import START, END, StateGraph

class SecurityState(TypedDict):

    scan_id: UUID
    finding_id: UUID
    repo_path: str

    analysis: str | None
    relevant_files: list[str]
    patch: str | None

    validation_passed: bool | None
    validation_error: str | None

    retry_count: int

def investigate(state: SecurityState):
    print(f"Lets investigate finding: {state['finding_id']}")

    return {
        'analysis': "Place Holder Anaylsis",
        'relevant_files': ["test1.py", "test2.py", "test3.py"],
    }

graph = StateGraph(SecurityState)
graph.add_node("investigate", investigate)
graph.add_edge(START, "investigate")
graph.add_edge("investigate", END)
security_graph = graph.compile()
