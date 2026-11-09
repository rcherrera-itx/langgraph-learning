"""Define los nodos y decisión de ruta de la fase 1"""

from typing import Literal

from langchain_core.messages import AIMessage, ToolMessage

from .services import authorize_ticket_requests
from .simulated_model import SimulatedModel
from .state import ConversationState


def classify(state: ConversationState) -> dict:
    """Clasifica la última solicitud y devuelve una actualizaicón del estado."""

    # Lee el último mensaje sin cambiarlo
    text = state["messages"][-1].content.lower()

    if "vacaciones" in text:
        return {"category": "hr"}

    if "computadora" in text or "ticket" in text:
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


def make_it_agent(model: SimulatedModel) -> callable[[ConversationState], dict]:
    """Crea el nodo de TI utilizando el modelo recibido."""

    def it_agent(state: ConversationState) -> dict:
        """Entrega el historial al modelo y devuelve su mensaje."""

        response = model.invoke(state["messages"])
        return {"messages": [response]}

    return it_agent


def route_after_it(state: ConversationState) -> Literal["authorize", "finish"]:
    """Decide si el modelo pidió una herramienta o ya respondió."""

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "authorize"

    return "finish"


def authorize_ticket(state: ConversationState) -> dict:
    """Consulta la política de la aplicación y devuelve la decisión."""

    request = state["messages"][-1]

    allowed = authorize_ticket_requests(state["employee_id"], request.tool_calls)

    return {"authorized": allowed}


def route_after_authorization(state:ConversationState) -> Literal["allowed", "denied"]:
    """Elige la ruta según la decisión ya incorporada al estado."""

    if state["authorized"]:
        return "allowed"

    return "denied"


def deny_ticket(state:ConversationState) -> dict:
    """Cierra la llamada rechazada sin ejecutar la herramienta."""

    request = state["messages"][-1]
    call_id = request.tool_calls[0]["id"]

    denial = ToolMessage(
        content="DENIED: No tienes permisos para consultar este ticket.",
        tool_call_id=call_id
    )

    return {
        "messages": [denial],
        "errors": ["Consulta de ticket denegada."]
    }