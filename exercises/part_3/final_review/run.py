"""Ejecuta un caso de prueba de la fase 1"""

from langchain_core.messages import HumanMessage

from .graph import build_graph
from .state import ConversationState


def main() -> None:
    """Ejecuta una solicitud y muesta el estado resultante."""

    graph = build_graph()

    initial_state: ConversationState = {
        "messages": [HumanMessage(content="¿Cuántos días tengo de vacaciones?.")],
        "errors": [],
        "category": "",
        "employee_id": "EMP-001",
        "profile": {},
    }

    result = graph.invoke(initial_state)

    print("Categoría:", result["category"])
    print("Mensajes:", len(result["messages"]))

    for message in result["messages"]:
        print(f"{type(message).__name__}: {message.content}")


if __name__ == "__main__":
    main()
