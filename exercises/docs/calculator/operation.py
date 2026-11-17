"""Operaciones que utilizarán las herramientas de la calculadora."""


def validate_number(value: object) -> None:
    """Exige un número entero o decimal; rechaza booleanos."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("Se esperaba un número entero o decimal.")


def add(a: float, b: float) -> float:
    """Devuelve la suma de dos números."""
    validate_number(a)
    validate_number(b)
    return a + b


def multiply(a: float, b: float) -> float:
    """Devuelve el producto de dos números."""
    validate_number(a)
    validate_number(b)
    return a * b


def divide(a: float, b: float) -> float:
    """Devuelve el cociente de dos números."""
    validate_number(a)
    validate_number(b)

    if b == 0:
        raise ValueError("El divisor no puede ser cero.")

    return a / b


def main() -> None:
    """Ejecuta comprobaciones manuales de las operaciones."""
    print("Suma:", add(8, 2))
    print("Multiplicación:", multiply(8, 2))
    print("División:", divide(8, 2))

    try:
        print("División entre cero:", divide(8, 0))
    except ValueError as error:
        print("Operación rechazada:", error)

    try:
        print(add("8", "2"))
    except TypeError as error:
        print("Argumentos rechazados:", error)

    try:
        print(divide("8", 2))
    except TypeError as error:
        print("Argumentos rechazados:", error)

    try:
        print(multiply(8, "2"))
    except TypeError as error:
        print("Argumentos rechazados:", error)


if __name__ == "__main__":
    main()
