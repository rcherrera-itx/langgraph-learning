"""Simula las respuestas de un modelo sin utilizar una API key."""

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage


class SimulatedModel:
    """Produce una respuesta fija o solicita consultar el ticket del ejercicio."""

    def invoke(self, messages: list[AnyMessage]) -> AIMessage:
        """Solicita un ticket o redacta una respuesta tras recibir su resultado"""

        last_message = messages[-1]

        if isinstance(last_message, ToolMessage):
            tool_result = str(last_message.content)

            if tool_result.startswith("DENIED"):
                return AIMessage(content="No tienes permiso para consultar ese ticket.")

            return AIMessage(content=f"Estado consultado: {tool_result}")

        request = str(last_message.content).upper()

        if "INC-4471" not in request:
            return AIMessage(content="Para recibir soporte técnico, abre un ticket.")

        call_id = f"call_ticket_{len(messages):03d}"

        return AIMessage(
            content="",
            tool_calls=[ # Describe la herramienta que debe ejecutarse.
                {
                    "name": "lookup_ticket", # Nombre de la herramienta solicitada.
                    "args": {"ticket_id": "INC-4471"}, # Parámetros que recibirá la herramienta solicitada.
                    "id": call_id, # Vincula la solicitud con ToolMessage.
                    "type": "tool_call", # Tipo de esta solicitud.
                }
            ],
        )
