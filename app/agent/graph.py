from typing import TypedDict
from uuid import UUID
from dotenv import load_dotenv
load_dotenv()
import os
import subprocess

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
    finding = state["finding"]

    # 1. Read source around the Semgrep finding
    filepath = os.path.join(
        state["repo_path"],
        finding["path"],
    )

    with open(filepath) as f:
        lines = f.readlines()

    relevant_lines = lines[
        max(0, finding["start_line"] - 20 - 1):
        finding["end_line"] + 20
    ]

    source = "".join(relevant_lines)

    # 2. Ask Graphify for repository-level structural context
    graph_path = os.path.join(
        state["repo_path"],
        "graphify-out",
        "graph.json",
    )

    graph_question = (
        f"Find code structurally related to {finding['path']} "
        f"that is relevant to this security finding: {finding['message']}"
    )

    graph_result = subprocess.run(
        [
            "graphify",
            "query",
            graph_question,
            "--graph",
            graph_path,
            "--budget",
            "1000",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    graph_context = graph_result.stdout

    print("\n=== GRAPHIFY CONTEXT ===")
    print(graph_context)
    print("========================\n")

    # 3. Give Semgrep evidence + local source + Graphify context to LLM
    prompt = f"""
    You are investigating a static-analysis security finding in a source-code repository.
    
    SEMGREP FINDING
    
    Rule:
    {finding["check_id"]}
    
    Severity:
    {finding["severity"]}
    
    File:
    {finding["path"]}
    
    Lines:
    {finding["start_line"]}-{finding["end_line"]}
    
    Message:
    {finding["message"]}
    
    
    SOURCE CODE AROUND FINDING
    
    {source}
    
    
    REPOSITORY STRUCTURAL CONTEXT FROM GRAPHIFY
    
    {graph_context}
    
    
    Investigate the finding.
    
    Determine:
    1. What security issue Semgrep detected.
    2. Whether the provided code supports the finding.
    3. How repository-level context affects whether this is actually exploitable or important.
    4. Which additional repository context would be useful if the evidence is insufficient.
    
    Clearly distinguish observed evidence from assumptions or inferred risk.
    Do not claim repository behavior that is not supported by the provided evidence.
    """

    response = llm.invoke(prompt)

    return {
        "analysis": response.content,
        "relevant_files": [finding["path"]],
    }


# Build workflow
graph = StateGraph(SecurityState)

graph.add_node("investigate", investigate)

graph.add_edge(START, "investigate")
graph.add_edge("investigate", END)

security_graph = graph.compile()
