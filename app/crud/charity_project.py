
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CharityDonationCRUDBase
from app.models import CharityProject


class CRUDCharityProject(CharityDonationCRUDBase):
    async def get_charity_project_by_name(
        self,
        project_name: str,
        session: AsyncSession
    ):
        query = await session.scalars(
            select(
                self.model
            ).where(self.model.name == project_name)
        )
        return query.first()


charity_projects_crud = CRUDCharityProject(CharityProject)
