#!/usr/bin/env python3
"""Inserta solo ejercicios en la tabla exercises (para poder crear rutinas)."""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DEBUG", "False")

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings


def _seed_engine():
    kw: dict = {"echo": False}
    ca = settings.mysql_connect_args()
    if ca:
        kw["connect_args"] = ca
    return create_async_engine(settings.get_database_url(), **kw)

EXERCISES = [
    {"name": "Sentadillas", "description": "Cuádriceps y glúteos", "muscle_group": "Piernas", "difficulty": "BEGINNER"},
    {"name": "Press banca", "description": "Pectorales y tríceps", "muscle_group": "Pecho", "difficulty": "INTERMEDIATE"},
    {"name": "Dominadas", "description": "Espalda y bíceps", "muscle_group": "Espalda", "difficulty": "INTERMEDIATE"},
    {"name": "Plancha", "description": "Core", "muscle_group": "Core", "difficulty": "BEGINNER"},
    {"name": "Peso muerto", "description": "Cadena posterior", "muscle_group": "Espalda", "difficulty": "ADVANCED"},
    {"name": "Remo con barra", "description": "Espalda", "muscle_group": "Espalda", "difficulty": "INTERMEDIATE"},
    {"name": "Press militar", "description": "Hombros", "muscle_group": "Hombros", "difficulty": "INTERMEDIATE"},
    {"name": "Curl bíceps", "description": "Bíceps", "muscle_group": "Brazos", "difficulty": "BEGINNER"},
]


async def main():
    from uuid import uuid4
    from src.infrastructure.database.models.training_models import ExerciseModel
    from sqlalchemy import select

    print("=== Insertar ejercicios en FitLife ===\n")
    engine = _seed_engine()
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        result = await session.execute(select(ExerciseModel).limit(1))
        if result.scalar_one_or_none():
            print("Ya hay ejercicios en la base de datos. No se añaden más.")
            print("Si quieres añadir de todos modos, borra antes los existentes en la tabla 'exercises'.")
        else:
            for ex in EXERCISES:
                session.add(ExerciseModel(
                    id=str(uuid4()),
                    name=ex["name"],
                    description=ex.get("description"),
                    muscle_group=ex.get("muscle_group"),
                    difficulty=ex.get("difficulty"),
                ))
            await session.commit()
            print(f"Se han insertado {len(EXERCISES)} ejercicios correctamente.")

    await engine.dispose()
    print("\nListo. Recarga la página de Rutinas en el navegador.")


if __name__ == "__main__":
    from src.infrastructure.database.win_asyncio import apply_windows_ssl_asyncio_fix

    apply_windows_ssl_asyncio_fix()
    asyncio.run(main())
