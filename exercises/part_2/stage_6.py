from langchain_core.messages import AIMessage, HumanMessage
from stage4 import graph

question = {
    "messages": [
        HumanMessage(
            content="¿Cuál es el estado del ticket INC-4471?"
        )
    ]
}

print("\nModo updates:")
for event in graph.stream(
    question,
    config={"recursion_limit": 12},
    stream_mode="updates"
):
    for node_name, update in event.items():
        message_type = [
            type(message).__name__
            for message in update["messages"]
        ]
        print(node_name, message_type)


print("\nModo updates con mensajes:")
for event in graph.stream(
    question,
    config={"recursion_limit": 12},
    stream_mode="updates"
):
    for node_name, update in event.items():
        for message in update["messages"]:
            print(
                f"{node_name} -> "
                f"{type(message).__name__}: {message.content}"
            )

            if isinstance(message, AIMessage) and message.tool_calls:
                print(  "Solicitud:", message.tool_calls)


print("\nModo values:")

for state in graph.stream(
    question, 
    config={"recursion_limit": 12},
    stream_mode="values"
):
    message_type = [
        type(message).__name__
        for message in state["messages"]
    ]
    print(len(state["messages"]), message_type)

print("\nModos combinados:")

for node, chunk in graph.stream(
    question,
    config={"recursion_limit": 12},
    stream_mode=["updates", "values"]
):
    if node == "updates":
        print("Actualizó nodo:", next(iter(chunk)))
    else:
        print("Mensajes en el estado", len(chunk["messages"]))