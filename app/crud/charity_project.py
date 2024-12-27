
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_charity_project_by_name(
        self,
        project_name: str,
        session: AsyncSession
    ):
        return await session.scalars(
            select(self.model).where(
                self.model.name == project_name
            )
        )


charity_projects_crud = CRUDCharityProject(CharityProject)
