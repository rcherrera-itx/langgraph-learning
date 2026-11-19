"""Indexación y recuperación de fragmentos de un PDF."""

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.runnables import chain
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from .chunk import split_pages
from .pdf_loader import get_pdf


def main() -> None:
    """Integra carga, fragmentación, indexación y recuperación."""
    pages = get_pdf()
    chunks = split_pages(pages)

    print("Cargando modelo local...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_store = InMemoryVectorStore(embedding=embeddings)

    # Genera un vector por fragmento y guarda su información.
    document_ids = vector_store.add_documents(documents=chunks)

    print("Páginas cargadas:", len(pages))
    print("Fragmentos generados:", len(chunks))
    print("Fragmentos indexados:", len(document_ids))

    @chain
    def retriever(query: str) -> list[Document]:
        """recupera el fragmento más imilar a la consulta."""
        return vector_store.similarity_search(query, k=1)
    

    queries = [
        "How many distribution centers does Nike have?",
        "When was Nike incorporated?"
    ]
    
    results = retriever.batch(queries)

    print("\nConsultas procesadas:", len(queries))
    print("Fragmentos recuperados:", len(results))

    for query, documents in zip(queries, results):
        print("Consulta:", query)
        print("Fragmentos recuperados:", len(documents))

        for document in documents:
            print("Archivo:", Path(document.metadata["source"]).name)
            print("Índice del página:", document.metadata["page"])
            print("Contenido:")
            print(document.page_content)


if __name__ == "__main__":
    main()
