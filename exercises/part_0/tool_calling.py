from langchain.messages import AIMessage, ToolMessage


def lookup_ticket(ticket_id):
    tickets = {"INC-4471": "Abierto; asignado al equipo de redes."}
    return tickets.get(ticket_id, "Ticket no encontrado")


request = AIMessage(
    content="",
    tool_calls=[
        {"name": "lookup_ticket", "args": {"ticket_id": "INC-4471"}, "id": "call_001"}
    ],
)

tool_call = request.tool_calls[0]

print("Solicitud preparada")

result = lookup_ticket(tool_call["args"]["ticket_id"])

tool_message = ToolMessage(content=result, tool_call_id=tool_call["id"])

print("Resultado: ", tool_message.content)
print("Solicitud asociada: ", tool_message.tool_call_id)
