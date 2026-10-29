from langchain.messages import AIMessage, HumanMessage, SystemMessage 

messages = [
    SystemMessage(content="Responde en español y paso a paso."),
    HumanMessage(content="Mi computadora es una HP"),
    AIMessage(content="Entendido ¿Qué problema tiene tu computadora?"),
]

for message in messages:
    print(message.type, ":", message.content)