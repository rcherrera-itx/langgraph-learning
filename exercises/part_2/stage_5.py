from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    category: str


class SimulatedModel:
    def invoke(self, messages):
        last_message = messages[-1]

        if last_message.content == "¿Qué modelo de laptop tengo?":
            has_laptop = any(
                isinstance(message, HumanMessage)
                and message.content == "Mi laptop es una X1 Carbon."
                for message in messages
            )

            if has_laptop:
                return AIMessage(content="Dijiste que tienes una X1 Carbon.")

            return AIMessage(content="No encuentro ese dato en el historial.")

        return AIMessage(content="Entendido.")


model = SimulatedModel()


def chat_node(state: HelpdeskState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(HelpdeskState)

builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    alice = {"configurable": {"thread_id": "alice-session-1"}}
    bob = {"configurable": {"thread_id": "bob-session"}}

    graph.invoke(
        {"messages": [HumanMessage(content="Mi laptop es una X1 Carbon.")], "category": ""},
        config=alice,
    )

    alice_result = graph.invoke(
        {"messages": [HumanMessage(content="¿Qué modelo de laptop tengo?")]},
        config=alice
    )

    bob_result = graph.invoke(
        {"messages": [HumanMessage(content="¿Qué modelo de laptop tengo?")], "category": ""},
        config=bob
    )

    print("Alice:", alice_result["messages"][-1].content)
    print("Bob:", bob_result["messages"][-1].content)
    print("Mensajes de Alice:", len(alice_result["messages"]))
    print("Mensajes de Bob:", len(bob_result["messages"]))

    snapshot = graph.get_state(alice)

    print("\nHistorial guardado de Alice:")
    for message in snapshot.values["messages"]:
        print(f"{type(message).__name__}: {message.content}")

    print("Nodos pendientes:", snapshot.next)

    print("\nVersiones guardadas del estado:")

    for saved in graph.get_state_history(alice):
        messages = saved.values.get("messages", [])

        print(
            f"Paso: {saved.metadata['step']} | "
            f"Mensajes: {len(messages)} | "
            f"Pendientes: {saved.next}"
        )

    previous_version = next(
        saved
        for saved in graph.get_state_history(alice)
        if len(saved.values.get("messages", [])) == 2
        and saved.next == ()
    )

    previous_state = graph.get_state(previous_version.config)
    current_state = graph.get_state(alice)

    print("\nComparación de versiones:")
    print("Configuración de la versión anterior:", previous_version.config)
    print("Mensajes en la versión anterior:", len(previous_state.values["messages"]))
    print("Configuración de la versión actual:", current_state.config)
    print("Mensajes en la versión actual:", len(current_state.values["messages"]))
    print("Paso de la versión anterior:", previous_state.metadata["step"])

    before_versions = len(list(graph.get_state_history(alice)))

    graph.update_state(alice, {"category": "it"})

    updated_state = graph.get_state(alice)
    after_versions = len(list(graph.get_state_history(alice)))

    print("\nActualización manual:")
    print("Categoría:", updated_state.values["category"])
    print("Mensajes:", len(updated_state.values["messages"]))
    print("Versiones antes:", before_versions)
    print("Versiones despúes:", after_versions)