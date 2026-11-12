"""Simula decisiones y respuestas de un modelo sin utilizar una API key."""

# Representa respuesta del asistente, mensajes del historial y resultados de herramientas.
from langchain_core.messages import AIMessage, AnyMessage, ToolMessage


class SimulatedModel:
    """Produce respuestas deterministas para las solicitudes del ejericio."""

    def invoke(
        self, messages: list[AnyMessage], profile: dict | None = None
    ) -> AIMessage:
        """Responde según el último mensaje y el perfil disponible."""

        # Examina el mensaje más reciente recibido por el modelo.
        last_message = messages[-1]

        # Si lleg+o un resultado de herramienta, redacta la respuesta final.
        if isinstance(last_message, ToolMessage):
            # Convierte el contenido de la herramienta en texto.
            tool_result = str(last_message.content)

            # reconoce la acción por el identificador de su llamada.
            is_password_reset = last_message.tool_call_id.startswith("call_reset_")

            # Comunica una denegación de un restablecimiento.
            if tool_result.startswith("DENIED") and is_password_reset:
                return AIMessage(
                    content="Solicitud denegada; no se restableció la contraseña."
                )

            # Comunica una denegación sin presentar datos del ticket.
            if tool_result.startswith("DENIED"):
                return AIMessage(content="No tienes permiso para consultar ese ticket.")

            # Comunica el resultado de un restablecimiento aprobado.
            if is_password_reset:
                return AIMessage(content=f"Resultado: {tool_result}")

            # Comunica el resultado de una consulta autorizada.
            return AIMessage(content=f"Estado consultado: {tool_result}")

        # Lee la solicitud actual cuando aún no hay resultado de herramienta.
        request = str(last_message.content).strip()

        # Normaliza mayúsculas y minúsculas para reconocer las frases simuladas.
        normalized_request = request.casefold()

        # Reconoce una solicitud de restablecimiento de contraseña.
        if "restablec" in normalized_request and "contraseña" in normalized_request:
            # Vincula la futura respuesta con esta llamada concreta
            call_id = f"call_reset_{len(messages):03d}"

            # Solicita la acción sin elegir usuario ni request_id
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "reset_password",
                        "args": {},
                        "id": call_id,
                        "type": "tool_call",
                    }
                ],
            )

        # Reconoce la pregunta por el modelo de laptop del empleado.
        if "modelo de laptop" in normalized_request and "tengo" in normalized_request:
            
            # Busca el modelo con el perfil que recibió desde el estado.
            laptop_model = (profile or {}).get("laptop_model")

            # Responde con el dato guardado cuando está disponible.
            if laptop_model:
                return AIMessage(content=f"Tu laptop es una {laptop_model}")

            # Responde que no existe un modelo registrado para el usuario.
            return AIMessage(content="No tengo registrado tu modelo de laptop.")

        if normalized_request.startswith("mi laptop es una "):
            
            # Comprueba si el perfil ya relfeja el modelo informado.
            laptop_model = (profile or {}).get("laptop_model")

            # Confirma el registro cuando el dato está disponible en el estado.
            if laptop_model:
                return AIMessage(content=f"Modelo de laptop registrado: {laptop_model}")

            # Evita afirmar que se guardó un dato que todavía no está en el perfil.
            return AIMessage(content="No pude registrar el modelo de tu laptop.")

        # Mantiene la respuesta general de IT para solicitudes sin ticket conocido.
        if "INC-4471" not in request.upper():
            return AIMessage(content="Para recibir soporte técnico, abre un ticket.")

        # Crea un identificador que relacionará esta solicitud con su ToolMessage
        call_id = f"call_ticket_{len(messages):03d}"

        # Solicita lookup_ticket; esta respuesta todavía no ejecuta la herramienta.
        return AIMessage(
            content="",
            tool_calls=[  # Describe la herramienta que debe ejecutarse.
                {
                    "name": "lookup_ticket",  # Nombre de la herramienta solicitada.
                    "args": {
                        "ticket_id": "INC-4471"
                    },  # Parámetros que recibirá la herramienta solicitada.
                    "id": call_id,  # Vincula la solicitud con ToolMessage.
                    "type": "tool_call",  # Tipo de esta solicitud.
                }
            ],
        )
