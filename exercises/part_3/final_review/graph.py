"""Construye el grafo de clasificación de solicitudes."""

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from .nodes import (
    authorize_ticket,
    classify,
    deny_ticket,
    make_it_agent,
    make_specialist,
    route_after_authorization,
    route_after_it,
    route_by_category,
)
from .services import lookup_ticket
from .simulated_model import SimulatedModel
from .state import ConversationState


def build_graph():
    """Registra los nodos, conecta sus rutas y devuelve el grafo compilado."""

    model = SimulatedModel()

    builder = StateGraph(ConversationState)

    builder.add_node("classify", classify)

    builder.add_node("hr_agent", make_specialist("Respuesta simulada de Recursos Humanos"))
    builder.add_node("it_agent", make_it_agent(model))
    builder.add_node("general_agent", make_specialist("Respuesta simulada de atención general"))

    builder.add_node("authorize_ticket", authorize_ticket)
    builder.add_node("it_tools", ToolNode([lookup_ticket]))
    builder.add_node("deny_ticket", deny_ticket)

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

    for agent in ("hr_agent", "general_agent"):
        builder.add_edge(agent, END)

    builder.add_conditional_edges(
        "it_agent",
        route_after_it,
        {"authorize": "authorize_ticket", "finish": END},
    )

    builder.add_conditional_edges(
        "authorize_ticket",
        route_after_authorization,
        {
            "allowed": "it_tools",
            "denied": "deny_ticket"
        }
    )

    builder.add_edge("it_tools", "it_agent")
    builder.add_edge("deny_ticket", "it_agent")

    return builder.compile()
