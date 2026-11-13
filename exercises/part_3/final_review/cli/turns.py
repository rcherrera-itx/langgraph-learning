"""Muestra el progreso de un turno y recoge decisiones de revisión."""

# Permite reanudar un grafo que solicitó una decisión humana.
from langgraph.types import Command

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