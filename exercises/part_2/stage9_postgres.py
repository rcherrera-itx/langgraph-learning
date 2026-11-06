import sys
from getpass import getpass
from typing import Annotated, TypedDict
from urllib.parse import quote

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, trim_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def chat(state: HelpdeskState) -> dict:
    context = trim_messages(
        state["messages"],
        max_tokens=4,
        token_counter=len,
        strategy="last",
        start_on="human",
        include_system=True,
    )

    last_message = state["messages"][-1]

    print("Mensajes disponibles:", len(state["messages"]))
    print("Mensajes usados:", len(context))
    print("Última entrada:", repr(last_message.content))

    if last_message.content == "¿Qué modelo de laptop tengo?":
        known = any(
            isinstance(message, HumanMessage)
            and message.content == "Mi laptop es una X1 Carbon."
            for message in context
        )

        answer = (
            "Dijiste que tienes una X1 Carbon." if known else "No encuentro ese dato."
        )
    else:
        answer = "Entendido."

    return {"messages": [AIMessage(content=answer)]}


builder = StateGraph(HelpdeskState)
builder.add_node("chat", chat)

builder.add_edge(START, "chat")
builder.add_edge("chat", END)

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit("Uso: python stage9_postgres.py 'mensaje' [thread_id]")

    password = getpass("Contraseña de langgraph demo: ")
    db_uri = (
        f"postgresql://langgraph_demo:{quote(password, safe='')}"
        "@127.0.0.1:5432/langgraph_demo"
    )

    thread_id = sys.argv[2] if len(sys.argv) == 3 else "stage9-demo-001"
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(db_uri) as checkpointer:
        checkpointer.setup()
        graph = builder.compile(checkpointer=checkpointer)

        result = graph.invoke(
            {"messages": [HumanMessage(content=sys.argv[1])]}, config=config
        )

        print("Mensajes:", len(result["messages"]))
        print("Respuesta:", result["messages"][-1].content)
