"""Construye el grafo de clasificación de solicitudes."""

from langgraph.graph import END, START, StateGraph

from .nodes import classify, make_specialist, route_by_category
from .state import ConversationState


def build_graph():
    """Registra los nodos, conecta sus rutas y devuelve el grafo compilado."""
    builder = StateGraph(ConversationState)

    builder.add_node("classify", classify)
    builder.add_node("hr_agent", make_specialist("Respuesta simulada de Recursos Humanos"))
    builder.add_node("it_agent", make_specialist("Respuesta simulada de soporte técnico"))
    builder.add_node(
        "general_agent", make_specialist("Respuesta simulada de atención general")
    )

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",  # Nodo que tomará la decisión
        route_by_category,  # Lee el estado y devuelve una clave de ruta
        {  # Relaciona la clave de ruta con nodo a ejecutar
            "hr": "hr_agent",
            "it": "it_agent",
            "general": "general_agent",
        },
    )

    for agent in ("hr_agent", "it_agent", "general_agent"):
        builder.add_edge(agent, END)

    return builder.compile()