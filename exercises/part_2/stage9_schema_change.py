from typing import NotRequired, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


# Versión 1 guarda el modelo con el nombre antiguo.
class OldState(TypedDict):
    employee_id: str
    laptop_model: NotRequired[str]


def save_old_model(state: OldState) -> dict:
    return {"laptop_model": "X1 Carbon"}


checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "schema-demo-001"}}

old_builder = StateGraph(OldState)

old_builder.add_node("save_old_model", save_old_model)

old_builder.add_edge(START, "save_old_model")
old_builder.add_edge("save_old_model", END)

old_graph = old_builder.compile(checkpointer=checkpointer)
old_graph_result = old_graph.invoke({"employee_id": "EMP-001"}, config)

print("Estado con versión 1:", old_graph_result)

# Versión 2: espera encontrar el campo renombrado

print("\n")
class NewState(TypedDict):
    employee_id: str
    device_model: NotRequired[str]
    reply: NotRequired[str]


def answer(state: NewState) -> dict:
    print("Campos recibidos por versión 2:", list(state))
    return {"reply": f"Tu laptop es {state['device_model']}"}


new_builder = StateGraph(NewState)

new_builder.add_node("answer", answer)

new_builder.add_edge(START, "answer")
new_builder.add_edge("answer", END)

new_graph = new_builder.compile(checkpointer=checkpointer)

print("Estado visible con versión 2:", new_graph.get_state(config).values)

try:
    print(
        "Resultado con versión 2:", new_graph.invoke({"employee_id": "EMP-001"}, config)
    )
except KeyError as error:
    print("Error al ejecutar versión 2:", repr(error))

# Versión 3: reconoce ambos campos

print("\n")
class CompatibleState(TypedDict):
    employee_id: str
    laptop_model: NotRequired[str]
    device_model: NotRequired[str]
    reply: NotRequired[str]


def migrate_model(state: CompatibleState) -> dict:
    print("Estado recibido por migrate_model:", state)

    update = {"device_model": state["laptop_model"]}
    print("Actualización devuelta por migrate_model:", update)

    return update


def answer_compatible(state: CompatibleState) -> dict:
    print("Estado recibido por answer_compatible:", state)
    return {"reply": f"Tu laptop es {state['device_model']}"}




compatible_builder = StateGraph(CompatibleState)

compatible_builder.add_node("migrate_model", migrate_model)
compatible_builder.add_node("answer", answer_compatible)

compatible_builder.add_edge(START, "migrate_model")
compatible_builder.add_edge("migrate_model", "answer")
compatible_builder.add_edge("answer", END)

compatible_graph = compatible_builder.compile(checkpointer=checkpointer)

print(
    "Estado visible con versión compatible:", compatible_graph.get_state(config).values
)
print(
    "Resultado compatible:", compatible_graph.invoke({"employee_id": "EMP-001"}, config)
)
