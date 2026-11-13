"""Registra restablecimientos simulados sin repetir una solicitud.

Dependencias:
    sqlite3: Registra los restablecimientos para evitar duplicados.
    closing: Cierra la conexión SQLite cuando termina la operación.
    DATA_DIR: Indica dónde guardar los datos persistentes.
"""

import sqlite3
from contextlib import closing

from ..persistence.storage import DATA_DIR

# Define los empleados a quienes puede aplicarse la acción simulada.
SUPPORTED_EMPLOYEES = {"EMP-001", "EMP-002"}

def reset_password(employee_id: str, request_id: str) -> str:
    """Realiza una sola vez cada restablecimiento simulado."""

    # Comprueba que la acción se dirija a un empleado de la simulación.
    if not isinstance(employee_id, str) or employee_id not in SUPPORTED_EMPLOYEES:
        raise ValueError("Empleado no válido para el restablecimiento.")

    # Exige una clave que permita reconocer la misma solicitud en un reintento.
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("El restablecimiento requiere un request_id válido.")

    # Prepara la misma carpeta de datos usada para las demás persistencias.
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Separa el registro de acciones del historial y de los perfiles.
    database_path = DATA_DIR / "reset_operations.sqlite"

    # En esta simulación, registrar este resultado constituye la acción.
    result = f"Restablecimiento simulado para {employee_id}"

    with (closing(sqlite3.connect(str(database_path), timeout=30)) as connection, connection):
        # Confirma la nueva operación al salir o revierte la escritura si falla.
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
            (employee_id, request_id),
        ).fetchone()

    # Informa únicamente cuando se añadió una operación nueva a SQLite.
    if was_created:
        print("Ejecutando reset_password.")

    # El registro siempre existe: esta operación la creó o lo encontró.
    return row[0]