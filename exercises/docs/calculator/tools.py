"""Herramientas de la calculadora con validación de argumentos."""

from langchain.tools import tool
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .operation import add, divide, multiply


class BinaryOperands(BaseModel):
    """Argumentos de una operación con dos números."""

    model_config = ConfigDict(strict=True, extra="forbid")

    a: int | float = Field(description="Primer número de la operación.")
    b: int | float = Field(description="Segundo número de la operación.")


@tool("add", args_schema=BinaryOperands)
def add_tool(a: int | float, b: int | float) -> float:
    """Suma dos números enteros o decimales."""
    return add(a, b)


@tool("divide", args_schema=BinaryOperands)
def divide_tool(a: int | float, b: int | float):
    """Divide dos números enteros o decimales."""
    return divide(a, b)


@tool("multiply", args_schema=BinaryOperands)
def multiply_tool(a: int | float, b: int | float):
    """Multiplica dos números enteros o decimales."""
    return multiply(a, b)


def main() -> None:
    """Comprueba la herramienta sin utilizar un modelo."""
    print("Nombre:", add_tool.name)
    print("Descripción:", add_tool.description)
    print("Resultado add:", add(8, 2))
    print("Resultado Tool:", add_tool.invoke({"a": 8, "b": 2}))

    try:
        add_tool.invoke({"a": "8", "b": 2})
    except ValidationError as error:
        print("Argumentos rechazados:", error)

    print("Producto:", multiply_tool.invoke({"a": 8, "b": 2}))
    print("Cociente:", divide_tool.invoke({"a": 8, "b": 2}))

    try:
        divide_tool.invoke({"a": 8, "b": 0})
    except ValueError as error:
        print("División rechazada:", error)


if __name__ == '__main__':
    main()