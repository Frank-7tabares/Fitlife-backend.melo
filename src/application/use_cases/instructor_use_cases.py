from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Optional
from ...domain.entities.instructor import Instructor, InstructorAssignment, InstructorRating
from ...infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository, SQLAlchemyInstructorAssignmentRepository, SQLAlchemyInstructorRatingRepository
from ..dtos.instructor_dtos import InstructorResponse, AssignInstructorRequest, RateInstructorRequest

class InstructorUseCases:

    def __init__(self, instructor_repo: SQLAlchemyInstructorRepository, assignment_repo: SQLAlchemyInstructorAssignmentRepository, rating_repo: SQLAlchemyInstructorRatingRepository):
        self.instructor_repo = instructor_repo
        self.assignment_repo = assignment_repo
        self.rating_repo = rating_repo

    async def create_instructor(self, name: str, certifications: List[str], specializations: str='', certificate_url: Optional[str]=None) -> InstructorResponse:
        specs = ', '.join((s.strip().upper() for s in (specializations or '').split(',') if s.strip()))
        certs = [c.strip().upper() for c in certifications or [] if c and str(c).strip()]
        instructor = Instructor(id=uuid4(), name=name, certifications=certs, specializations=specs, rating_avg=0.0, active_users_count=0, certificate_url=certificate_url, certificate_status='pending')
        await self.instructor_repo.save(instructor)
        count = await self.assignment_repo.count_active_by_instructor(instructor.id)
        return InstructorResponse(id=instructor.id, name=instructor.name, certifications=instructor.certifications, specializations=instructor.specializations, rating_avg=instructor.rating_avg, active_users_count=count, certificate_url=instructor.certificate_url, certificate_status=instructor.certificate_status)

    async def list_instructors(self, *, verified_only: bool=True) -> List[InstructorResponse]:
        models = await self.instructor_repo.find_all()
        result = []
        for m in models:
            st = getattr(m, 'certificate_status', None) or 'pending'
            if verified_only and st != 'verified':
                continue
            count = await self.assignment_repo.count_active_by_instructor(UUID(m.id))
            result.append(InstructorResponse(id=UUID(m.id), name=m.name, certifications=m.certifications or [], specializations=m.specializations or '', rating_avg=float(m.rating_avg), active_users_count=count, certificate_url=getattr(m, 'certificate_url', None), certificate_status=st))
        return result

    async def get_instructor_by_id(self, instructor_id: UUID) -> Optional[InstructorResponse]:
        m = await self.instructor_repo.find_by_id(instructor_id)
        if not m:
            return None
        count = await self.assignment_repo.count_active_by_instructor(instructor_id)
        st = getattr(m, 'certificate_status', None) or 'pending'
        return InstructorResponse(id=UUID(m.id), name=m.name, certifications=m.certifications or [], specializations=m.specializations or '', rating_avg=float(m.rating_avg), active_users_count=count, certificate_url=getattr(m, 'certificate_url', None), certificate_status=st)

    async def assign_instructor(self, user_id: UUID, request: AssignInstructorRequest) -> None:
        instructor = await self.instructor_repo.find_by_id(request.instructor_id)
        if not instructor:
            raise ValueError('Instructor not found')
        st = getattr(instructor, 'certificate_status', None) or 'pending'
        if st != 'verified':
            raise ValueError('Instructor must be verified before assignment')
        await self.assignment_repo.deactivate_active_for_user(user_id)
        assignment = InstructorAssignment(id=uuid4(), user_id=user_id, instructor_id=request.instructor_id, started_at=datetime.utcnow(), ended_at=None, is_active=True)
        await self.assignment_repo.save(assignment)

    async def rate_instructor(self, user_id: UUID, instructor_id: UUID, request: RateInstructorRequest) -> None:
        instructor = await self.instructor_repo.find_by_id(instructor_id)
        if not instructor:
            raise ValueError('Instructor not found')
        rating = InstructorRating(id=uuid4(), user_id=user_id, instructor_id=instructor_id, rating=request.rating, created_at=datetime.utcnow(), comment=request.comment)
        await self.rating_repo.save(rating)
        new_avg = await self.rating_repo.get_average_rating(instructor_id)
        if new_avg is not None:
            await self.instructor_repo.update_rating_avg(instructor_id, new_avg)

    async def verify_certificate(self, instructor_id: UUID, status: str) -> None:
        if status not in ('verified', 'rejected'):
            raise ValueError("status must be 'verified' or 'rejected'")
        await self.instructor_repo.update_certificate_status(instructor_id, status)
