"""Gestiona la revisión humana de restablecimiento simulados."""

# Describe los posibles destinos del nodo de aprobación.
from typing import Literal

# Identifica la solicitud del modelo y comunica el resultado de la acción.
from langchain_core.messages import AIMessage, ToolMessage

# Permite pausar el grafo y elegir el siguiente nodo al reanudarlo.
from langgraph.types import Command, interrupt

# Ejecuta la acción simulada con protección frente a reintentos.
from .services import reset_password

# Describe los datos disponibles durante la conversación.
from .state import ConversationState


def get_reset_call(state: ConversationState) -> dict:
    """Valida y devuelve la solicitud de restablecimiento pendiente."""

    # La última respuesta del modelo debe solicitar la acción.
    message = state["messages"][-1]

    # Esta ruta admite exactamente una llamada a herramienta.
    if not isinstance(message, AIMessage) or len(message.tool_calls) != 1:
        raise ValueError("Se esperaba una sola solicitud de restablecimiento.")

    # Obtiene la llamada que produjo el modelo simulado.
    call = message.tool_calls[0]

    # Acepta únicamente la acción prevista y sin argumentos del modelo.
    # El empleado y el request_id proceden de nuestra aplicación.
    if call.get("name") != "reset_password" or call.get("args") != {}:
        raise ValueError("Solicitud de restablecimiento no válida.")

    # El identificador vinculará esta solicitud con su ToolMessage.
    call_id = call.get("id")

    if not isinstance(call_id, str) or not call_id.startswith("call_reset_"):
        raise ValueError("La solicitud no tiene un tool_call_id válido.")

    # Exige el identificador que 'run.py' creó para este mensaje del usuario.
    request_id = state.get("request_id")

    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("La solicitud no tiene un request_id válido.")

    # Entrega la llamada validada a los nodos de aprobación y ejecución.
    return call


def approval_gate(
    state: ConversationState,
) -> Command[Literal["execute_reset", "it_agent"]]:
    """Pausa el grafo y dirige la solicitud según la decisión humana."""

    # Valida la llamda antes de presentar una acción al revisor.
    call = get_reset_call(state)

    # Suspende el grafo y muestra los datos de la acción propuesta.
    # Al reanudar, la decisión proporcionada será el valor devuelto aquí.
    decision = interrupt(
        {
            "action": call["name"],
            "employee_id": state["employee_id"],
            "request_id": state["request_id"],
        }
    )

    # Solo una aprobación explícita permite ejecutar el restablecimiento.
    if decision == "approve":
        return Command(goto="execute_reset")

    # Rechaza cualquier valor distinto de las dos decisiones admitidas.
    if decision != "deny":
        raise ValueError("La decisión del revisor no es válida.")

    # Registra una denegación ligada a la llamada original del modelo.
    if decision != "deny":
        raise ValueError("La decisión del revisor no es válida.")

    # Registra una denegación ligada a la llamada original del modelo.
    denial = ToolMessage(
        content="DENIED: La acción fue denegada por el revisor.",
        tool_call_id=call["id"],
    )

    # Agrega la denegación al historial y pide a IT redactar la respuesta.
    return Command(
        update={
            "messages": [denial],
            "errors": ["Restablecimiento de contraseña denegado."],
        },
        goto="it_agent",
    )


def execute_reset(state: ConversationState) -> dict:
    """Ejecuta la acción aprobada y devuelve su resultado al historial."""

    # Vuelve a comprobar qué llamada se aprobó.
    call = get_reset_call(state)

    # Usa el empleado y la clave de operación definidos por la aplicación.
    # El servicio reconoce un reintento por esta misma pareja de valores.
    result = reset_password(
        employee_id=state["employee_id"], request_id=state["request_id"]
    )

    # Relaciona el resultado con el AIMessage que solicitó la acción.
    response = ToolMessage(content=result, tool_call_id=call["id"])

    # 'add_messages' incorporará este mensaje al historial del estado.
    return {"messages": [response]}
