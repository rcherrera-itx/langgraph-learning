"""Define el nodo que carga un perfil compartido entre conversaciones."""

# Permite que LangGraph proporcione al nodo el store del grafo.
from langgraph.runtime import Runtime

# Describe los campos del estado que recibe y actualiza el nodo.
from .state import ConversationState


def load_profile(state: ConversationState, runtime: Runtime) -> dict:
    """Carga del store el perfil correspondiente al empleado del estado."""

    # Si el grafo se compiló sin store, no modifica el perfil existente.
    if runtime.store is None:
        return {}

    # Agrupa los perfiles por empleado dentro del store.
    namespace = ("employee_profiles", state["employee_id"])

    # Busca el registro identificado como "profile" en ese espacio.
    item = runtime.store.get(namespace, "profile")

    # Si no existe un perfil guardado, deja un diccionario vacío en el estado.
    if item is None:
        return {"profile": {}}

    # Copia los datos recuperados al campo 'profile' del estado del grafo.
    return {"profile": dict(item.value)}