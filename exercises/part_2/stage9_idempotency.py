from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


class TemporaryFailure(Exception):
    pass


class State(TypedDict):
    reset_done: bool


external_system = {"resets": 0}
attempts = 0


def reset_password(state: State) -> dict:
    global attempts
    attempts += 1

    print(f"\nIntento {attempts}")
    print("reset_done recibido:", state["reset_done"])

    # Simula que el sistema externo ya realizó la acción.
    external_system["resets"] += 1
    print("Reestablecimientos realizados:", external_system["resets"])

    if attempts == 1:
        print("Fallo antes de devolver la actualización")
        raise TemporaryFailure("Fallo simulado")

    print('Devolviendo: {"reset_done": True}')
    return {"reset_done": True}


builder = StateGraph(State)
builder.add_node(
    "reset_password",
    reset_password,
    retry_policy=RetryPolicy(
        max_attempts=2,
        retry_on=TemporaryFailure,
        initial_interval=0.0,
        jitter=False
    ),
)

print("Política registrada:", builder.nodes["reset_password"].retry_policy)

builder.add_edge(START, "reset_password")
builder.add_edge("reset_password", END)

graph = builder.compile()
result = graph.invoke({"reset_done": False})

print("\nEstado final:", result)
print("Acciones realizadas:", external_system["resets"])