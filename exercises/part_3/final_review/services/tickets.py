"""Define datos simulados, permisos y acciones de la mesa de ayuda."""

# Convierte la consulta de tickets en una herramienta.
from langchain_core.tools import tool

# Define qué empleados pueden consultar cada ticket de la simulación.
TICKET_ACCESS: dict[str, set[str]] = {"INC-4471": {"EMP-001"}}

# Guarda el resultado que devuelve la consulta de cada ticket.
TICKET_STATUS: dict[str, str] = {"INC-4471": "Abierto; asignado al equipo de redes."}

@tool
def lookup_ticket(ticket_id: str) -> str:
    """Devuelve el estado de un ticket; el grafo comprueba antes del permiso."""

    # Hace visible cuando se ejecuta realmente la herramienta.
    print("Ejecutando lookup_ticket.")

    # Devuelve el estado del ticket autorizado por la ruta anterior.
    return TICKET_STATUS[ticket_id]


def can_read_ticket(employee_id: str, ticket_id: str) -> bool:
    """Comprueba si un empleado puede leer un ticket concreto."""

    # Obtiene los empleados autorizados o un conjunto vacío si no hay registro.
    allowed = TICKET_ACCESS.get(ticket_id, set())

    # Acepta la consulta solo si el empleado pertenece a ese conjunto.
    return employee_id in allowed


def authorize_ticket_call(employee_id: str, tool_call: dict) -> bool:
    """Valida una solicitud del modelo antes de permitir la consulta."""

    # Rechaza una solicitud que no tenga la estructura esperada.
    if not isinstance(tool_call, dict):
        return False

    # Permite únicamente la herramienta prevista para esta ruta.
    if tool_call.get("name") != "lookup_ticket":
        return False

    # Obtiene los argumentos propuestos por el modelo simulado.
    args = tool_call.get("args")

    # Rechaza argumentos que no formen un diccionario.
    if not isinstance(args, dict):
        return False

    # Obtiene el identificador del ticket solicitado.
    ticket_id = args.get("ticket_id")

    # Rechaza un identificador ausente o de otro tipo.
    if not isinstance(ticket_id, str):
        return False

    # Deja la decisión de accesso a la política de la aplicación.
    return can_read_ticket(employee_id, ticket_id)


def authorize_ticket_requests(employee_id: str, tool_calls: list[dict]) -> bool:
    """Autoriza un turno que contiene una sola consulta del ticket."""

    # Esta ruta admite una sola llamada para poder resolverla por completo.
    if not isinstance(tool_calls, list) or len(tool_calls) != 1:
        return False

    # Valida esa llamada y permiso del usuario.
    return authorize_ticket_call(employee_id, tool_calls[0])