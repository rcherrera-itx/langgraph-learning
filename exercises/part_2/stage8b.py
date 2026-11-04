from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    employee_id: str
    profile: dict


def load_profile(state: HelpdeskState, runtime: Runtime) -> dict:
    namespace = ("profiles", state["employee_id"])
    item = runtime.store.get(namespace, "profile")
    return {"profile": item.value if item else {}}


class SimluatedModel:
    def invoke(self, messages, profile):
        last = messages[-1]

        if last.content.startswith("Mi laptops es una"):
            return AIMessage(content="Entendido")

        if last.content == "¿Qué modelo de laptop tengo?":
            model = profile.get("laptop_model")
            return AIMessage(
                content=f"Tienes una {model}." if model else "No tengo ese dato"
            )

        return AIMessage(content="No entendí la solicitud.")


model = SimluatedModel()


def chat_node(state: HelpdeskState) -> dict:
    response = model.invoke(state["messages"], state["profile"])
    return {"messages": [response]}


def save_profile(state: HelpdeskState, runtime: Runtime) -> dict:
    latest_human = next(
        message
        for message in reversed(state["messages"])
        if isinstance(message, HumanMessage)
    )

    prefix = "Mi laptop es una "

    if not latest_human.content.startswith(prefix):
        return {}

    new_profile = {
        **state["profile"],
        "laptop_model": latest_human.content[len(prefix) :].rstrip("."),
    }

    namespace = ("profiles", state["employee_id"])
    runtime.store.put(namespace, "profile", new_profile)

    return {"profile": new_profile}


builder = StateGraph(HelpdeskState)

builder.add_node("load_profile", load_profile)
builder.add_node("chat", chat_node)
builder.add_node("save_profile", save_profile)

builder.add_edge(START, "load_profile")
builder.add_edge("load_profile", "chat")
builder.add_edge("chat", "save_profile")
builder.add_edge("save_profile", END)

graph = builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())

if __name__ == "__main__":
    first = graph.invoke(
        {
            "messages": [HumanMessage(content="Mi laptop es una X1 Cabron")],
            "employee_id": "EMP-0001",
            "profile": {},
        },
        config={"configurable": {"thread_id": "case-001"}},
    )

    second = graph.invoke(
        {
            "messages": [HumanMessage(content="¿Qué modelo de laptop tengo?")],
            "employee_id": "EMP-0001",
            "profile": {},
        },
        config={"configurable": {"thread_id": "case-002"}},
    )

    third = graph.invoke(
        {
            "messages": [HumanMessage(content="¿Qué modelo de laptop tengo?")],
            "employee_id": "EMP-0002",
            "profile": {},
        },
        config={"configurable": {"thread_id": "case-003"}},
    )

    print("Mensajes en caso 1:", len(first["messages"]))
    print("Mensajes en caso 2:", len(second["messages"]))
    print("Perfil cargado en caso 2:", second["profile"])
    print("Respuesta en caso 2:", second["messages"][-1].content)
    print("Perfil cargado para EMP-002:", third["profile"])
    print("Respuesta para EMP-002:", third["messages"][-1].content)
