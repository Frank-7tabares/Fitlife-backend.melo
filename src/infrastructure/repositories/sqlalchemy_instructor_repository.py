from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities.instructor import Instructor, InstructorAssignment, InstructorRating
from ..database.models.instructor_models import InstructorModel, InstructorAssignmentModel, InstructorRatingModel

class SQLAlchemyInstructorRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(self) -> List[InstructorModel]:
        stmt = select(InstructorModel)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, instructor_id: UUID) -> Optional[InstructorModel]:
        stmt = select(InstructorModel).where(InstructorModel.id == str(instructor_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, instructor: Instructor) -> Instructor:
        model = InstructorModel(id=str(instructor.id), name=instructor.name, certifications=instructor.certifications, specializations=instructor.specializations, rating_avg=instructor.rating_avg, certificate_url=getattr(instructor, 'certificate_url', None), certificate_status=getattr(instructor, 'certificate_status', 'pending'))
        self.session.add(model)
        await self.session.commit()
        return instructor

    async def delete_by_id(self, instructor_id: UUID) -> bool:
        stmt = delete(InstructorModel).where(InstructorModel.id == str(instructor_id))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_certificate_status(self, instructor_id: UUID, status: str) -> None:
        stmt = update(InstructorModel).where(InstructorModel.id == str(instructor_id)).values(certificate_status=status)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_rating_avg(self, instructor_id: UUID, new_avg: float) -> None:
        stmt = update(InstructorModel).where(InstructorModel.id == str(instructor_id)).values(rating_avg=new_avg)
        await self.session.execute(stmt)
        await self.session.commit()

    async def find_active_assignment(self, user_id: UUID) -> Optional[InstructorAssignment]:
        return await SQLAlchemyInstructorAssignmentRepository(self.session).find_active_by_user(user_id)

class SQLAlchemyInstructorAssignmentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, assignment: InstructorAssignment) -> InstructorAssignment:
        model = InstructorAssignmentModel(id=str(assignment.id), user_id=str(assignment.user_id), instructor_id=str(assignment.instructor_id), started_at=assignment.started_at, ended_at=assignment.ended_at, is_active=assignment.is_active)
        self.session.add(model)
        await self.session.commit()
        return assignment

    async def deactivate_active_for_user(self, user_id: UUID) -> None:
        stmt = update(InstructorAssignmentModel).where(InstructorAssignmentModel.user_id == str(user_id), InstructorAssignmentModel.is_active == True).values(is_active=False)
        await self.session.execute(stmt)
        await self.session.commit()

    async def find_active_by_user(self, user_id: UUID) -> Optional[InstructorAssignment]:
        stmt = select(InstructorAssignmentModel).where(InstructorAssignmentModel.user_id == str(user_id), InstructorAssignmentModel.is_active == True)
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        if not m:
            return None
        return InstructorAssignment(id=UUID(m.id), user_id=UUID(m.user_id), instructor_id=UUID(m.instructor_id), started_at=m.started_at, ended_at=m.ended_at, is_active=m.is_active)

    async def exists_active_pair(self, instructor_id: UUID, client_user_id: UUID) -> bool:
        stmt = select(InstructorAssignmentModel.id).where(InstructorAssignmentModel.instructor_id == str(instructor_id), InstructorAssignmentModel.user_id == str(client_user_id), InstructorAssignmentModel.is_active == True).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_active_by_instructor(self, instructor_id: UUID) -> int:
        stmt = select(func.count()).select_from(InstructorAssignmentModel).where(InstructorAssignmentModel.instructor_id == str(instructor_id), InstructorAssignmentModel.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

class SQLAlchemyInstructorRatingRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, rating: InstructorRating) -> InstructorRating:
        model = InstructorRatingModel(id=str(rating.id), user_id=str(rating.user_id), instructor_id=str(rating.instructor_id), rating=rating.rating, created_at=rating.created_at, comment=rating.comment)
        self.session.add(model)
        await self.session.commit()
        return rating

    async def get_average_rating(self, instructor_id: UUID) -> Optional[float]:
        stmt = select(func.avg(InstructorRatingModel.rating)).where(InstructorRatingModel.instructor_id == str(instructor_id))
        result = await self.session.execute(stmt)
        avg = result.scalar()
        if avg is None:
            return None
        return round(float(avg), 2)
