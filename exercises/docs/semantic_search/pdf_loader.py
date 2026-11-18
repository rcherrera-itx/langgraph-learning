"""Lectura local de un PDF y conversión de sus páginas a documentos."""

from pathlib import Path

from pypdf import PdfReader

from langchain_core.documents import Document


def load_pdf_pages(file_path: Path) -> list[Document]:
    """Extrae el texto de cada página y conserva su origen."""
    reader = PdfReader(str(file_path))

    return [
        Document(
            page_content=page.extract_text() or "",
            metadata={
                "source": str(file_path),
                "page": page_index
            },
        )
        for page_index, page in enumerate(reader.pages)
    ]


def main() -> None:
    """Muestra una página para comprobar la extracción."""
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "nke-10k-2023.pdf"
    )

    documents = load_pdf_pages(file_path)

    print("Archivo:", file_path.name)
    print("Páginas cargadas:", len(documents))

    if documents:
        first_document = documents[0]

        print("\nÍndice de página:", first_document.metadata["page"])
        print("Origen:", first_document.metadata["source"])
        print("Caracteres extraídos:", len(first_document.page_content))
        print("\nPrimeros 500 caracteres:")
        print(first_document.page_content[:500])


if __name__ == '__main__':
    main()