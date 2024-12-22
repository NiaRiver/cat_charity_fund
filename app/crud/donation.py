from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func

from app.crud.base import CharityDonationCRUDBase
from app.models import Donation, CharityProject


class CRUDDonation(CharityDonationCRUDBase):
    async def get_own_donations(
        self,
        user_id: int,
        session: AsyncSession,
    ):
        donations = await session.scalars(
            select(self.model).where(self.model.user_id == user_id)
        )
        return donations.all()

    async def get_new_fullfilled_projects(
        self,
        new_full_amount: int,
        session: AsyncSession,
    ):
        total_donations = await self.get_total_full_amount(session)
        subquery = (
            select(
                CharityProject,
                func.sum(CharityProject.full_amount + new_full_amount)
                .over(order_by=CharityProject.id)
                .label("cumulative_sum"),
            ).subquery()
        )
        last_full_charity = await session.scalars(
            select(CharityProject).join(
                subquery, CharityProject.id == subquery.c.id
            ).where(
                subquery.c.cumulative_sum <= total_donations,
                subquery.c.fully_invested is False or
                subquery.c.fully_invested == 0
            ).order_by(subquery.c.id.desc())
        )
        return last_full_charity.all()


dontions_crud = CRUDDonation(Donation)
