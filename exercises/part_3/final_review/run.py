"""Ofrece una interfaz de consola para el chatbot de soporte simulado."""

# Genera un identificador distinto para cada conversación.
from uuid import uuid4

# Representa las preguntas escritas por el usuario.
from langchain_core.messages import HumanMessage

# Permite reanudar un grafo que solicitó una decisión humana.
from langgraph.types import Command

# Importa el constructor del grafo.
from .graph import build_graph

# Abre los almacenes SQLite durante toda la sesión de consola.
from .persistence import open_storage

# Define los usuario disponibles en esta simulación.
EMPLOYEES = {"EMP-001", "EMP-002"}

# Asocia cada nodo con un mensaje de progreso para la consola.
PROGRESS_LABELS = {
    "load_profile": "Perfil cargado.",
    "save_profile": "Perfil revisado.",
    "classify": "Solicitud clasificada.",
    "hr_agent": "Recursos Humanos procesó la solicitud.",
    "it_agent": "IT procesó un paso.",
    "general_agent": "Atención general procesó la solicitud.",
    "authorize_ticket": "Permiso de consulta evaluado.",
    "it_tools": "Consulta de ticket completada.",
    "deny_ticket": "Consulta de ticket denegada.",
    "approval_gate": "Decisión del revisor registrada.",
    "execute_reset": "Restablecimiento simulado completado."
}


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

        print("Escribe 'approve' or 'deny'.")


def stream_turn(graph, graph_input: dict | Command, config: dict) -> dict | None:
    """Muestra avances, atiende pausas y devuelve el estado final del turno."""

    # El primer recorrido recibe un mensaje nuevo o una decisión para renudar el hilo.
    current_input = graph_input

    # Permite reanudar una o más interrupciones del mismo turno.
    while True:
        # Guardará el estado completo más reciente de esta ejecución.
        final_state = None

        # Guardará una solicitud de revisión si el grafo se interrumpe.
        review_request = None

        # Solicita actualización por nodo y versiones completas del estado.
        for mode, chunk in graph.stream(
            current_input,
            config=config,
            stream_mode=["updates", "values"]
        ):
            # Una interrupción se entrega como un evento especial.
            if "__interrupt__" in chunk:
                # Recupera el contenido que 'approval_gate' envió al revisor.
                review_request = chunk["__interrupt__"][0].value
                continue

            if mode == "updates":
                # Un evento puede incluir más de un nodo.
                for node_name in chunk:
                    # Busca una explicaicón breve para mostrarla al usuario.
                    label = PROGRESS_LABELS.get(node_name, "Paso completado.")

                    # Muestra el avance sin imprimir el estado completo.
                    print(f"[{node_name}] {label}")

            # 'values' contiene el estado completo despúes de cada paso.
            elif mode == "values":

                # Conserva el más reciente para obtener la respuesta final.
                final_state = chunk

        if review_request is None:
            # Detecta una ejecución sin interrumpirse, entrega su estado final.
            if final_state is None:
                raise ValueError("El grafo no devolvió un estado final.")

            return final_state

        # Solicita la decisión correspondiente a la interrupción detectada.
        decision = read_review_decision(review_request)

        # Termina el turno si el revisor cerró la entrada sin decidir.
        if decision is None:
            return None

        # Reanuda el hilo existente con la decisión recibida.
        # El request_id ya está guardado en el estado de ese hilo.
        current_input = Command(resume=decision)


def run_chat(graph) -> None:
    """Atiende comandos y mensajes mientras los almacenes están abiertos."""

    # Selecciona el empleado que comenzará a usar la consola.
    employee_id = choose_employee()

    # Crea la primera conversación del empleado seleccionado.
    thread_id = create_thread_id(employee_id)

    # Indica que esa conversación aún no tiene estado inicial guardado.
    is_new_thread = True

    # Muestra el identificador recuperable y los comandos disponibles en esta versión.
    print(f"Conversación: {thread_id}")
    print("Comandos: /id, /new, /resume THREAD_ID, /switch EMP-001, /switch EMP-002, /quit")

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

        # Repite el identificador si el empleado desea guardarlo.
        if user_input.lower() == "/id":
            print(f"Conversación: {thread_id}")
            continue

        # Abre otra conversación del usuario activo.
        if user_input.lower() == "/new":
            thread_id = create_thread_id(employee_id)
            is_new_thread = True
            print(f"Nueva conversación: {thread_id}")
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
            print(f"Conversación iniciada para {employee_id}: {thread_id}")
            continue

        # Recupera un hilo conocido desde el checkpointer persistente.
        if user_input.lower().startswith("/resume"):

            # Exige el identificador completo mostrado por '/id' o '/new'
            parts = user_input.split()
            if len(parts) != 2 or parts[0].lower() != "/resume":
                print("Uso: /resume EMP-00X:identificador")
                continue

            # Impide seleccionar un hilo que pertenezca a otro empleado.
            candidate_id = parts[1]
            if not candidate_id.startswith(f"{employee_id}:"):
                print("La conversación no pertenece al empleado seleccionado.")
                continue

            # Consulta el estado guardado sin modificar la conversación activa.
            candidate_config = {"configurable": {"thread_id": candidate_id}}
            snapshot = graph.get_state(candidate_config)

            # Comprueba que el hilo exista y confirme su propietario en el estado.
            if not snapshot.values or snapshot.values.get("employee_id") != employee_id:
                print("No existe una conversación guardada con ese identificador.")
                continue

            # Un paso pendiente distinto de la aprobaci+on no se renuda a ciegas.
            if snapshot.next and not snapshot.interrupts:
                print("La conversación tiene un paso pendiente que requiere revisión.")
                continue

            # Selecciona el hilo recuperado y conserva su estado previo.
            thread_id = candidate_id
            is_new_thread = False
            print(f"Conversación recuperada: {thread_id}")
            print(f"Mensajes guardados: {len(snapshot.values['messages'])}")

            # Una aprobación pendiente conserva su solicitud en el checkpointer.
            if snapshot.interrupts:
                review_request = snapshot.interrupts[0].value
                decision = read_review_decision(review_request)

                # Al cerrar la entrada, el hilo seguirá pendiente en SQLite.
                if decision is None:
                    print("La revisión permanece pendiente. Sesión terminada.")
                    return

                # Reanuda exactamente el hilo y la solicitud interrumpidos.
                result = stream_turn(graph, Command(resume=decision), candidate_config)
                if result is None:
                    print("La revisión permanece pendiente. Sesión terminada.")
                    return

                # Presenta el resultado del turno que había quedado pausado.
                print(f"Asistente: {result['messages'][-1].content}")
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

        # Identifica esta solicitud concreta, incluso si pertenece a un hilo existente.
        graph_input["request_id"] = uuid4().hex

        # Selecciona el historial identificado por el 'thread_id' activo.
        config = {"configurable": {"thread_id": thread_id}}

        # recorre el grafo, muestra avances y atiende posibles revisiones.
        result = stream_turn(graph, graph_input, config)

        if result is None:
            print("La revisión permanece pendiente. Sesión terminada.")
            return

        # Marca que la conversación actual ya tiene estado en el checkpointer.
        is_new_thread = False

         # Obtiene el último mensaje, que contiene la respuesta final.
        final_message = result["messages"][-1]

        # Presenta la respuesta al usuario en la consola.
        print(f"Asistente: {final_message.content}")


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