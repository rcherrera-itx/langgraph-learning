"""División de las páginas de un PDF en fragmentos."""

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .pdf_loader import get_pdf


def main() -> None:
    """Carga las páginas y muestra los primeros fragmentos."""
    pages = get_pdf()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True
    )

    chunks = splitter.split_documents(pages)

    print("Páginas cargadas:", len(pages))
    print("Fragmentos generados:", len(chunks))

    for position, chunk in enumerate(chunks[:3], start=1):
        print(f"\nFragmento {position}")
        print("Caracteres:", len(chunk.page_content))
        print("Índice de página:", chunk.metadata["page"])
        print("Inicio de la página:", chunk.metadata["start_index"])
        print("Origin:", chunk.metadata["source"])
        print("Contenido:")
        print(chunk.page_content)


if __name__ == '__main__':
    main()