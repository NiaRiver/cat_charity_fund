
from datetime import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    async def create(
        self,
        obj_in, *,
        to_commit: bool = True,
        session: AsyncSession
    ):
        obj_in_data = obj_in.dict()
        obj_in_data["create_date"] = dt.now()
        db_obj = self.model(**obj_in_data)
        if to_commit:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def get_open_projects(
        self,
        session: AsyncSession
    ):
        db_obj_list = await session.scalars(select(
            self.model
        ).where(self.model.full_amount > self.model.invested_amount)
        )
        return db_obj_list.all()

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
