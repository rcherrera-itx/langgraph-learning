"""Ofrece una interfaz de consola para el chatbot de soporte simulado."""

# Genera un identificador distinto para cada conversación.
from uuid import uuid4

# Representa las preguntas escritas por el usuario.
from langchain_core.messages import HumanMessage

# Conserva el estado de cada conversación durante esta ejecución.
from langgraph.checkpoint.memory import InMemorySaver

# Permite compartir perfiles entre conversaciones durante esta ejecución.
from langgraph.store.memory import InMemoryStore

# Permite reanudar un grafo que solicitó una decisión humana.
from langgraph.types import Command

# Importa el constructor del grafo.
from .graph import build_graph

# Define los usuario disponibles en esta simulación.
EMPLOYEES = {"EMP-001", "EMP-002"}


def create_thread_id(employee_id: str) -> str:
    """Crea un identificador nuevo para una conversación del empleado."""

    # Añade un valor único para que el empleado pueda abrir varias conversaciones.
    return f"{employee_id}:{uuid4().hex}"


def choose_employee() -> str:
    """Selecciona un empleado definido para esta simulación."""

    # repite la pregunta hasta recibir uno de los identificadores admitidos.
    while True:
        
        # Lee y normaliza el identificador escrito en la consola.
        employee_id = input("Empleado simulado (EMP-001 o EMP-002): ").strip().upper()

        # Acepta únicamente los empleados definidos en el ejericio.
        if employee_id in EMPLOYEES:
            return employee_id

        # Responde el por qué se solicita el identificador nuevamente.
        print("El usuario no está disponible en la simulación.")


def read_review_decision(request: object) -> str | None:
    """Muestra una acción pendiente y recoge la decisión del revisor."""

    # Presenta la solicitud que provocó la pausa del grafo.
    print("Solicitud de revisión:", request)

    # Solicita una decisión explícita antes de reanudar.
    while True:
        try:
            # Acepta las dos decisiones que entenderá el nodo de aprobación.
            decision = input("Revisor (approve/deny): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # Deja la acción sin ejecutar si se cierra la entrada.
            print()
            return None

        # Devuelve únicamente una decisión reconocida.
        if decision in {"approve", "deny"}:
            return decision

        print("Escribe approve or deny.")


def main() -> None:
    """Mantiene una conversación y envía cada mensaje nuevo al grafo."""

    # Crea el almacenamiento de los estados de las conversaciones.
    checkpointer = InMemorySaver()

    # Crea el almacenamiento de perfiles que utilizará 'load_profile'.
    store = InMemoryStore()

    # Construye el grafo una sola vez co ambos almacenamientos.
    graph = build_graph(checkpointer=checkpointer, store=store)

    # Selecciona el empleado que comenzará a usar la consola.
    employee_id = choose_employee()

    # Crea la primera conversación del empleado seleccionado.
    thread_id = create_thread_id(employee_id)

    # Indica que esa conversación aún no tiene estado inicial guardado.
    is_new_thread = True

    # Muestra los comandos disponibles en esta versión.
    print("Comandos: /new, /switch EMP-001, /switch EMP-002, /quit")

    # Recibe mensajes sucesivos sin reconstruir el grafo.
    while True:

        try:
            #Solicita una entrada e identifica al usuario activo.
            user_input = input(f"{employee_id}> ").strip()
        except (EOFError, KeyboardInterrupt):
            # Permite cerrar la consola sin mostrar un traceback.
            print("\nHasta luego.")
            break

        # Impide procesar un mensaje vacío.
        if not user_input:
            print("Escribe un mensaje o comando.")
            continue

        # Termina la sesión cuando el empleado lo solicita.
        if user_input.lower() == "/quit":
            print("Hasta luego.")
            break

        # Abre otra conversación del usuario activo.
        if user_input.lower() == "/new":
            thread_id = create_thread_id(employee_id)
            is_new_thread = True
            print("Nueva conversación iniciada.")
            continue

        # Permite simular la selección de otro empleado.
        if user_input.lower().startswith("/switch"):

            # Separa el comando del identificador de empleado.
            parts = user_input.split()

            # Comprueba la forma del comando y el usuario solicitado.
            if len(parts) != 2 or parts[1].upper() not in EMPLOYEES:
                print("Uso: /switch EMP-001 o /switch EMP-002")
                continue

            # Cambia al usuario indicado en la simulación.
            employee_id = parts[1].upper()

            # Inicia una conversación nueva para el empleado seleccionado.
            thread_id = create_thread_id(employee_id)
            is_new_thread = True
            print(f"Conversación iniciada para {employee_id}.")
            continue

        # Evita un comando no reconocido.
        if user_input.startswith("/"):
            print("Comando desconocido.")
            continue

        # Convierte el texto escrito en un mensaje de usuario.
        human_message = HumanMessage(content=user_input)

        # Envía todos los campos necesarios al iniciar una conversación.
        if is_new_thread:
            graph_input = {
                "messages": [human_message],
                "errors": [],
                "category": "",
                "employee_id": employee_id,
                "profile": {},
                "authorized": False,
            }
        else:
            # Añade un mensaje al estado guardado de esta conversación.
            # Reinicia la autorización antes de procesar una nueva solicitud.
            graph_input = {
                "messages": [human_message],
                "employee_id": employee_id,
                "authorized": False,
            }

        # Selecciona el historial identificado por el 'thread_id' activo.
        config = {"configurable": {"thread_id": thread_id}}

        # Ejecuta el grafo con el mensaje nuevo y el estado correspondiente.
        result = graph.invoke(graph_input, config=config)

        # Atiende una interrupción antes de mostrar una respuesta final.
        while "__interrupt__" in result:

            # Obtiene los datos que el nodo envió al revisor.
            request = result["__interrupt__"][0].value

            # Pide una decisión sobre esa solicitud concreta.
            decision = read_review_decision(request)

            # Sale in ejecutar la acción si no se recibió una decisión.
            if decision is None:
                print("La acción no se ejecutó. Sesión terminada.")
                return

            # Reanuda la misma conversación con la decisión del revisor.
            result = graph.invoke(Command(resume=decision), config=config)


        # Marca que la conversación actual ya tiene estado en el checkpointer.
        is_new_thread = False

         # Obtiene el último mensaje, que contiene la respuesta final.
        final_message = result["messages"][-1]

        # presenta la respuesta al usuario en la consola.
        print(f"Asistente: {final_message.content}")

# Inicia la interfaz únicamente al ejecutar este módulo.
if __name__ == "__main__":
    main()
