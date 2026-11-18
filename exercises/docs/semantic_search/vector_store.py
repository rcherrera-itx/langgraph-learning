"""Almacén vectorial en memoria con embeddings simulados."""

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from .documents import build_documents


def main() -> None:
    """Almacena documentos y recupera resultados por similitud."""
    documents = build_documents()

    embeddings = DeterministicFakeEmbedding(size=8)
    vector_store = InMemoryVectorStore(embedding=embeddings)

    # El almacen genera los vectores y conserva los textos y metadatos.
    documents_ids = vector_store.add_documents(documents=documents)

    print("Documentos incorporados:", len(documents_ids))

    query = "¿Cómo puedo solicitar vacaciones?"

    # Recuperamos los dos documentos con mayor similitud numérica.
    results = vector_store.similarity_search_with_score(query=query, k=2)

    print("\nConsulta:", query)

    for position, (document, score) in enumerate(results, start=1):
        print(f"\nResultado {position}")
        print("Similitud:", f"{score:.4f}")
        print("Contenido:", document.page_content)
        print("Origen:", document.metadata["source"])
        print("Sección:", document.metadata["section"])

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )

    # Recibe la consulta y devuelve una lista de documentos.
    retrieved_documents = retriever.invoke(query)

    print("\nDocumentos obtenidos mediante el retriever.")

    for position, document in enumerate(retrieved_documents, start=1):
        print(f"\nDocumento {position}")
        print("Contenido:", document.page_content)
        print("Origen:", document.metadata["source"])


if __name__ == "__main__":
    main()