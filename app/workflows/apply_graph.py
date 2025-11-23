from typing import TypedDict
from langgraph.graph import StateGraph

class ApplyState(TypedDict):
    candidate_id: str
    job_id: str
    resume_text: str
    status: str
    message: str

def validate_input(state: ApplyState) -> ApplyState:
    # later: check candidate + job exist in DB
    state["status"] = "validated"
    state["message"] = "Input validated"
    return state

def score_match(state: ApplyState) -> ApplyState:
    # later: call LangChain RAG/LLM
    state["status"] = "scored"
    state["message"] = "Candidate-job match scored"
    return state

def build_apply_graph():
    graph = StateGraph(ApplyState)
    graph.add_node("validate_input", validate_input)
    graph.add_node("score_match", score_match)

    graph.set_entry_point("validate_input")
    graph.add_edge("validate_input", "score_match")

    return graph.compile()
