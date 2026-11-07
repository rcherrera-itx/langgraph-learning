import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    """Define los datos que comparten los nodos del grafo."""

    messages: Annotated[list[AnyMessage], add_messages]
    errors: Annotated[list[str], operator.add]
    category: str
    employee_id: str
    profile: dict


def classify(state: ConversationState) -> dict:
    """Clasifica la última solicitud y devuelve una actualizaicón del estado."""

    # Lee el último mensaje sin cambiarlo
    text = state["messages"][-1].content.lower()

    if "vacaciones" in text:
        return {"category": "hr"}

    if "computadora" in text:
        return {"category": "it"}

    return {"category": "general"}


def route_by_category(state: ConversationState) -> Literal["hr", "it", "general"]:
    """Devuelve la ruta correspondiente a la categoría ya guardada."""

    if state["category"] == "hr":
        return "hr"

    if state["category"] == "it":
        return "it"

    return "general"


def make_specialist(reply: str):
    """Crea un nodo que devuelve la respuesta simulada indicada."""

    def specialist(state: ConversationState) -> dict:
        """Devuelve un mensaje nuevo para incorporarlo al historial."""

        return {"messages": [AIMessage(content=reply)]}

    return specialist


builder = StateGraph(ConversationState)

builder.add_node("classify", classify)
builder.add_node("hr_agent", make_specialist("Respuesta simulada de Recursos Humanos"))
builder.add_node("it_agent", make_specialist("Respuesta simulada de soporte técnico"))
builder.add_node("general_agent", make_specialist("Respuesta simulada de atención general"))

builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify", # Nodo que tomará la decisión
    route_by_category, # Lee el estado y devuelve una clave de ruta
    { # Relaciona la clave de ruta con nodo a ejecutar
        "hr": "hr_agent",
        "it": "it_agent",
        "general": "general_agent"
    }
)

for agent in ("hr_agent", "it_agent", "general_agent"):
    builder.add_edge(agent, END)

graph = builder.compile()

result = graph.invoke({
    # "messages": [HumanMessage(content="Mi computadora no enciende.")],
    "messages": [HumanMessage(content="¿Cuántos días tengo de vacaciones?.")],
    "errors": [],
    "category": "",
    "employee_id": "EMP-001",
    "profile": {}
})

print("Categoría:", result["category"])
print("Mensajes:", len(result["messages"]))

for message in result["messages"]:
    print(f"{type(message).__name__}: {message.content}")