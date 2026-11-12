"""Define los nodos del chatbot y sus decisión de ruta."""

# Describe el tipo de función que crea 'make_it_agent'.
from collections.abc import Callable

# Limita las claves de ruta esperadas para facilitar su revisión.
from typing import Literal

# representa respuestas del asistente y resultados de herramientas.
from langchain_core.messages import AIMessage, ToolMessage

# Importa la política de accesso definida por la aplicación.
from .services import authorize_ticket_requests

# Importa el modelo simulado que redacta las respuestas de IT.
from .simulated_model import SimulatedModel

# Importa los campos compartidos durante la ejecución del grafo.
from .state import ConversationState


def classify(state: ConversationState) -> dict:
    """Clasifica la solicitud más reciente del usuario."""

    # Lee el último mensaje, que al comenzar este recorrido es la nuva solicitud.
    text = str(state["messages"][-1].content).casefold()

    # Dirige una solicitud de contraseña a IT para su revisión posterior.
    if "restablec" in text and "contraseña" in text:
        return {"category": "it"}

    # Dirige las preguntas sobre vacaciones a Recursos Humanos.
    if "vacaciones" in text:
        return {"category": "hr"}

    # Dirige tickets, computadoras y laptops al especialista de IT.
    if "computadora" in text or "ticket" in text or "laptop" in text:
        return {"category": "it"}

    # Dirige las demás solicitudes a atención general.
    return {"category": "general"}


def route_by_category(state: ConversationState) -> Literal["hr", "it", "general"]:
    """Selecciona la ruta correspondiente a la categoría del estado."""

    # Envía las solicitudes de vacaciones al nodo de Recursos Humanos.
    if state["category"] == "hr":
        return "hr"

    # Envía las solicitudes técnicas al nodo de IT.
    if state["category"] == "it":
        return "it"

    # Utiliza la ruta general para las categorías restantes.
    return "general"


def make_specialist(reply: str) -> Callable[[ConversationState], dict]:
    """Crea un nodo que devuelve la respuesta simulada indicada."""

    def specialist(state: ConversationState) -> dict:
        """Añade una respuesta del especialista al historial."""

        # Devuelve una lista para que 'add_messages' incorpore el mensaje.
        return {"messages": [AIMessage(content=reply)]}

    # Entrega la función creada para registrarla como nodo del grafo.
    return specialist


def make_it_agent(model: SimulatedModel) -> Callable[[ConversationState], dict]:
    """Crea el nodo de TI utilizando el modelo simulado recibido."""

    def it_agent(state: ConversationState) -> dict:
        """Entrega al modelo el historial y el perfil del empleado."""

        # El perfil ya fue cargado al estado por 'load_profile'.
        response = model.invoke(state["messages"], state["profile"])

        # Devuelve la respuesta o solicitud de herramienta como actualización.
        return {"messages": [response]}

    # Entrega la función creada oara registrarla como nodo del grafo.
    return it_agent


def route_after_it(state: ConversationState) -> Literal["authorize", "review_reset" ,"finish"]:
    """Decide si IT pidió una herramienta o terminó de responder."""

    # Consulta el mensaje que acaba de producir el modelo.
    last_message = state["messages"][-1]

    # Una solicitud de herramienta necesita un paso adicional.
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        # Envía el restablecimiento a la revisión humana.
        # 'approval.py' validará la estructura completa de esa solicitud.
        if last_message.tool_calls[0].get("name") == "reset_password":
            return "review_reset"

        # Envía la consulta de ticket a la política de autorizaión.
        # El servicio validará la llamada antes de permitir 'lookup_ticket'
        return "authorize"

    # Termina cuando el modelo ya devolvió una respuesta normal.
    return "finish"


def authorize_ticket(state: ConversationState) -> dict:
    """Obtiene de la aplicación la decisión sobre la consulta solicitada."""

    # recupera el AIMessage que contiene la solicitud de herramienta.
    request = state["messages"][-1]

    # Deja la validación de argumentos y permisos a la política de la aplicación.
    allowed = authorize_ticket_requests(state["employee_id"], request.tool_calls)

    # Entrega la decisión para que LangGraph la incorpore al estado.
    return {"authorized": allowed}


def route_after_authorization(state: ConversationState) -> Literal["allowed", "denied"]:
    """Selecciona la ruta de ejecución o denegación."""

    # Permite llegar a ToolNode únicamente cuando se concedió el accesso.
    if state["authorized"]:
        return "allowed"

    # Envía la solicitud rechazada al nodo que comunicará la denegación.
    return "denied"


def deny_ticket(state: ConversationState) -> dict:
    """Cierra la llamada rechazada sin ejecutar 'lookup_ticket'."""

    # Recupera la solicitud rechazada para identificar su 'tool_call_id'.
    request = state["messages"][-1]

    # Relaciona el resultado de denegación con la llamda original.
    call_id = request.tool_calls[0]["id"]

    # Crea un resultado de denegación que el modelo podrá interpretar.
    denial = ToolMessage(
        content="DENIED: No tienes permisos para consultar este ticket.",
        tool_call_id=call_id,
    )

    # Añade el resultado al historial y registra el error en el estado.
    return {"messages": [denial], "errors": ["Consulta de ticket denegada."]}