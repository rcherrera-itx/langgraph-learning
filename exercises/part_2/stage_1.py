from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# 1. STATE: estructura de los datos
class HelpdeskState(TypedDict):
    request: str
    reply: str
    handled_by: str


# 2. NODE: tarea que procesa la solicitud
def echo_node(state: HelpdeskState) -> dict:
    request = state["request"]

    return {"reply": f"Received: {request!r}", "handled_by": "echo"}


# 3. WIRING: registro del nodo y sus conexiones.
builder = StateGraph(HelpdeskState)
builder.add_node("echo", echo_node)

builder.add_edge(START, "echo")
builder.add_edge("echo", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {"request": "Mi computadora no enciende", "reply": "", "handled_by": ""}
    )

    print(result)
    print(graph.get_graph().draw_mermaid())
