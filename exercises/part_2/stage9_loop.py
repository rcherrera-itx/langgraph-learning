from typing import TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.managed import RemainingSteps


class State(TypedDict):
    count: int
    remaining_steps: RemainingSteps


def tick(state: State) -> dict:
    count = state["count"] + 1
    print(f"Paso {count}")
    return {"count": count}


def route(state: State):
    if state["count"] >= 3:
        return END

    if state["remaining_steps"] <= 2:
        print("Quedan pocos pasos; terminando con resultado parcial.")
        return END

    return "tick"



builder = StateGraph(State)

builder.add_node("tick", tick)

builder.add_edge(START, "tick")
builder.add_conditional_edges("tick", route)

graph = builder.compile()

for limit in (2, 5):
    print("\nLimite:", limit)
    try:
        result = graph.invoke(
            {"count": 0},
            {"recursion_limit": limit}
        )
        print("Resultados:", result["count"])
    except GraphRecursionError:
        print("Se alcanzó el límite antes de terminar.")