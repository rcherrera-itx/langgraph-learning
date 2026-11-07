"""Define el esquema del estado compartido por el grafo."""

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    """Define los datos que comparten los nodos del grafo."""

    messages: Annotated[list[AnyMessage], add_messages] # Conserva el historial
    errors: Annotated[list[str], operator.add] # Acumula los errores
    category: str # Guarda la categoría más reciente.
    employee_id: str # Identifica al empleado
    profile: dict # Guarda el perfil cargado para esta ejecución.