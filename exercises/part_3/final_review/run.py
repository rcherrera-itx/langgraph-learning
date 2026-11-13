"""Inicia el chatbot de soporte simulado."""

# Importa la sesion a ejecutarse para el chat.
from .cli.session import run_chat

# Importa el constructor del grafo.
from .graph.builder import build_graph

# Mantiene abiertos los almacenes SQLite durante toda la sesión.
from .persistence.storage import open_storage


def main() -> None:
    """Mantiene los almacenes abiertos hhasta que termina la consola."""

    # Cierra ambas conexiones incluso si se termina con '/quit' o 'Ctrl+C'.
    with open_storage() as (checkpointer, store):
        # El grafo usa el checkpointer por hilo y el store por empleado.
        graph = build_graph(checkpointer=checkpointer, store=store)

        # Atiende mensajes mientars el grafo puede acceder a sus almacenes.
        run_chat(graph)

    

# Inicia la interfaz únicamente al ejecutar este módulo.
if __name__ == "__main__":
    main()