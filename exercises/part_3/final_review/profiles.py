"""Carga y guarda perfiles de usuarios para el chatbbot simulado."""

# Identifica los mensajes escritos por el usuario.
from langchain_core.messages import HumanMessage

# Permite accedder al store asociado al grafo.
from langgraph.runtime import Runtime

# Describe los campos del estado que reciben los nodos.
from .state import ConversationState


def profile_namespace(employee_id: str) -> tuple[str, str]:
    """Construye el espacio del store correspondiente a un empleado."""

    # Utiliza la misma dirección para guardar y recuperar su perfil.
    return ("employee_profiles", employee_id)


def extract_laptop_model(content: str) -> str | None:
    """Extrae un modelo de la fase admitida por esta simluación."""

    # Define el comienzo de la frase que registra una laptop.
    prefix = "mi laptop es una "

    # Comprueba la frase sin distinguir mayúsculas de minúsculas.
    if not content.casefold().startswith(prefix):
        return None

    # Obtiene el texto posterior al prefijo y elimina espacios y el punto final.
    model = content[len(prefix) :].strip().rstrip(".").strip()

    # Rechaza un modelo vacío o demasiado largo antes de almacenarlo.
    if not model or len(model) > 80:
        return None

    # Devuelve el modelo validado a quien solicitó el registro.
    return model


def load_profile(state: ConversationState, runtime: Runtime) -> dict:
    """Carga el perfil del empleado desde el store cuando está disponible."""

    # Conserva el estado actual si el grafo no tiene un store asociado.
    if runtime.store is None:
        return {}

    # Obtiene el espacio correspondiente al empleado del estado.
    namespace = profile_namespace(state["employee_id"])

    # Busca el perfil guardado bajo la clave estable "profile".
    item = runtime.store.get(namespace, "profile")

    # Si no existe un perfil guardado, deja un diccionario vacío en el estado.
    if item is None:
        return {"profile": {}}

    # Devuelve el perfil para que LangGraph lo incorpore al estado.
    return {"profile": dict(item.value)}


def save_profile(state: ConversationState, runtime: Runtime) -> dict:
    """Guarda una laptop informada por el empleado y actualiza su estado."""

    # Sin store no puede confirmarse ni realizarse el guardado.
    if runtime.store is None:
        return {}

    # Examina el mensaje nuevo que acaba de recibir el grafo.
    last_message = state["messages"][-1]

    # Procesa únicamente entradas escritas por el empleado.
    if not isinstance(last_message, HumanMessage):
        return {}

    # Requiere texto para poder interpretar la frase de registro.
    if not isinstance(last_message.content, str):
        return {}

    # Delega la extracción y validación a una función de la aplicación.
    laptop_model = extract_laptop_model(last_message.content)

    # Deja intacto el perifl si la entrada no informa un modelo válido.
    if laptop_model is None:
        return {}

    # Conserva otros datos del perfil y actualiza el modelo de laptop.
    updated_profile = {**state["profile"], "laptop_model": laptop_model}

    # Selecciona el mismo espacio que utiliza 'load_profile' al leer.
    namespace = profile_namespace(state["employee_id"])

    # Guarda el perfil para que otras conversaciones puedan recuperarlo.
    runtime.store.put(namespace, "profile", updated_profile)

    # Actualiza también el estado de la conversación actual.
    return {"profile": updated_profile}
