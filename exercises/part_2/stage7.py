from typing import TypedDict

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict):
    employee_id: str
    status: str


def approval_gate(state: ApprovalState) -> dict:
    print("approval_gate iniciando...")

    decision = interrupt(
        {
            "action": "reset_password",
            "employee_id": state["employee_id"],
        }
    )

    print("Decisión recibida:", decision)

    if decision == "approve":
        return {"status": "approved"}

    return {"status": "denied"}


@tool
def reset_password(employee_id: str) -> str:
    """Simula el restablecimiento de una contraseña."""
    return f"Restablecimiento simulado para {employee_id}"


def route_after_approval(state: ApprovalState) -> str:
    if state["status"] == "approved":
        return "execute_reset"
    return END


def execute_reset(state: ApprovalState) -> dict:
    print("Ejecutando herramienta simulada")
    result = reset_password.invoke({
        "employee_id": state["employee_id"]
    })
    return {"status": result}


builder = StateGraph(ApprovalState)
builder.add_node("approval_gate", approval_gate)
builder.add_node("execute_reset", execute_reset)

builder.add_edge(START, "approval_gate")

builder.add_conditional_edges(
    "approval_gate",
    route_after_approval,
    {
        "execute_reset": "execute_reset",
        END: END
    }
)

builder.add_edge("execute_reset", END)

graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "approval-001"}}

    paused = graph.invoke(
        {"employee_id": "EMP-001", "status": "pending"}, config=config
    )

    print("Solicitud de revisión:", paused["__interrupt__"][0].value)
    print("Nodo pendiente:", graph.get_state(config).next)

    resumed = graph.invoke(Command(resume="approve"), config=config)

    print("Estado final:", resumed["status"])
