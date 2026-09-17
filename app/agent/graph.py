from typing import TypedDict
from uuid import UUID
from dotenv import load_dotenv
load_dotenv()
import os

from langgraph.graph import START, END, StateGraph
from langchain_groq import ChatGroq

groq_api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("MODEL")

llm = ChatGroq(
    api_key=groq_api_key,
    model=model,
    temperature=0,
    reasoning_effort="medium",
    max_retries=2,
)

class FindingEvidence(TypedDict):
    check_id: str
    path: str
    start_line: int
    end_line: int
    message: str
    severity: str

class SecurityState(TypedDict):

    scan_id: UUID
    finding_id: UUID
    repo_path: str
    finding: FindingEvidence

    analysis: str | None
    relevant_files: list[str]
    patch: str | None

    validation_passed: bool | None
    validation_error: str | None

    retry_count: int


def investigate(state: SecurityState):
    print(f"Lets investigate finding: {state['finding_id']}")

    # LLM investigates 20 lines before and after
    filepath = os.path.join(state['repo_path'], state['finding']['path'])

    relevant_lines = []
    with open(filepath) as f:
        relevant_lines = f.readlines()
        relevant_lines = relevant_lines[max(0, state['finding']['start_line']-20-1):state['finding']['end_line']+20]

    if relevant_lines == []:
        return {
            "analysis": "No relevant lines found",
            "relevant_files": ["No relevant lines found"],
        }

    source = "".join(relevant_lines)

    prompt = f"""
    You are investigating a static-analysis security finding in a software repository.

    Semgrep finding:
    - Rule: {state["finding"]["check_id"]}
    - Severity: {state["finding"]["severity"]}
    - Message: {state["finding"]["message"]}
    - File: {state["finding"]["path"]}
    - Lines: {state["finding"]["start_line"]}-{state["finding"]["end_line"]}

    Source code around the finding:
    ```{source}```

    Analyze the finding.

    Determine:
    1. What security issue Semgrep detected.
    2. Whether the provided code supports the finding.
    3. Why the code may be vulnerable.
    4. What additional repository context, if any, would be useful to investigate.

    Do not propose a fix yet.
    """

    response = llm.invoke(prompt)

    return {
        'analysis': f"{response.content}",
        'relevant_files': [state["finding"]["path"]],
    }

graph = StateGraph(SecurityState)
graph.add_node("investigate", investigate)
graph.add_edge(START, "investigate")
graph.add_edge("investigate", END)
security_graph = graph.compile()
