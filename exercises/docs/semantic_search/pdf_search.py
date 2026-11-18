"""Indexación y recuperación de fragmentos de un PDF."""

from pathlib import Path

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from .chunk import split_pages
from .pdf_loader import get_pdf


def main() -> None:
    """Integra carga, fragmentación, indexación y recuperación."""
    pages = get_pdf()
    chunks = split_pages(pages)

    embeddings = DeterministicFakeEmbedding(size=8)
    vector_store = InMemoryVectorStore(embedding=embeddings)

    # Genera un vector por fragmento y guarda su información.
    document_ids = vector_store.add_documents(documents=chunks)

    print("Páginas cargadas:", len(pages))
    print("Fragmentos generados:", len(chunks))
    print("Fragmentos indexados:", len(document_ids))

    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwrgs={"k": 3}
    )

    query = " How many distribution centers does Nike have?"
    results = retriever.invoke(query)

    print("\nConsulta:", query)
    print("Fragmentos recuperados:", len(results))

    for position, document in enumerate(results, start=1):
        print(f"\nResultado: {position}")
        print("Archivo:", Path(document.metadata["source"]).name)
        print("Índice del fragmento:", document.metadata["page"])
        print("Inicio de la página:", document.metadata["start_index"])
        print("Contenido:")
        print(document.page_content)


if __name__ == '__main__':
    main()