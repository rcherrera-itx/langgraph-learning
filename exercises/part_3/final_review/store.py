"""Comprueba que un perfil puede leerse desde distintas conversaciones."""

# Representa la entrada enviada al grafo por un usuairo.
from langchain_core.messages import HumanMessage

# Guarda los estados de las conversaciones durante este proceso.
from langgraph.checkpoint.memory import InMemorySaver

# Guarda perfiles accessibles desde diferentes conversaciones.
from langgraph.store.memory import InMemoryStore

# Construye el grafo con los almacenamientos proporcionados.
from .graph import build_graph

# Describe los campos que recibe el grafo al iniciar una conversación.
from .state import ConversationState


def initial_state(employee_id: str) -> ConversationState:
    """Crea el estado inicial de una conversación para un empleado."""

    # Proporciona todos los campos que utiliza el tutorial.
    return {
        "messages": [HumanMessage(content="Hola, necesito orientación.")],
        "errors": [],
        "category": "",
        "employee_id": employee_id,
        "profile": {},
        "authorized": False,
    }


def main() -> None:
    """Compara perfiles recuperados desde 3 conversaciones."""

    # Crea el almacenamiento de estados separados por thread_id
    checkpointer = InMemorySaver()

    # Crea el almacenamiento de perfiles separados por empleado.
    store = InMemoryStore()

    # Guarda el perfil de EMP-001 en el espacio que leerá 'load_profile'
    store.put(
        ("employee_profiles", "EMP-001"), "profile", {"laptop_model": "X1 Carbon"}
    )

    # Compila un grafo que comparte ambos almacenamientos.
    graph = build_graph(checkpointer=checkpointer, store=store)

    # Define la primera conversación de EMP-001
    alice_first_config = {"configurable": {"thread_id": "emp001-store-1"}}

    # Define la segunda conversación de EMP-001.
    alice_second_config = {"configurable": {"thread_id": "emp001-store-2"}}

    # Define una conversación independiente de EMP-002
    bob_config = {"configurable": {"thread_id": "emp002-store-1"}}

    # Ejecuta la primera conversación y carga el perfil de EMP-001.
    alice_first = graph.invoke(initial_state("EMP-001"), alice_first_config)

    # Ejecuta la primera conversación y carga el perfil de EMP-001.
    alice_second = graph.invoke(initial_state("EMP-001"), alice_second_config)

    # Ejecuta una conversación de un empleado sin perfil guardado.
    bob = graph.invoke(initial_state("EMP-002"), bob_config)

    # Muestra el perfil cargado en la primera conversación de EMP-001.
    print("Perfil de EMP-001, conversación 1:", alice_first["profile"])

    # Muestra el perfil cargado en la segunda conversación de EMP-001.
    print("Perfil de EMP-001, conversación 2:", alice_second["profile"])

    # Muestra el perfil cargado para EMP-002.
    print("Perfil de EMP-002:", bob["profile"])

    # Muestra que cada conversación comenzó con su propio historial.
    print(
        "Mensajes por conversación:",
        len(alice_first["messages"]),
        len(alice_second["messages"]),
        len(bob["messages"])
    )


if __name__ == '__main__':
    main()