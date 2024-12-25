from datetime import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    async def create(
        self,
        obj_in,
        user: User, *,
        to_commit: bool = True,
        session: AsyncSession
    ):
        obj_in_data = obj_in.dict()
        obj_in_data["create_date"] = dt.now()
        obj_in_data["user_id"] = user.id
        db_obj = self.model(**obj_in_data)
        if to_commit:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def get_open_donations(
        self,
        session: AsyncSession
    ):
        db_obj_list = await session.scalars(select(
            self.model
        ).where(self.model.full_amount > self.model.invested_amount)
        )
        return db_obj_list.all()

    async def get_own_donations(
        self,
        user_id: int,
        session: AsyncSession,
    ):
        donations = await session.scalars(
            select(self.model).where(self.model.user_id == user_id)
        )
        return donations.all()


dontions_crud = CRUDDonation(Donation)
