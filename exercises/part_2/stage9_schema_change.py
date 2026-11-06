from typing import NotRequired, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class OldState(TypedDict):
    employee_id: str
    laptop_model: NotRequired[str]


class NewState(TypedDict):
    employee_id: str
    device_model: NotRequired[str]
    reply: NotRequired[str]


checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "schema-demo-001"}}


# Versión 1 guarda el modelo con el nombre antiguo.
def register(state: OldState) -> dict:
    return {"laptop_model": "X1 Carbon"}


old_builder = StateGraph(OldState)

old_builder.add_node("register", register)

old_builder.add_edge(START, "register")
old_builder.add_edge("register", END)

old_graph = old_builder.compile(checkpointer=checkpointer)

print("Estado con versión 1:", old_graph.invoke({"employee_id": "EMP-001"}, config))

# Versión 2: espera encontrar el campo renombrado
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
    print("Resultado con versión 2:", new_graph.invoke({
        "employee_id": "EMP-001"
    }, config))
except KeyError as error:
    print("Error al ejecutar versión 2:", repr(error))


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

print("\n")

compatible_builder = StateGraph(CompatibleState)

compatible_builder.add_node("migrate_model", migrate_model)
compatible_builder.add_node("answer", answer_compatible)

compatible_builder.add_edge(START, "migrate_model")
compatible_builder.add_edge("migrate_model", "answer")
compatible_builder.add_edge("answer", END)

compatible_graph = compatible_builder.compile(checkpointer=checkpointer)

print("Estado visible con versión compatible:", compatible_graph.get_state(config).values)
print(
    "Resultado compatible:", 
    compatible_graph.invoke({"employee_id": "EMP-001"}, config)
)