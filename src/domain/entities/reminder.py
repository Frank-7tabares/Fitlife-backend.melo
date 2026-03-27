"""Entidad de dominio: Recordatorio (Historia 8 - Recordatorios, RF-095 a RF-100)."""
from dataclasses import dataclass
from datetime import datetime, time
from uuid import UUID
from enum import Enum
from typing import Optional


class ReminderType(str, Enum):
    """Tipo de recordatorio (RF-097)."""
    TRAINING = "TRAINING"  # Recordatorio de entrenamiento
    PHYSICAL_RECORD = "PHYSICAL_RECORD"  # Recordatorio de registro físico
    INSTRUCTOR_FOLLOWUP = "INSTRUCTOR_FOLLOWUP"  # Seguimiento del instructor


class ReminderFrequency(str, Enum):
    """Frecuencia de recordatorio (RF-099)."""
    ONCE = "ONCE"  # Una vez
    DAILY = "DAILY"  # Diariamente
    WEEKLY = "WEEKLY"  # Semanalmente
    MONTHLY = "MONTHLY"  # Mensualmente


@dataclass
class Reminder:
    """Recordatorio para usuario.

    Atributos:
        id: UUID único del recordatorio
        user_id: Usuario propietario del recordatorio
        reminder_type: TRAINING | PHYSICAL_RECORD | INSTRUCTOR_FOLLOWUP (RF-097)
        title: Título del recordatorio
        description: Descripción (opcional)
        scheduled_time: Hora del recordatorio (HH:MM) (RF-100)
        timezone: Zona horaria (ej. America/Bogota) (RF-100)
        frequency: ONCE | DAILY | WEEKLY | MONTHLY (RF-099)
        is_active: Si el recordatorio está activo (RF-098)
        last_sent_at: Último envío (para control de duplicados)
        created_at: Fecha de creación
        updated_at: Fecha de actualización (opcional)

    Notas (RF-095 a RF-100):
        - RF-095: Recordatorios para entrenamiento, registro físico, seguimiento
        - RF-096: Tipo de recordatorio
        - RF-097: Enumeración de tipos
        - RF-098: Activación/desactivación
        - RF-099: Frecuencia configurable
        - RF-100: Respeto de zona horaria del usuario
    """
    id: UUID
    user_id: UUID
    reminder_type: ReminderType
    title: str
    scheduled_time: str  # HH:MM formato
    timezone: str  # ej. America/Bogota
    frequency: ReminderFrequency
    is_active: bool = True
    created_at: datetime = None
    description: Optional[str] = None
    last_sent_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
