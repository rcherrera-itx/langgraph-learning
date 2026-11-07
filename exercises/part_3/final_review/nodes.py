"""Define los nodos y decisión de ruta de la fase 1"""

from typing import Literal

from langchain_core.messages import AIMessage

from .state import ConversationState


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