"""Define datos simulados, permisos y acciones de la mesa de ayuda."""

# Cierra la conexión SQLite cuando termina la operación.
from contextlib import closing

# Registra restablecimientos con una clave única que sobrevive a reinicios.
import sqlite3

# Convierte una función en herramienta para el ToolNode de tickets.
from langchain_core.tools import tool

# Comparte con el chatbot la ubicación de sus archivos persistentes.
from .persistence import DATA_DIR

# Define qué empleados pueden consultar cada ticket de la simulación.
TICKET_ACCESS: dict[str, set[str]] = {"INC-4471": {"EMP-001"}}

# Guarda el resultado que devuelve la consulta de cada ticket.
TICKET_STATUS: dict[str, str] = {"INC-4471": "Abierto; asignado al equipo de redes."}

# Define los empleados a quienes puede aplicarse la acción simulada.
SUPPORTED_EMPLOYEES = {"EMP-001", "EMP-002"}


@tool
def lookup_ticket(ticket_id: str) -> str:
    """Consulta el estado de un ticket previamente autorizado."""

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


def reset_password(employee_id: str, request_id: str) -> str:
    """Realiza una sola vez cada restablecimiento simulado."""

    # Comprueba que la acción se dirija a un empleado de la simulación.
    if not isinstance(employee_id, str) or employee_id not in SUPPORTED_EMPLOYEES:
        raise ValueError("Empleado no válido para el restablecimiento.")

    # Exige una clave que permita reconocer la misma solicitud en un reintento.
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("El restablecimiento requiere un request_id válido.")

    # Prepara la misma carpeta de datos usadoa para las demás persistencias.
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Separa el registro de acciones del historial y de los perfiles.
    database_path = DATA_DIR / "reset_operations.sqlite"

    # En esta simulación, registrar este resultado constituye la acción.
    result = f"Restablecimiento simulado para {employee_id}"

    with closing(sqlite3.connect(str(database_path), timeout=30)) as connection:
        # Confirma la nueva operación al salir o revierte la escritura si falla.
        with connection:
            # La pareja empleado/solicitud identifica una única acción.
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reset_operations(
                    employee_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    result TEXT NOT NULL,
                    PRIMARY KEY (employee_id, request_id)
                )
                """
            )

            # La clave primaria impide registrar dos veces la misma acción.
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO reset_operations
                    (employee_id, request_id, result)
                VALUES (?, ?, ?)
                """,
                (employee_id, request_id, result),
            )

            # Distingue la primera ejecución de un reintento de la misma clave.
            was_created = cursor.rowcount == 1

            # Recupera el resultado registrado, sea nuevo o anterior.
            row = connection.execute(
                """
                SELECT result FROM reset_operations
                WHERE employee_id = ? AND request_id = ?
                """,
                (employee_id, request_id)
            ).fetchone()

    # Informa únicamente cuando se añadió una operación nueva a SQLite.
    if was_created:
        print("Ejecutando reset_password.")

    # El registro siempre existe: esta operación la cre+o o lo encontró.
    return row[0]
