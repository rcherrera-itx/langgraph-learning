from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


class TemporaryFailure(Exception):
    pass


class State(TypedDict):
    reset_done: bool
    request_id: str


# Simula un sistema externo durante esta ejecución.
external_system = {"resets": 0, "processed": set()}
attempts = 0


def external_reset(operation_key: str) -> None:
    if operation_key in external_system["processed"]:
        print("Acción omitida: solicitud ya procesada")
        return

    external_system["processed"].add(operation_key)
    external_system["resets"] += 1
    print("Reestablecimientos realizados:", external_system["resets"])


def reset_password(state: State) -> dict:
    global attempts
    attempts += 1

    operational_key = f"reset_password:{state["request_id"]}"

    print(f"\nIntento {attempts}")
    print("reset_done recibido:", state["reset_done"])
    print("Clave de operación:", operational_key)

    external_reset(operation_key=operational_key)

    if attempts == 1:
        print("Fallo antes de devolver la actualización")
        raise TemporaryFailure("Fallo simulado")

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

builder.add_edge(START, "reset_password")
builder.add_edge("reset_password", END)

graph = builder.compile()
result = graph.invoke({"reset_done": False, "request_id": "reset-EMP-001-001"})

print("\nEstado final:", result)
print("Acciones realizadas:", external_system["resets"])