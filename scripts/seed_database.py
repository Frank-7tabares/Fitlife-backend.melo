import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DEBUG', 'False')
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.settings import settings

def _seed_engine():
    kw: dict = {'echo': False}
    ca = settings.mysql_connect_args()
    if ca:
        kw['connect_args'] = ca
    return create_async_engine(settings.get_database_url(), **kw)
SEED_USERS = [{'email': 'admin@fitlife.com', 'password': 'Admin123!', 'role': 'ADMIN', 'full_name': 'Administrador FitLife'}, {'email': 'instructor@fitlife.com', 'password': 'Coach123!', 'role': 'INSTRUCTOR', 'full_name': 'Carlos Instructor'}, {'email': 'user@fitlife.com', 'password': 'User1234!', 'role': 'USER', 'full_name': 'María Usuario'}]

async def seed_users(session: AsyncSession) -> None:
    from src.infrastructure.database.models.user_model import UserModel
    from src.infrastructure.security.password_hasher import PasswordHasher
    from uuid import uuid4
    from datetime import datetime
    from sqlalchemy import select
    for user_data in SEED_USERS:
        result = await session.execute(select(UserModel).where(UserModel.email == user_data['email']))
        if result.scalar_one_or_none():
            print(f"  [SKIP] {user_data['email']} ya existe")
            continue
        model = UserModel(id=str(uuid4()), email=user_data['email'], password_hash=PasswordHasher.hash(user_data['password']), role=user_data['role'], is_active=True, full_name=user_data['full_name'], created_at=datetime.utcnow())
        session.add(model)
        print(f"  [OK] Creado: {user_data['email']} ({user_data['role']})")
    await session.commit()

async def seed_instructors(session: AsyncSession) -> None:
    from src.infrastructure.database.models.instructor_models import InstructorModel
    from src.infrastructure.database.models.user_model import UserModel
    from sqlalchemy import select
    result = await session.execute(select(UserModel).where(UserModel.email == 'instructor@fitlife.com'))
    instructor_user = result.scalar_one_or_none()
    if not instructor_user:
        print('  [SKIP] Usuario instructor no encontrado, omitiendo seed de instructor')
        return
    result = await session.execute(select(InstructorModel).where(InstructorModel.id == instructor_user.id))
    if result.scalar_one_or_none():
        print('  [SKIP] Instructor ya existe')
        return
    model = InstructorModel(id=str(instructor_user.id), name='Carlos Instructor', certifications=['ACE', 'NSCA'], specializations='Fuerza y acondicionamiento físico', rating_avg=0.0, certificate_status='verified')
    session.add(model)
    await session.commit()
    print('  [OK] Instructor creado')

async def seed_exercises(session: AsyncSession) -> None:
    from src.infrastructure.database.models.training_models import ExerciseModel
    from sqlalchemy import select
    from uuid import uuid4
    result = await session.execute(select(ExerciseModel).limit(1))
    if result.scalar_one_or_none():
        print('  [SKIP] Ya existen ejercicios')
        return
    exercises = [{'name': 'Sentadillas', 'description': 'Cuádriceps y glúteos', 'muscle_group': 'Piernas', 'difficulty': 'BEGINNER'}, {'name': 'Press banca', 'description': 'Pectorales y tríceps', 'muscle_group': 'Pecho', 'difficulty': 'INTERMEDIATE'}, {'name': 'Dominadas', 'description': 'Espalda y bíceps', 'muscle_group': 'Espalda', 'difficulty': 'INTERMEDIATE'}, {'name': 'Plancha', 'description': 'Core', 'muscle_group': 'Core', 'difficulty': 'BEGINNER'}, {'name': 'Peso muerto', 'description': 'Cadena posterior', 'muscle_group': 'Espalda', 'difficulty': 'ADVANCED'}]
    for ex in exercises:
        session.add(ExerciseModel(id=str(uuid4()), name=ex['name'], description=ex.get('description'), muscle_group=ex.get('muscle_group'), difficulty=ex.get('difficulty')))
    await session.commit()
    print(f'  [OK] Creados {len(exercises)} ejercicios')

async def main():
    print('=== FitLife Database Seed ===\n')
    engine = _seed_engine()
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        print('Creando usuarios...')
        await seed_users(session)
        print('\nCreando instructores...')
        await seed_instructors(session)
        print('\nCreando ejercicios...')
        await seed_exercises(session)
    await engine.dispose()
    print('\n=== Seed completado ===')
if __name__ == '__main__':
    from src.infrastructure.database.win_asyncio import apply_windows_ssl_asyncio_fix
    apply_windows_ssl_asyncio_fix()
    asyncio.run(main())
