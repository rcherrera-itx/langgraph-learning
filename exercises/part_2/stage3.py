from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

Category = Literal["it", "hr", "general"]


class Triage(BaseModel):
    category: Category = Field(description="Equipo que debe atender la solicitud")
    reason: str = Field(description="Expliación breve de la clasificación")


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    category: str
    reason: str


def classify(state: HelpdeskState) -> dict:
    # Simulamos el resultado del clasificador
    classification = Triage(
        category="it", reason="La solicitud trata sobre un problema de hardware."
    )

    return {"category": classification.category, "reason": classification.reason}


def specialist(response_text: str):
    def node(state: HelpdeskState) -> dict:
        return {"messages": [AIMessage(content=response_text)]}

    return node

it_agent = specialist("Respuesta simulada de soporte técnico")
hr_agent = specialist("Respuesta simulada de Recursos Humanos")
general_agent = specialist("Respuesta simulada de atención general")

# def route_after_classify(state: HelpdeskState) -> Literal["it_agent", "hr_agent", "general_agent"] :
#     destinations = {
#         "it": "it_agent",
#         "hr": "hr_agent",
#         "general": "general_agent"
#     }

#     destination = destinations[state["category"]]
#     print("[Enrutamiento por nodo] Valor devuelto:", destination)
#     return destination


def route_by_category(state: HelpdeskState) -> str:
    category = state["category"]
    print("[Enrutamiento con mapeo] Valor devuelto:", category)
    return category


builder = StateGraph(HelpdeskState)
builder.add_node("classify", classify)
builder.add_node("it_agent", it_agent)
builder.add_node("hr_agent", hr_agent)
builder.add_node("general_agent", general_agent)

builder.add_edge(START, "classify")

# builder.add_conditional_edges("classify", route_after_classify)
builder.add_conditional_edges(
    "classify",
    route_by_category,
    path_map={"it": "it_agent", "hr": "hr_agent", "general": "general_agent"},
)

builder.add_edge("it_agent", END)
builder.add_edge("hr_agent", END)
builder.add_edge("general_agent", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="Mi computadora no enciende.")],
            "category": "",
            "reason": "",
        }
    )

    print("Categoría en el estado:", result["category"])
    print("Motivo en el estado:", result["reason"])
    print("Mensajes conservados:", len(result["messages"]))

    for message in result["messages"]:
        print(f"{type(message).__name__}: {message.content}")

    print(graph.get_graph().draw_mermaid())
