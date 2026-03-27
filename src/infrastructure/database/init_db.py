import asyncio
import logging
import os
import sys

# Add the project root to sys.path to allow absolute imports from 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.infrastructure.database.connection import engine, Base
# Import all models to ensure they are registered with Base.metadata
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.models.auth_models import RefreshTokenModel, PasswordResetTokenModel, PasswordHistoryModel
from src.infrastructure.database.models.assessment_model import AssessmentModel
from src.infrastructure.database.models.physical_record_model import PhysicalRecordModel
from src.infrastructure.database.models.training_models import ExerciseModel, RoutineModel
from src.infrastructure.database.models.training_assignment_models import RoutineAssignmentModel, WorkoutCompletionModel
from src.infrastructure.database.models.nutrition_models import NutritionPlanModel
from src.infrastructure.database.models.audit_model import ProfileAuditLogModel
from src.infrastructure.database.models.instructor_models import InstructorModel, InstructorAssignmentModel, InstructorRatingModel
from src.infrastructure.database.models.reminder_model import ReminderModel
from src.infrastructure.database.models.message_model import MessageModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        # Warning: This will drop all tables and recreate them
        # logger.info("Dropping all tables...")
        # await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
