"""Representar textos como documentos de LangChain."""

from langchain_core.documents import Document


def build_documents() -> list[Document]:
    """Construye docuemtnos de ejemplo con texto y metadatos."""

    return [
        Document(
            page_content="Para solicitar vacaciones, registra las fechas en el portal de Recursos Humanos.",
            metadata={"source": "manual_rrhh", "section": "vacaciones"},
        ),
        Document(
            page_content="Si olvidaste tu contraseña, utiliza la opción de recuperación en el portal de accesso.",
            metadata={"source": "manual_soporte", "section": "accesso"},
        ),
        Document(
            page_content="Los gastos de viaje deben incluir comprobantes y enviarse al área de administración.",
            metadata={"source": "manual_administracion", "section": "viaticos"},
        ),
    ]


def main() -> None:
    """Muestra el contenido y los metadatos de cada documento."""
    documents = build_documents()

    print("Cantidad de documentos:", len(documents))

    for position, document in enumerate(documents, start=1):
        print(f"\nDocumento: {position}")
        print("Contenido:", document.page_content)
        print("Origen:", document.metadata["source"])
        print("Sección:", document.metadata["section"])


if __name__ == '__main__':
    main()