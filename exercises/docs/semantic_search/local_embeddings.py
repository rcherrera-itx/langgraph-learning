"""Primera búsqueda con un modelo local de embeddings."""

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


def main() -> None:
    """Busca entre textos breves utilizando embeddings reales."""
    print("Cargando modelo local...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    documents = [
        Document(
            page_content="Employees request vacation through the HR portal.",
            metadata={"source": "hr_manual"},
        ),
        Document(
            page_content="Reset your password using the account recovery page.",
            metadata={"source": "support_manual"},
        ),
        Document(
            page_content="Travel expenses require reciepts.",
            metadata={"source": "support_manual"},
        ),
    ]

    query = "How can I ask for time off?"

    query_vector = embeddings.embed_query(query)
    print("Dimensiones:", len(query_vector))

    vector_store = InMemoryVectorStore(embedding=embeddings)
    vector_store.add_documents(documents=documents)

    results = vector_store.similarity_search_with_score(query=query, k=3)

    print("\nConsulta:", query)

    for document, score in results:
        print(f"\nSimilitud: {score:.4f}")
        print("Contenido:", document.page_content)
        print("Origen:", document.metadata["source"])


if __name__ == "__main__":
    main()
