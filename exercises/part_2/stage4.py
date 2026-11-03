from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


@tool
def lookup_ticket(ticket_id: str) -> str:
    """Consulta el estado de un ticket de soporte mediante su identificador."""

    fake_db = {
        "INC-4471": (
            "Abierto; asignado al equipo de redes. Última actualización: hace 2 días."
        ),
        "INC-4472": "Resuelto; laptop de reemplazo enviada.",
    }

    return fake_db.get(ticket_id, f"No se encontró el ticket {ticket_id}")


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class SimulatedModel:
    def invoke(self, messages):
        last_message = messages[-1]

        if isinstance(last_message, ToolMessage):
            return AIMessage(content=f"Estado consultado: {last_message.content}")

        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "lookup_ticket",
                    "args": {"ticket_id": "INC-4471"},
                    "id": "call_001",
                }
            ],
        )

model = SimulatedModel()

def it_agent(state: HelpdeskState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(HelpdeskState)

builder.add_node("it_agent", it_agent)
builder.add_node("it_tools", ToolNode([lookup_ticket]))

builder.add_edge(START, "it_agent")

builder.add_conditional_edges("it_agent", tools_condition, {
    "tools": "it_tools",
    "__end__": END,
})

builder.add_edge("it_tools", "it_agent")

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="¿Cuál es el estado del ticket INC-4471?")
            ]
        },
        config={"recursion_limit": 12}
    )

    print("Mensajes en el estado:", len(result["messages"]))

    for message in result["messages"]:
        print(f"{type(message).__name__}: {message.content}")

        if isinstance(message, AIMessage):
            print("  Solicitudes de herramientas:", message.tool_calls)
