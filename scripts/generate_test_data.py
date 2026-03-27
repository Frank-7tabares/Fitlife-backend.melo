#!/usr/bin/env python3
"""Script: Genera datos de prueba masivos para entornos de desarrollo/QA."""
import asyncio
import sys
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DEBUG", "False")

from dotenv import load_dotenv
load_dotenv()

try:
    from faker import Faker
except ImportError:
    print("ERROR: Instala 'faker' con: pip install faker")
    sys.exit(1)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config.settings import settings
from src.infrastructure.security.password_hasher import PasswordHasher

fake = Faker("es_CO")

DATABASE_URL = (
    f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

NUM_USERS = int(os.getenv("SEED_USERS", "20"))
NUM_ASSESSMENTS = int(os.getenv("SEED_ASSESSMENTS", "40"))


async def generate_users(session: AsyncSession) -> list:
    from src.infrastructure.database.models.user_model import UserModel

    users = []
    password_hash = PasswordHasher.hash("TestUser123!")

    for _ in range(NUM_USERS):
        model = UserModel(
            id=str(uuid4()),
            email=fake.unique.email(),
            password_hash=password_hash,
            role="USER",
            is_active=True,
            full_name=fake.name(),
            created_at=fake.date_time_between(start_date="-6m", end_date="now"),
        )
        session.add(model)
        users.append(model)

    await session.commit()
    print(f"  [OK] {NUM_USERS} usuarios generados")
    return users


async def generate_assessments(session: AsyncSession, users: list) -> None:
    from src.infrastructure.database.models.assessment_model import AssessmentModel
    import json

    categories = ["EXCELLENT", "GOOD", "FAIR", "POOR"]
    comparisons = ["BODY_YOUNGER", "BODY_OLDER", "SAME_AGE"]

    for _ in range(NUM_ASSESSMENTS):
        user = random.choice(users)
        score = round(random.uniform(30, 98), 2)
        real_age = random.randint(18, 65)
        body_age = round(real_age + random.uniform(-8, 8), 2)
        body_age = max(18, min(120, body_age))

        model = AssessmentModel(
            id=str(uuid4()),
            user_id=user.id,
            fitness_score=score,
            category=categories[min(3, int((100 - score) / 25))],
            body_age=body_age,
            comparison=comparisons[0] if body_age < real_age else comparisons[1],
            responses=json.dumps({"q1": random.randint(1, 10), "q2": random.randint(1, 5)}),
            created_at=fake.date_time_between(start_date="-3m", end_date="now"),
        )
        session.add(model)

    await session.commit()
    print(f"  [OK] {NUM_ASSESSMENTS} evaluaciones generadas")


async def main():
    print("=== FitLife Test Data Generator ===\n")
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        print("Generando usuarios...")
        users = await generate_users(session)
        print("\nGenerando evaluaciones físicas...")
        await generate_assessments(session, users)

    await engine.dispose()
    print(f"\n=== Generación completada: {NUM_USERS} usuarios, {NUM_ASSESSMENTS} evaluaciones ===")


if __name__ == "__main__":
    asyncio.run(main())
