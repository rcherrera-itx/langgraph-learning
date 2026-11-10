"""Define las reglas de accesso a los tickets simulados."""

from langchain_core.tools import tool

TICKET_ACCESS: dict[str, set[str]] = {
    "INC-4471": {"EMP-001"}
}

TICKET_STATUS: dict[str, str] = {
    "INC-4471": "Abierto; asignado al equipo de redes."
}


@tool
def lookup_ticket(ticket_id: str) -> str:
    """Consulta el estado de un ticket previamente autorizado."""

    print("Ejecutando lookup_ticket.")
    return TICKET_STATUS[ticket_id]


def can_read_ticket(employee_id: str, ticket_id: str) -> bool:
    """Comprueba si un empleado puede leer un ticket concreto."""

    allowed = TICKET_ACCESS.get(ticket_id, set())
    return employee_id in allowed


def authorize_ticket_call(employee_id: str, tool_call: dict) -> bool:
    """Valida una solicitud del modelo antes de permitir la consulta."""

    if tool_call.get("name") != "lookup_ticket":
        return False

    args = tool_call.get("args")

    if not isinstance(args, dict):
        return False

    ticket_id = args.get("ticket_id")

    if not isinstance(ticket_id, str):
        return False

    return can_read_ticket(employee_id, ticket_id)


def authorize_ticket_requests(employee_id: str, tool_calls: list[dict]) -> bool:
    """Autoriza un turno que contiene una sola consulta del ticket."""

    if len(tool_calls) != 1:
        return False

    return authorize_ticket_call(employee_id, tool_calls[0])