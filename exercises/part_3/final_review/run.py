"""Ejecuta un caso de prueba de la fase 1"""

from langchain_core.messages import AIMessage, HumanMessage

from .graph import build_graph
from .state import ConversationState


def main() -> None:
    """Ejecuta una solicitud y muesta el estado resultante."""

    graph = build_graph()

    initial_state: ConversationState = {
        "messages": [HumanMessage(content="¿Cuál es el estado del ticket INC-4471?")],
        "errors": [],
        "category": "",
        "employee_id": "EMP-002",
        "profile": {},
        "authorized": False,
    }

    result = graph.invoke(initial_state)

    print("Categoría:", result["category"])
    print("Mensajes:", len(result["messages"]))
    print("Autorizado:", result["authorized"])
    print("Errores:", result["errors"])

    for message in result["messages"]:
        print(f"{type(message).__name__}: {message.content}")

        if isinstance(message, AIMessage):
            print("Solicitudes:", message.tool_calls)


if __name__ == "__main__":
    main()
