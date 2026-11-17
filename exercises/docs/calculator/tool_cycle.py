"""Ejecuta una solicitud de herramienta simulada, sin API_KEY."""

from langchain.messages import AIMessage, HumanMessage, ToolMessage

from .tools import add_tool, divide_tool, multiply_tool


def main() -> None:
    """Recorre un ciclo de solicitud, ejecución y respuesta."""

    # Relaciona el nombre público con el objeto de herramienta.
    tools_by_name = {
        add_tool.name: add_tool,
        divide_tool.name: divide_tool,
        multiply_tool.name: multiply_tool,
    }

    user_message = HumanMessage(content="¿Cuánto es 8 más dos?")

    # Representa la solicitud que podría producir un modelo.
    request = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "add",
                "args": {"a": 8, "b": 2},
                "id": "call_calc_001",
                "type": "tool_call",
            }
        ],
    )

    # Este primer ejercicio procesa una sola solicitud.
    call = request.tool_calls[0]

    if call["name"] not in tools_by_name:
        raise ValueError(f"Herramienta desconocida: {call['name']}")

    selected_tool = tools_by_name[call["name"]]

    # Valida los argumentos y ejecuta la herramienta.
    result = selected_tool.invoke(call["args"])

    # Vincula el resultado con la solicitud concreta.
    tool_result = ToolMessage(content=str(result), tool_call_id=call["id"], name=call["name"])

    # Simula la respuesta posterior a recibir el resultado.
    final_response = AIMessage(content=f"El resultado es {tool_result.content}.")

    print("Usuario:", user_message.content)
    print("Heramienta solicitada:", call["name"])
    print("Argumentos:", call["args"])
    print("Resultado de herramienta:", tool_result.content)
    print("Solicitud asociada:", tool_result.tool_call_id)
    print("respuesta simulada:", final_response.content)


if __name__ == '__main__':
    main()
