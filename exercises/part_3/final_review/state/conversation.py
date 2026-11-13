"""Define los datos compartidos durante una conversación del chatbot."""

# proporciona el reducer que acumula la lista de errores.
import operator

# Define el tipo de los campos y sus reglas de actualización-
from typing import Annotated, NotRequired, TypedDict

# Representa los distintos tipos de mensaje del historial.
from langchain_core.messages import AnyMessage

# Incorpora mensajes nuevos sin reemplazar los anteriores.
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    """Describe los datos que reciben y actualizan los nodos del grafo."""

    messages: Annotated[list[AnyMessage], add_messages] # Conserva el historial de mensajes.
    errors: Annotated[list[str], operator.add] # Acumula los errores devueltos durante la conversación.
    category: str # Guarda la categoría más reciente de la solicitud.
    employee_id: str # Identifica al usuario seleccionado.
    profile: dict # Guarda el perfil cargado o actualizado durante el turno de la conversación.
    authorized: bool # Conserva la autorización más reciente sobre una consulta de ticket.
    request_id: NotRequired[str] # Identifica una operación concretaa para reconocer sus reintentos.