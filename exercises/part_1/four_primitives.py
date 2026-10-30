from typing import TypedDict
from langgraph.graph import START, END, StateGraph

# Esquema: describe la estructura esperada
class SupportState(TypedDict):
    employee_id: str
    messages: list[str]
    category: str
    answer: str


# Valores: representan una solicitud concreta.
initial_state: SupportState = {
    "employee_id": "EMP-001",
    "messages": ["Mi computadora no prende"],
    "category": "",
    "answer": ""
}

print("Estado inicial: ", initial_state)
print("Empleado: ", initial_state["employee_id"])
print("Mensajes: ", initial_state["messages"])
print("Categoria: ", initial_state["category"])
print("Respuesta: ", initial_state["answer"])

def classify(state: SupportState):
    return {"category": "it"}

update = classify(initial_state)

print("Actualización devuelta: ", update)
print("Estado despúes de llamar a la función", initial_state)

def prepare_reply(state: SupportState):
    print("[prepare_reply] Categoría recibida: ", state["category"])
    return {
        "answer": "Tus solicitud corresponde a " +  state["category"]
    }

#Creamos el constructor indicando el esquema del estado.
builder = StateGraph(SupportState)

# Registramos nuestra función como un nodo
builder.add_node("classify", classify)
builder.add_node("prepare_reply", prepare_reply)

# Definimos las conexiones: comenzar, clasificar y terminar.
builder.add_edge(START, "classify")
builder.add_edge("classify", "prepare_reply")
builder.add_edge("prepare_reply", END)

# Compilamos la estructura para poder ejecutarla.
print("[APP] Antes de compilar")
graph = builder.compile()
print("[APP] Después de compilar")

# Ejecutamos el grafo con los datos iniciales
print("[APP] Antes del invoke")
result = graph.invoke(initial_state)
print("[APP] Después del invoke")

print("Resultado del grafo: ", result)