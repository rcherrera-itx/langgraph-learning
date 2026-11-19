"""Indexación y recuperación de fragmentos de un PDF."""

from pathlib import Path

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

    query = "How many distribution centers does Nike have?"
    query_vector = embeddings.embed_query(query)
    results = vector_store.similarity_search_by_vector(embedding=query_vector, k= 3)

    print("\nConsulta:", query)
    print("Fragmentos recuperados:", len(results))
    print("Dimensiones del fragmento:", query_vector)

    if not results:
        print("No se encontraron fragmentos para tu búsqueda.")

    for position, document in enumerate(results, start=1):
        print(f"\nResultado: {position}")
        print("Archivo:", Path(document.metadata["source"]).name)
        print("Índice del página:", document.metadata["page"])
        print("Inicio del fragmento en la página:", document.metadata["start_index"])
        print("Contenido:")
        print(document.page_content)


if __name__ == '__main__':
    main()