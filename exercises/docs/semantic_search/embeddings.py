"""Generación de embeddings simulados sin servicios externos."""

from langchain_core.embeddings import DeterministicFakeEmbedding

from .documents import build_documents


def main() -> None:
    """Convierte los textos en vectores e inspecciona su estructura."""
    documents = build_documents()

    # Cada vector tendrá ocho componentes numéricos.
    embeddings = DeterministicFakeEmbedding(size=8)

    # Extraemos únicamente el contenido texto.
    texts = [document.page_content for document in documents]

    # Generamos un vector por cada texto.
    document_vector = embeddings.embed_documents(texts)

    print("Cantidad de vectores:", len(document_vector))

    for position, vector in enumerate(document_vector, start=1):
        print(f"\nVector del documento: {position}")
        print("Dimensiones:", len(vector))
        print("Valores:", vector)

    # La consulta también debe convertirse en un vector.
    query = "¿Cómo puedo solicitar vacaciones?"
    query_vector = embeddings.embed_query(query)

    print("\nConsulta:", query)
    print("Dimensiones de la consulta:", len(query_vector))

    # Comprobamos la reproducibilidad del simulador.
    repeated_vector = embeddings.embed_query(query)

    print("Mismo texto produce el mismo vector:", query_vector == repeated_vector)


if __name__ == '__main__':
    main()