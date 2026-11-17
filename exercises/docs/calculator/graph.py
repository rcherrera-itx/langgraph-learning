"""Calculadora con LangGraph y respuestas simuladas."""

from typing import Literal

from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from .tools import add_tool, divide_tool, multiply_tool


def simulated_model(state: MessagesState) -> dict:
    """Simula una solicitud de suma y su respuesta posterior."""
    last_message = state["messages"][-1]

    # Después de ejecutar la herramienta, produce la respuesta final.
    if isinstance(last_message, ToolMessage):
        return {
            "messages": [AIMessage(content=f"El resultado es {last_message.content}.")]
        }

    # Reconoce que se pide una suma y prepara la llamada de la herramienta oara ejecutar la suma.
    if isinstance(last_message, HumanMessage) and last_message.content == "Suma 8 y 2.":
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "add",
                            "args": {"a": 8, "b": 2},
                            "id": "call_add_001",
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }

    # Reconoce que se pide una multiplicación y prepara la llamada de la herramienta oara ejecutar la multiplicación.
    if (
        isinstance(last_message, HumanMessage)
        and last_message.content == "Multiplica 8 y 2."
    ):
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "multiply",
                            "args": {"a": 8, "b": 2},
                            "id": "call_multiply_001",
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }

    # Reconoce que se pide una división y prepara la llamada de la herramienta oara ejecutar la división.
    if isinstance(last_message, HumanMessage) and last_message.content == "Divide 8 y 2.":
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "divide",
                            "args": {"a": 8, "b": 2},
                            "id": "call_divide_001",
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }

    return {
        "messages": [AIMessage(content="Esta simulación solo reconoce: Suma 8 y 2.")]
    }


def route_after_model(state: MessagesState) -> Literal["tools", "finish"]:
    """Decide si hay herramientas pendientes o debemos terminar."""
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "finish"


def build_graph():
    """Construye y compila el ciclo de la calculadora."""
    builder = StateGraph(MessagesState)

    builder.add_node("model", simulated_model)
    builder.add_node(
        "tools",
        ToolNode([add_tool, multiply_tool, divide_tool], handle_tool_errors=False),
    )

    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model", route_after_model, {"tools": "tools", "finish": END}
    )
    builder.add_edge("tools", "model")

    return builder.compile()


def main() -> None:
    """Ejecuta un caso y muestra el historial resultante."""
    graph = build_graph()

    add_result = graph.invoke(
        {"messages": [HumanMessage(content="Suma 8 y 2.")]},
        config={"recursion_limit": 10},
    )

    print("Resultado de la suma:", add_result["messages"][-1].content)

    multiply_result = graph.invoke(
            {"messages": [HumanMessage(content="Multiplica 8 y 2.")]},
            config={"recursion_limit": 10},
        )
    
    print("Resultado de la multiplicación:", multiply_result["messages"][-1].content)

    divide_result = graph.invoke(
                {"messages": [HumanMessage(content="Divide 8 y 2.")]},
                config={"recursion_limit": 10},
            )
        
    print("Resultado de la división:", divide_result["messages"][-1].content)

    # for message in result["messages"]:
    #     message.pretty_print()


if __name__ == "__main__":
    main()
