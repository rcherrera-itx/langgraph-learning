"""Construye el grafo de clasificación de solicitudes."""

# Importa los marcadores de inicio y fin, y el constructor del grafo.
from langgraph.graph import END, START, StateGraph

# Permite ejecutar herramientas solicitadas mediante 'tool_calls'
from langgraph.prebuilt import ToolNode

# Importa los nodos y las funciones que deciden las rutas.
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

# Importa el nodo que recupera el perfil desde el store.
from .profiles import load_profile

# Importa la herramienta que consulta el estado de un ticket.
from .services import lookup_ticket

# Importa el modelo siimulado que produce solicitudes y respuestas.
from .simulated_model import SimulatedModel

# Importa la definición de los campos que comparten los nodos.
from .state import ConversationState


def build_graph(checkpointer=None, store=None):
    """Construye el grafo con alamcenamiento opciona para estado y perfiles."""

    # Crea una instancia del modelo simulado para el nodo de TI.
    model = SimulatedModel()

    # Define la estructura del estado que utilizará el grafo.
    builder = StateGraph(ConversationState)

    # Registra el nodo que carga el perfil del empleado.
    builder.add_node("load_profile", load_profile)

    # Registra el nodo que clasifica la solicitud.
    builder.add_node("classify", classify)

    # Registra el nodo que responde solicitudes de Recursos Humanos.
    builder.add_node("hr_agent", make_specialist("Respuesta simulada de Recursos Humanos"))

    # Registra el nodo de TI que puede solicitar una herramienta o responder.
    builder.add_node("it_agent", make_it_agent(model))

    # Registra el nodo que responde solicitudes generales.
    builder.add_node("general_agent", make_specialist("Respuesta simulada de atención general"))

    # Registra el nodo que comprueba el permiso antes de consultar un ticket.
    builder.add_node("authorize_ticket", authorize_ticket)

    # Registra el nodo que ejecuta 'lookup_ticket' cuando existe autorización.
    builder.add_node("it_tools", ToolNode([lookup_ticket]))

    # Registra el nodo que comunica la denegación sin ejecutar la herramienta,
    builder.add_node("deny_ticket", deny_ticket)

    # Inicia cada ejecucuión cargabdo el perfil.
    builder.add_edge(START, "load_profile")

    # Ejecuta la clasificación despúes de cargar el perfil.
    builder.add_edge("load_profile", "classify")

    # Convierte la categoría devuelta en el nombre del nodo especializado.
    builder.add_conditional_edges(
        "classify",  # Nodo que tomará la decisión
        route_by_category,  # Lee el estado y devuelve una clave de ruta
        {  # Relaciona la clave de ruta con nodo a ejecutar
            "hr": "hr_agent",
            "it": "it_agent",
            "general": "general_agent",
        },
    )

    # Finaliza despúes de que responde el nodo de Recursos Humano y solicitudes generales.
    for agent in ("hr_agent", "general_agent"):
        builder.add_edge(agent, END)

    # Si IT solicitó una herramienta, continúa con la autorización.
    # Si IT ya produjo una respuesta final, etermina la ejecución.
    builder.add_conditional_edges(
        "it_agent",
        route_after_it,
        {"authorize": "authorize_ticket", "finish": END},
    )

    # Envía las solicitudes autorizadas a la herramienta.
    # Envía las solicitudes denegadas al nodo que registra la denegación.
    builder.add_conditional_edges(
        "authorize_ticket",
        route_after_authorization,
        {
            "allowed": "it_tools",
            "denied": "deny_ticket"
        }
    )

    # Tras ejecutar la herramienta, IT interpreta su ToolMessage.
    builder.add_edge("it_tools", "it_agent")

    # Tras registrar la denegación, IT redacta la respuesta al usuario.
    builder.add_edge("deny_ticket", "it_agent")

    # Compila el grafo con el checkpointer recibido.
    return builder.compile(checkpointer=checkpointer, store=store)
