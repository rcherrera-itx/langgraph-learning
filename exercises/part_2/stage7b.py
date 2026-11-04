from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt


@tool
def reset_password(employee_id: str) -> str:
    """Simula el restablecimiento de la contraseña de un empleado"""
    print("Ejecutando herramienta simulada")
    return f"Restablecimiento simulado para {employee_id}"


@tool
def helpdesk_hours() -> str:
    """Consulta el horario público de la mesa de ayuda."""
    return "Horario: lunes a viernes, de 9:00 a 18:00"


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class SimulatedModel:
    def invoke(self, messages):
        last = messages[-1]

        if isinstance(last, ToolMessage):
            if last.content.startswith("DENIED:"):
                return AIMessage(
                    content="Solicitud denegada; no se restableció la contraseña."
                )

            return AIMessage(content=f"Resultado: {last.content}")

        ask_hours = "horario" in str(last.content).lower()
        tool_name = "helpdesk_hours" if ask_hours else "reset_password"

        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": tool_name,
                    "args": ({} if ask_hours else {"employee_id": "EMP-001"}),
                    "id": ("call_hours_001" if ask_hours else "call_reset_001"),
                }
            ],
        )


model = SimulatedModel()


def it_agent(state: HelpdeskState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


def route_after_agent(
    state: HelpdeskState,
) -> Literal["approval_gate", "tools", "__end__"]:
    calls = state["messages"][-1].tool_calls

    if not calls:
        return END

    name = calls[0]["name"]

    if name == "reset_password":
        return "approval_gate"
    if name == "helpdesk_hours":
        return "tools"

    raise ValueError(f"herramienta no contemplada: {name}")


def approval_gate(
    state: HelpdeskState,
) -> Command[Literal["tools", "it_agent"]]:
    call = state["messages"][-1].tool_calls[0]

    decision = interrupt({"action": call["name"], "args": call["args"]})

    if decision == "approve":
        return Command(goto="tools")

    return Command(
        goto="it_agent",
        update={
            "messages": [
                ToolMessage(
                    content="DENIED: La acción fue denegada por el revisor.",
                    tool_call_id=call["id"],
                )
            ]
        },
    )


builder = StateGraph(HelpdeskState)
builder.add_node("it_agent", it_agent)
builder.add_node("approval_gate", approval_gate)
builder.add_node("tools", ToolNode([reset_password, helpdesk_hours]))

builder.add_edge(START, "it_agent")
builder.add_conditional_edges(
    "it_agent",
    route_after_agent,
    {"approval_gate": "approval_gate", "tools": "tools", END: END},
)
builder.add_edge("tools", "it_agent")

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    for decision in ("deny", "approve"):
        config = {"configurable": {"thread_id": f"reset-{decision}"}}

        paused = graph.invoke(
            {"messages": [HumanMessage(content="Necesito restablecer mi contraseña.")]},
            config=config,
        )

        print("\nDecisión:", decision)
        print("Solicitud:", paused["__interrupt__"][0].value)

        result = graph.invoke(Command(resume=decision), config=config)

        for message in result["messages"]:
            print(f"{type(message).__name__}: {message.content}")

            if isinstance(message, ToolMessage):
                print("  tool_call_id:", message.tool_call_id)

    public_config = {"configurable": {"thread_id": "hours-001"}}

    public_result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="¿Cuál es el horario de la mesa de ayuda?")
            ]
        },
        config=public_config,
    )

    print("\nConsulta pública:")
    print("¿Se pausó?", "__interrupt__" in public_result)
    print("Respuesta:", public_result["messages"][-1].content)
