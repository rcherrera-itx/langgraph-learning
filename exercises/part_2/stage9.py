import sys
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, trim_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class HelpdeskState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def chat(state: HelpdeskState) -> dict:
    last = state["messages"][-1]

    if last.content == "¿Qué modelo de laptop tengo?":
        context = trim_messages(
            state["messages"],
            max_tokens=4,
            token_counter=len,
            strategy="last",
            start_on="human",
            include_system=True,
        )

        print("Mensajes disponibles:", len(state["messages"]))
        print("Mensajes usados:", len(context))

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
        raise SystemExit("Uso: python stage9.py 'mensaje' [thread_id]")

    db_path = Path(__file__).with_name("stage9.sqlite")

    thread_id = sys.argv[2] if len(sys.argv) == 3 else "stage9-demo-001"
    config = {"configurable": {"thread_id": thread_id}}

    with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)

        result = graph.invoke(
            {"messages": [HumanMessage(content=sys.argv[1])]}, config=config
        )

        print("Mensajes:", len(result["messages"]))
        print("Respuesta:", result["messages"][-1].content)
