"""Abre el almacenamiento local persistente para conversaciones y perfiles."""

# Permite mantener abiertas ambas conexiones durante la vida del chatbot.
# Describe el tipo de valor que entrega el administrador de contexto.
from collections.abc import Iterator
from contextlib import contextmanager

# Construye rutas independientes del directorio desde donde se ejecua Python.
from pathlib import Path

# Guarda los estados y las interrupciones de cada 'thread_id' en SQLite.
from langgraph.checkpoint.sqlite import SqliteSaver

# Guarda perfiles que pueden consultarse desde distintos 'thread_id'
from langgraph.store.sqlite import SqliteStore

# Coloca los archivos de datos junto a los módulos del chatbot.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@contextmanager
def open_storage() -> Iterator[tuple[SqliteSaver, SqliteStore]]:
    """Abre los dos almacenes y cierra sus conexiones al salir del bloque."""

    # Crea eñ directorio la primera vez que se ejecuta el chatbot.
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Mantiene estados y perfiles en archivos distintos para distinguir su función.
    checkpoints_path = DATA_DIR / "checkpoints.sqlite"
    profiles_path = DATA_DIR / "profiles.sqlite"

    # Conserva ambas conexiones abiertas mientras se ejecuta el bloque 'with'
    with (
        SqliteSaver.from_conn_string(str(checkpoints_path)) as checkpointer,
        SqliteStore.from_conn_string(str(profiles_path)) as store,
        ):
        
        # Prepara las tablas del store antes de guardar o recuperar perfiles.
        store.setup()

        # El checkpointer prepara sus tablas automáticamente al primer uso.
        yield checkpointer, store
