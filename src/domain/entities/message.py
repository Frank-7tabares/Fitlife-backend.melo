"""Entidad de dominio: Mensaje entre usuarios (Historia 7 - Mensajería, RF-088 a RF-094)."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional


class MessageType(str, Enum):
    """Tipo de mensaje (RF-089)."""
    INSTRUCTOR_MESSAGE = "INSTRUCTOR_MESSAGE"  # Mensaje directo de instructor a usuario
    USER_MESSAGE = "USER_MESSAGE"  # Mensaje del atleta hacia su instructor asignado
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"  # Notificación automática del sistema


@dataclass
class Message:
    """Mensaje entre usuarios.

    Atributos:
        id: UUID único del mensaje
        sender_id: ID del usuario que envía (instructor o sistema)
        recipient_id: ID del usuario que recibe (siempre usuario regular)
        subject: Asunto del mensaje (opcional)
        content: Contenido del mensaje (RF-090)
        message_type: INSTRUCTOR_MESSAGE | SYSTEM_NOTIFICATION (RF-089)
        is_read: Si el destinatario ha leído el mensaje (RF-091)
        created_at: Timestamp de creación
        read_at: Timestamp de lectura (opcional, RF-091)

    Notas (RF-088 a RF-094):
        - RF-088: Mensajes entre instructor y usuario
        - RF-089: Tipo de mensaje (directo vs automático)
        - RF-090: Contenido del mensaje
        - RF-091: Marca de lectura
        - RF-092: Historial de mensajes
        - RF-093: Instructor solo a usuarios asignados
        - RF-094: Notificaciones automáticas al asignar rutina/plan
    """
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    content: str
    message_type: MessageType
    is_read: bool = False
    created_at: datetime = None
    subject: Optional[str] = None
    read_at: Optional[datetime] = None
