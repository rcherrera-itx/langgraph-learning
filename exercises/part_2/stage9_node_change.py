from typing import Literal, NotRequired, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    request: str
    flow_version: NotRequired[int]
    reply: NotRequired[str]


def prepare_old(state: State) -> dict:
    return {"flow_version": 1}


def prepare_new(state: State) -> dict:
    return {"flow_version": 2}


def answer_old(state: State) -> dict:
    print("Ejecutando answer_old")
    return {"reply": "Respuesta de la versión 1"}


def answer_new(state: State) -> dict:
    print("Ejecutando answer_new")
    return {"reply": "Respuesta de la versión 2"}


def route(state: State) -> Literal["answer_old", "answer_new"]:
    if state["flow_version"] == 1:
        return "answer_old"
    return "answer_new"


checkpointer = InMemorySaver()
old_config = {"configurable": {"thread_id": "old-conversation"}}

# Versión 1: se detiene justo antes de answer_old
builder_v1 = StateGraph(State)

builder_v1.add_node("prepare", prepare_old)
builder_v1.add_node("answer_old", answer_old)

builder_v1.add_edge(START, "prepare")
builder_v1.add_edge("prepare", "answer_old")
builder_v1.add_edge("answer_old", END)

graph_v1 = builder_v1.compile(
    checkpointer=checkpointer,
    interrupt_before=["answer_old"]
)

graph_v1.invoke({"request": "Necesito ayuda"}, old_config)
print("Pendiente en versión 1:", graph_v1.get_state(old_config).next)

# Versión 2: las conversaciones nuevas usan answer_new pero answer_old sigue registradi oara las que estaban pendientes
builder_v2 = StateGraph(State)

builder_v2.add_node("prepare", prepare_new)
builder_v2.add_node("answer_old", answer_old)
builder_v2.add_node("answer_new", answer_new)

builder_v2.add_edge(START, "prepare")
builder_v2.add_conditional_edges(
    "prepare",
    route,
    {
        "answer_old": "answer_old",
        "answer_new": "answer_new"
    }
)
builder_v2.add_edge("answer_old", END)
builder_v2.add_edge("answer_new", END)

graph_v2 = builder_v2.compile(checkpointer=checkpointer)

print("Pendiente visto por versión 2:", graph_v2.get_state(old_config).next)
old_result = graph_v2.invoke(None, old_config)
print("Respuesta de conversación anterior:", old_result["reply"])

new_config = {"configurable": {"thread_id": "new_conversation"}}
new_result = graph_v2.invoke({"request": "Necesito ayuda"}, new_config)
print("Respuesta de conversación nueva:", new_result["reply"])