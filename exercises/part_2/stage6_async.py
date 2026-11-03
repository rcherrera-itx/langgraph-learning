import asyncio

from langchain_core.messages import HumanMessage
from stage4 import graph


async def main():
    question = {
        "messages": [HumanMessage(content="¿Cuál es el estado del ticket INC-4471?")]
    }

    config = {"recursion_limit": 12}

    result = await graph.ainvoke(question, config=config)
    print("ainvoke:", len(result["messages"]), "mensajes")
    print("Respuesta:", result["messages"][-1].content)

    print("\nastream:")
    async for event in graph.astream(question, config=config, stream_mode="updates"):
        for node_name, update in event.items():
            types = [
                type(message).__name__
                for message in update["messages"]
            ]
            print(node_name, types)


if __name__ == "__main__":
    asyncio.run(main())
