from typing import TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph


class SimulatedModel:
    def invoke(self, messages):
        return AIMessage(
            content="Para solicitar una laptop, abre un ticket de hardware."
        )

model = SimulatedModel();

SYSTEM = SystemMessage(
    content=(
        "You are an internal helpdesk assistant for IT and HR questions. "
        "Be concise and practical"
    )
)

class HelpdeskState(TypedDict):
    messages: list[AnyMessage]

def chat_bot(state: HelpdeskState) -> dict:
    response = model.invoke([SYSTEM, *state["messages"]])
    return {"messages": [response]}

builder = StateGraph(HelpdeskState)
builder.add_node("chat", chat_bot)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {"messages": [HumanMessage(content="How do I request a new laptop")]}
    )


    print(f"Messages in final state: {len(result['messages'])}")
    for message in result["messages"]:
        print(f"{type(message).__name__}: {message.content}")