"""Demuestra c+omo un checkpointer conserva dos turnos de una conversación."""

# Importa el tipo de mensaje que representa una entrada del usuario.
from langchain_core.messages import HumanMessage

# Importa el checkpointer que guarda estados en la memoria del proceso.
from langgraph.checkpoint.memory import InMemorySaver

# Importa el constructor del grafo que se está trabajando, que ahora acepra un checkpointer.
from .graph import build_graph


def main() -> None:
    """Ejecuta dos solicitudes que comparten el mismo thread_id"""

    # Crea el objeto que almacenará las versiones del estado.
    checkpointer = InMemorySaver()

    # Conecta ese almacenamiento al grafo para compilarlo.
    graph = build_graph(checkpointer=checkpointer)

    # Identifica la conversación que tendrá 2 turnos.
    alice_config = {"configurable": {"thread_id": "emp001-conversation-1"}}

    # Identifica otra conversación independiente.
    bob_config = {"configurable": {"thread_id": "emp002-conversation-1"}}

    # Inicia la conversación con todos los campos del estado.
    first = graph.invoke(
        {
            "messages": [HumanMessage(content="¿Cuántos días de vacaciones tengo?")],
            "errors": [],
            "category": "",
            "employee_id": "EMP-001",
            "profile": {},
            "authorized": False,
        },
        alice_config,
    )

    # Muestra el resultado del primer turno de EMP-001.
    print("EMP-001, Turno 1:", len(first["messages"]), first["category"])

    # Continúa la conversación de EMP-001 enviando solo el mensaje nuevo.
    second = graph.invoke(
        {"messages": [HumanMessage(content="Mi computadora no enciende.")]},
        alice_config,
    )

    # Muestra el resultado acumulado del segundo turno de EMP-001.
    print("EMP-001, Turno 2:", len(second["messages"]), second["category"])

    # Inicia la conversación de EMP-002 con su propio estado completo.
    bob_result = graph.invoke(
        {
            "messages": [HumanMessage(content="Mi computadora no enciende.")],
            "errors": [],
            "category": "",
            "employee_id": "EMP-002",
            "profile": {},
            "authorized": False,
        },
        bob_config,
    )

    # Muestra cuántos mensajes contiene la conversación de EMP-002
    print("EMP-002, Turno 1:", len(bob_result["messages"]), bob_result["category"])

    # Recupera el último snapshot de la conversación de EMP-001
    alice_snapshot = graph.get_state(alice_config)

    # Recupera el último snapshot de la conversación de EMP-002
    bob_snapshot = graph.get_state(bob_config)

    # Compara los mensajes conservados en ambas conversaciones.
    print("Historial de EMP-001:", len(alice_snapshot.values["messages"]))
    print("Historial de EMP-002:", len(bob_snapshot.values["messages"]))

    # Comprueba que cada conversación conserva su employee_id.
    print("Empleado en conversación 1:", alice_snapshot.values["employee_id"])
    print("Empleado de conversación 2:", bob_snapshot.values["employee_id"])


# Evita que la demostración se ejecute al importar este módulo.
if __name__ == "__main__":
    main()
